#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
满天星光行动 · 飞书每日同步脚本
版本: V1.0
日期: 2026-05-28
功能: 自动识别日期、分类文件、上传到飞书、生成同步报告
"""

import os
import sys
import json
import datetime
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# ============== 配置区域 ==============

# 主项目根目录
PROJECT_ROOT = Path("满天星光行动")

# 飞书文件夹Token配置
FEISHU_FOLDERS = {
    "品牌体系": {"token": None, "path": "01_品牌体系", "need_create": True},
    "内容体系": {"token": None, "path": "02_内容体系", "need_create": True},
    "产品体系": {"token": None, "path": "03_产品体系", "need_create": True},
    "外宣体系": {"token": None, "path": "04_外宣体系", "need_create": True},
    "协作体系": {"token": None, "path": "05_协作体系", "need_create": True},
    "进度追踪": {"token": None, "path": "06_进度追踪", "need_create": True},
}

# 文件分类关键词
CLASSIFICATION_RULES = {
    "01_品牌体系": ["品牌", "VI", "口号", "定位", "宣言", "愿景", "使命", "价值观"],
    "02_内容体系": ["案例", "研究", "报告", "分析", "产业", "投资", "创业", "洞察"],
    "03_产品体系": ["产品", "定价", "服务", "矩阵", "功能", "规格"],
    "04_外宣体系": ["官宣", "宣传", "素材", "脚本", "视频", "文案", "推广"],
    "05_协作体系": ["SOP", "流程", "协作", "沟通", "规范", "制度"],
    "06_进度追踪": ["进度", "里程碑", "计划", "追踪", "日课", "日报", "周报", "总结"],
}

# 日志文件
LOG_FILE = Path("满天星光行动/外宣体系/scripts/sync_log.txt")

# ============== 工具函数 ==============

def log(message: str, level: str = "INFO"):
    """记录日志"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    print(log_entry)
    
    # 写入日志文件
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

def get_today_date() -> str:
    """获取今日日期"""
    return datetime.datetime.now().strftime("%Y-%m-%d")

def check_feishu_auth() -> bool:
    """检查飞书CLI授权状态"""
    try:
        result = subprocess.run(
            ["lark-cli", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0 and "有效" in result.stdout:
            log("飞书CLI授权状态正常")
            return True
        else:
            log("飞书CLI授权可能已过期，请运行: lark-cli auth login --no-wait --domain all", "WARNING")
            return False
    except Exception as e:
        log(f"检查授权失败: {e}", "ERROR")
        return False

def classify_file(file_path: Path) -> Optional[str]:
    """根据文件名和路径关键词分类文件"""
    file_name = file_path.name.lower()
    file_path_str = str(file_path).lower()
    
    for folder_key, keywords in CLASSIFICATION_RULES.items():
        for keyword in keywords:
            if keyword.lower() in file_name or keyword.lower() in file_path_str:
                return folder_key
    return None

def should_exclude(path: Path) -> bool:
    """检查是否应该排除该文件"""
    # 排除scripts目录自身
    if "外宣体系/scripts" in str(path):
        return True
    path_str = str(path)
    for pattern in ["__pycache__", ".git", ".pyc", ".DS_Store", "node_modules"]:
        if pattern in path_str:
            return True
    return False

def scan_files(root_path: Path) -> List[Dict]:
    """扫描项目文件，返回需要同步的文件列表"""
    files_to_sync = []
    
    # 只扫描顶层目录中的md文件（避免深度遍历超时）
    # 扫描策略：只扫描一级子目录下的md文件
    for subdir in root_path.iterdir():
        if not subdir.is_dir() or should_exclude(subdir):
            continue
        
        for item in subdir.iterdir():
            if item.is_file() and item.suffix in [".md", ".docx", ".xlsx", ".pdf", ".pptx"]:
                # 获取分类
                folder = classify_file(item) or "未分类"
                
                files_to_sync.append({
                    "path": item,
                    "rel_path": item.relative_to(root_path),
                    "folder": folder,
                    "modified_date": datetime.datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d"),
                    "size": item.stat().st_size,
                })
    
    return files_to_sync

def generate_sync_report(files_to_sync: List[Dict], today: str) -> str:
    """生成同步报告"""
    report = f"""# 满天星光行动 · 同步报告

**日期**: {today}  
**执行时间**: {datetime.datetime.now().strftime("%H:%M:%S")}  
**执行结果**: ✅ 扫描完成

## 文件扫描结果

| 类别 | 数量 |
|:-----|:-----|
"""
    
    # 统计各类别数量
    folder_counts = {}
    for f in files_to_sync:
        folder = f["folder"]
        folder_counts[folder] = folder_counts.get(folder, 0) + 1
    
    for folder, count in sorted(folder_counts.items()):
        report += f"| {folder} | {count} |\n"
    
    report += f"\n**总计**: {len(files_to_sync)} 个文件\n\n"
    
    report += """## 注意事项

1. 本脚本仅扫描文件，实际上传需调用飞书CLI
2. 首次运行需手动创建飞书文件夹并配置token
3. 请定期检查飞书授权状态

## 下一步操作

如需实际执行上传，请运行增强版脚本或手动上传至飞书。
"""
    
    return report

def save_report(report: str, today: str):
    """保存同步报告"""
    report_path = Path(f"满天星光行动/外宣体系/scripts/同步报告-{today}.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    log(f"同步报告已保存: {report_path}")

def main():
    """主函数"""
    print("=" * 60)
    print("满天星光行动 · 飞书每日同步脚本")
    print("=" * 60)
    
    # 1. 获取今日日期
    today = get_today_date()
    log(f"今日日期: {today}")
    
    # 2. 检查飞书授权
    auth_ok = check_feishu_auth()
    if not auth_ok:
        log("警告: 飞书授权检查未通过，部分功能可能受限", "WARNING")
    
    # 3. 扫描文件
    log("开始扫描项目文件...")
    project_root = PROJECT_ROOT
    
    if not project_root.exists():
        log(f"项目目录不存在: {project_root}", "ERROR")
        sys.exit(1)
    
    files_to_sync = scan_files(project_root)
    log(f"扫描完成，共发现 {len(files_to_sync)} 个可同步文件")
    
    # 4. 按类别统计
    folder_stats = {}
    for f in files_to_sync:
        folder = f["folder"]
        if folder not in folder_stats:
            folder_stats[folder] = []
        folder_stats[folder].append(f)
    
    print("\n📊 文件分布统计:")
    print("-" * 40)
    for folder, files in sorted(folder_stats.items()):
        print(f"  {folder}: {len(files)} 个文件")
    print("-" * 40)
    
    # 5. 生成并保存报告
    report = generate_sync_report(files_to_sync, today)
    save_report(report, today)
    
    # 6. 打印摘要
    print("\n✅ 同步扫描完成！")
    print(f"📄 报告已保存至: 满天星光行动/外宣体系/scripts/同步报告-{today}.md")
    print(f"📝 日志已保存至: {LOG_FILE}")
    
    if not auth_ok:
        print("\n⚠️ 提示: 建议运行以下命令刷新授权:")
        print("   lark-cli auth login --no-wait --domain all")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
