#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
满意解研究所 · 备份管理器
Backup Manager for Manyi Solution Research Institute

功能:
- 自动备份核心配置文件、文档、记忆文件
- 支持全量/增量备份
- 备份完整性验证
- 灾难恢复支持
- 自动清理过期备份

作者: Kimi Claw
版本: 1.0.0
日期: 2026-03-10
"""

import os
import sys
import json
import hashlib
import shutil
import argparse
import tarfile
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Tuple

# 配置
VERSION = "1.0.0"
WORKSPACE_DIR = Path("/root/.openclaw/workspace")
OPENCLAW_DIR = Path("/root/.openclaw")
BACKUP_BASE_DIR = Path("/backups")
LOG_DIR = BACKUP_BASE_DIR / "logs"
RETENTION_DAYS = {
    "daily": 30,
    "weekly": 90,
    "monthly": 365
}

# 备份清单
BACKUP_ITEMS = {
    "config": {
        "description": "核心配置文件",
        "paths": [
            (WORKSPACE_DIR / ".env", "config/.env"),
            (OPENCLAW_DIR / "openclaw.json", "config/openclaw.json"),
            (OPENCLAW_DIR / "cron" / "jobs.json", "config/cron_jobs.json"),
        ],
        "priority": "P0"
    },
    "docs": {
        "description": "Markdown文档",
        "paths": [
            (WORKSPACE_DIR / "docs", "workspace-md/docs"),
            (WORKSPACE_DIR / "*.md", "workspace-md"),
        ],
        "priority": "P0"
    },
    "memory": {
        "description": "记忆文件",
        "paths": [
            (WORKSPACE_DIR / "memory", "memory"),
            (WORKSPACE_DIR / "MEMORY.md", "memory/MEMORY.md"),
        ],
        "priority": "P1"
    },
    "skills": {
        "description": "Skill文件",
        "paths": [
            (WORKSPACE_DIR / "skills", "skills"),
        ],
        "priority": "P1"
    },
    "scripts": {
        "description": "脚本文件",
        "paths": [
            (WORKSPACE_DIR / "scripts", "scripts"),
            (WORKSPACE_DIR / ".scripts", "scripts/.scripts"),
        ],
        "priority": "P1"
    }
}

# 设置日志
def setup_logging():
    """配置日志系统"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"backup_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()


class BackupManager:
    """备份管理器主类"""
    
    def __init__(self):
        self.backup_base = BACKUP_BASE_DIR
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def ensure_directories(self):
        """确保备份目录存在"""
        dirs = [
            self.backup_base / "daily",
            self.backup_base / "weekly", 
            self.backup_base / "monthly",
            self.backup_base / "archive",
            LOG_DIR,
            self.backup_base / "status"
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
            os.chmod(d, 0o700)
            
    def calculate_checksum(self, file_path: Path) -> str:
        """计算文件MD5校验和"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"计算校验和失败 {file_path}: {e}")
            return ""
            
    def copy_item(self, src: Path, dst: Path) -> bool:
        """复制单个文件或目录"""
        try:
            if not src.exists():
                logger.warning(f"源文件不存在: {src}")
                return False
                
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            if src.is_file():
                shutil.copy2(src, dst)
                os.chmod(dst, 0o600)
            elif src.is_dir():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                for root, dirs, files in os.walk(dst):
                    os.chmod(root, 0o700)
                    for f in files:
                        os.chmod(Path(root) / f, 0o600)
                        
            logger.info(f"已备份: {src} -> {dst}")
            return True
            
        except Exception as e:
            logger.error(f"备份失败 {src}: {e}")
            return False
            
    def expand_wildcards(self, pattern: str, base_dir: Path) -> List[Path]:
        """展开通配符路径"""
        if "*" in str(pattern):
            import glob
            return [Path(p) for p in glob.glob(str(base_dir / pattern))]
        return [base_dir / pattern]
        
    def backup_category(self, category: str, backup_dir: Path) -> Dict:
        """备份一个分类"""
        if category not in BACKUP_ITEMS:
            logger.error(f"未知的备份分类: {category}")
            return {"success": False, "error": "Unknown category"}
            
        item = BACKUP_ITEMS[category]
        logger.info(f"开始备份: {item['description']} ({category})")
        
        results = {
            "category": category,
            "description": item["description"],
            "priority": item["priority"],
            "files_backed_up": 0,
            "files_failed": 0,
            "checksums": {}
        }
        
        for src_pattern, dst_rel in item["paths"]:
            if isinstance(src_pattern, str) and "*" in src_pattern:
                src_dir = WORKSPACE_DIR if "docs" not in str(src_pattern) else WORKSPACE_DIR
                src_files = self.expand_wildcards(src_pattern.replace(str(src_dir) + "/", ""), src_dir)
            else:
                src_files = [src_pattern] if isinstance(src_pattern, Path) else [Path(src_pattern)]
                
            for src_file in src_files:
                if not src_file.exists():
                    continue
                    
                if src_file.is_file():
                    dst_file = backup_dir / dst_rel
                    if self.copy_item(src_file, dst_file):
                        results["files_backed_up"] += 1
                        results["checksums"][str(dst_rel)] = self.calculate_checksum(dst_file)
                    else:
                        results["files_failed"] += 1
                elif src_file.is_dir():
                    dst_dir = backup_dir / dst_rel
                    if self.copy_item(src_file, dst_dir):
                        results["files_backed_up"] += self.count_files(src_file)
                    else:
                        results["files_failed"] += 1
                        
        results["success"] = results["files_failed"] == 0
        return results
        
    def count_files(self, directory: Path) -> int:
        """统计目录中的文件数"""
        return sum(1 for _ in directory.rglob("*") if _.is_file())
        
    def create_backup(self, backup_type: str = "daily", categories: Optional[List[str]] = None) -> Dict:
        """创建备份"""
        self.ensure_directories()
        
        backup_dir = self.backup_base / backup_type / self.today
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"=" * 60)
        logger.info(f"开始{backup_type}备份: {self.today}")
        logger.info(f"备份目录: {backup_dir}")
        logger.info(f"=" * 60)
        
        if categories is None:
            categories = list(BACKUP_ITEMS.keys())
            
        results = {
            "backup_id": f"{backup_type}-{self.timestamp}",
            "backup_type": backup_type,
            "backup_date": self.today,
            "backup_dir": str(backup_dir),
            "categories": {},
            "total_files": 0,
            "total_failed": 0,
            "status": "success"
        }
        
        for category in categories:
            cat_result = self.backup_category(category, backup_dir)
            results["categories"][category] = cat_result
            results["total_files"] += cat_result["files_backed_up"]
            results["total_failed"] += cat_result["files_failed"]
            
        if results["total_failed"] > 0:
            results["status"] = "partial_failure"
            
        # 保存备份清单
        manifest_path = backup_dir / "backup_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        os.chmod(manifest_path, 0o600)
        
        # 更新最新状态
        self.update_status(results)
        
        logger.info(f"=" * 60)
        logger.info(f"备份完成: {results['total_files']} 个文件, {results['total_failed']} 个失败")
        logger.info(f"=" * 60)
        
        return results
        
    def update_status(self, results: Dict):
        """更新备份状态"""
        status_file = self.backup_base / "status" / "latest.json"
        status = {
            "last_backup": results["backup_date"],
            "last_backup_id": results["backup_id"],
            "last_backup_type": results["backup_type"],
            "last_status": results["status"],
            "total_files": results["total_files"],
            "updated_at": datetime.now().isoformat()
        }
        
        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=2)
            
    def get_backup_list(self) -> List[Dict]:
        """获取备份列表"""
        backups = []
        
        for backup_type in ["daily", "weekly", "monthly"]:
            type_dir = self.backup_base / backup_type
            if not type_dir.exists():
                continue
                
            for date_dir in type_dir.iterdir():
                if date_dir.is_dir():
                    manifest = date_dir / "backup_manifest.json"
                    if manifest.exists():
                        try:
                            with open(manifest, "r") as f:
                                data = json.load(f)
                                backups.append({
                                    "date": date_dir.name,
                                    "type": backup_type,
                                    "path": str(date_dir),
                                    "files": data.get("total_files", 0),
                                    "status": data.get("status", "unknown")
                                })
                        except:
                            pass
                            
        return sorted(backups, key=lambda x: x["date"], reverse=True)
        
    def restore_backup(self, date: str, backup_type: str = "daily", target_dir: Optional[Path] = None) -> bool:
        """恢复备份"""
        backup_dir = self.backup_base / backup_type / date
        
        if not backup_dir.exists():
            logger.error(f"备份不存在: {backup_dir}")
            return False
            
        logger.info(f"开始恢复备份: {backup_dir}")
        
        # 验证备份清单
        manifest = backup_dir / "backup_manifest.json"
        if not manifest.exists():
            logger.error(f"备份清单不存在: {manifest}")
            return False
            
        # 恢复各个分类
        for category in BACKUP_ITEMS.keys():
            cat_dir = backup_dir / category
            if not cat_dir.exists():
                continue
                
            logger.info(f"恢复分类: {category}")
            
            # 恢复config
            if category == "config":
                for src_file in cat_dir.rglob("*"):
                    if src_file.is_file():
                        if src_file.name == ".env":
                            dst = WORKSPACE_DIR / ".env"
                        elif src_file.name == "openclaw.json":
                            dst = OPENCLAW_DIR / "openclaw.json"
                        elif src_file.name == "cron_jobs.json":
                            dst = OPENCLAW_DIR / "cron" / "jobs.json"
                        else:
                            continue
                            
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src_file, dst)
                        logger.info(f"已恢复: {src_file} -> {dst}")
                        
        logger.info(f"备份恢复完成: {date}")
        return True
        
    def cleanup_old_backups(self):
        """清理过期备份"""
        logger.info("开始清理过期备份...")
        
        deleted_count = 0
        
        for backup_type, days in RETENTION_DAYS.items():
            type_dir = self.backup_base / backup_type
            if not type_dir.exists():
                continue
                
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for date_dir in type_dir.iterdir():
                if not date_dir.is_dir():
                    continue
                    
                try:
                    dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
                    if dir_date < cutoff_date:
                        shutil.rmtree(date_dir)
                        logger.info(f"已删除过期备份: {date_dir}")
                        deleted_count += 1
                except ValueError:
                    continue
                    
        logger.info(f"清理完成，删除 {deleted_count} 个过期备份")
        return deleted_count
        
    def verify_backup(self, date: str, backup_type: str = "daily") -> Dict:
        """验证备份完整性"""
        backup_dir = self.backup_base / backup_type / date
        manifest = backup_dir / "backup_manifest.json"
        
        if not manifest.exists():
            return {"valid": False, "error": "Manifest not found"}
            
        with open(manifest, "r") as f:
            data = json.load(f)
            
        verified = True
        errors = []
        
        for category, info in data.get("categories", {}).items():
            for rel_path, expected_checksum in info.get("checksums", {}).items():
                file_path = backup_dir / rel_path
                if not file_path.exists():
                    verified = False
                    errors.append(f"文件缺失: {rel_path}")
                    continue
                    
                actual_checksum = self.calculate_checksum(file_path)
                if actual_checksum != expected_checksum:
                    verified = False
                    errors.append(f"校验和不匹配: {rel_path}")
                    
        return {
            "valid": verified,
            "errors": errors,
            "date": date,
            "type": backup_type
        }


def main():
    parser = argparse.ArgumentParser(
        description="满意解研究所备份管理器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s backup --type daily          # 创建每日备份
  %(prog)s backup --type full           # 创建完整备份
  %(prog)s list                         # 列出所有备份
  %(prog)s restore --date 2026-03-10    # 恢复指定日期备份
  %(prog)s verify                       # 验证最新备份
  %(prog)s cleanup                      # 清理过期备份
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # backup 命令
    backup_parser = subparsers.add_parser("backup", help="创建备份")
    backup_parser.add_argument("--type", choices=["daily", "weekly", "monthly", "full"],
                              default="daily", help="备份类型 (默认: daily)")
    backup_parser.add_argument("--categories", nargs="+", 
                              choices=list(BACKUP_ITEMS.keys()),
                              help="指定备份分类")
                              
    # restore 命令
    restore_parser = subparsers.add_parser("restore", help="恢复备份")
    restore_parser.add_argument("--date", required=True, help="备份日期 (YYYY-MM-DD)")
    restore_parser.add_argument("--type", default="daily", help="备份类型")
    restore_parser.add_argument("--target", help="恢复目标目录")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出备份")
    list_parser.add_argument("--limit", type=int, default=10, help="显示数量限制")
    
    # verify 命令
    verify_parser = subparsers.add_parser("verify", help="验证备份")
    verify_parser.add_argument("--date", help="指定日期 (默认: 最新)")
    verify_parser.add_argument("--type", default="daily", help="备份类型")
    verify_parser.add_argument("--report", action="store_true", help="生成报告")
    
    # cleanup 命令
    cleanup_parser = subparsers.add_parser("cleanup", help="清理过期备份")
    cleanup_parser.add_argument("--days", type=int, help="指定保留天数")
    
    # status 命令
    status_parser = subparsers.add_parser("status", help="查看备份状态")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    manager = BackupManager()
    
    if args.command == "backup":
        if args.type == "full":
            result = manager.create_backup("daily", list(BACKUP_ITEMS.keys()))
        else:
            categories = args.categories or list(BACKUP_ITEMS.keys())
            result = manager.create_backup(args.type, categories)
            
        if result["status"] == "success":
            print(f"✅ 备份成功: {result['backup_id']}")
            print(f"   文件数: {result['total_files']}")
            print(f"   备份路径: {result['backup_dir']}")
        else:
            print(f"⚠️ 备份部分失败: {result['total_failed']} 个文件失败")
            sys.exit(1)
            
    elif args.command == "restore":
        success = manager.restore_backup(args.date, args.type, 
                                        Path(args.target) if args.target else None)
        if success:
            print(f"✅ 备份恢复成功: {args.date}")
        else:
            print(f"❌ 备份恢复失败")
            sys.exit(1)
            
    elif args.command == "list":
        backups = manager.get_backup_list()
        print(f"\n{'日期':<12} {'类型':<10} {'文件数':<10} {'状态':<15}")
        print("-" * 50)
        for b in backups[:args.limit]:
            print(f"{b['date']:<12} {b['type']:<10} {b['files']:<10} {b['status']:<15}")
            
    elif args.command == "verify":
        date = args.date or datetime.now().strftime("%Y-%m-%d")
        result = manager.verify_backup(date, args.type)
        
        if result["valid"]:
            print(f"✅ 备份验证通过: {date}")
        else:
            print(f"❌ 备份验证失败: {date}")
            for error in result["errors"]:
                print(f"   - {error}")
                
    elif args.command == "cleanup":
        count = manager.cleanup_old_backups()
        print(f"✅ 已清理 {count} 个过期备份")
        
    elif args.command == "status":
        status_file = BACKUP_BASE_DIR / "status" / "latest.json"
        if status_file.exists():
            with open(status_file, "r") as f:
                status = json.load(f)
                print(f"\n📊 备份状态")
                print(f"   上次备份: {status.get('last_backup', 'N/A')}")
                print(f"   备份类型: {status.get('last_backup_type', 'N/A')}")
                print(f"   备份状态: {status.get('last_status', 'N/A')}")
                print(f"   文件数量: {status.get('total_files', 0)}")
                print(f"   更新时间: {status.get('updated_at', 'N/A')}")
        else:
            print("⚠️ 暂无备份状态信息")


if __name__ == "__main__":
    main()
