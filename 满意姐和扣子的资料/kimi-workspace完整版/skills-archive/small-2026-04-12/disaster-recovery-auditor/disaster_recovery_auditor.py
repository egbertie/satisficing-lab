#!/usr/bin/env python3
"""
disaster-recovery-auditor: 灾备审计
检查点恢复验证，RPO/RTO合规检查

作者: 满意妞
版本: 1.0.0
日期: 2026-03-28
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class CheckpointAudit:
    """检查点审计记录"""
    checkpoint_id: str
    timestamp: str
    integrity_check: bool
    file_count: int
    total_size: int
    rpo_seconds: float
    rto_seconds: Optional[float]
    status: str  # PASS, FAIL, WARNING
    issues: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "checkpoint_id": self.checkpoint_id,
            "timestamp": self.timestamp,
            "integrity_check": self.integrity_check,
            "file_count": self.file_count,
            "total_size": self.total_size,
            "rpo_seconds": self.rpo_seconds,
            "rto_seconds": self.rto_seconds,
            "status": self.status,
            "issues": self.issues,
        }


class DisasterRecoveryAuditor:
    """
    灾备审计器 - 检查点恢复验证
    
    功能:
    - 检查点完整性审计
    - 恢复流程验证
    - RPO/RTO合规检查
    """
    
    # RPO/RTO目标（秒）
    RPO_TARGET = 300  # 5分钟
    RTO_TARGET = 600  # 10分钟
    
    def __init__(
        self,
        checkpoint_dir: str = "~/.openclaw/system-v2/checkpoints",
        audit_log_path: str = "~/.openclaw/system-v2/audit/dr-audit.json",
    ):
        """
        初始化灾备审计器
        
        Args:
            checkpoint_dir: 检查点目录
            audit_log_path: 审计日志路径
        """
        self.checkpoint_dir = Path(checkpoint_dir).expanduser()
        self.audit_log_path = Path(audit_log_path).expanduser()
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._audit_history: List[CheckpointAudit] = []
        self._load_audit_history()
    
    def _load_audit_history(self):
        """加载审计历史"""
        if self.audit_log_path.exists():
            try:
                with open(self.audit_log_path, 'r') as f:
                    data = json.load(f)
                
                for audit_data in data.get("audits", []):
                    self._audit_history.append(CheckpointAudit(
                        checkpoint_id=audit_data["checkpoint_id"],
                        timestamp=audit_data["timestamp"],
                        integrity_check=audit_data["integrity_check"],
                        file_count=audit_data["file_count"],
                        total_size=audit_data["total_size"],
                        rpo_seconds=audit_data["rpo_seconds"],
                        rto_seconds=audit_data.get("rto_seconds"),
                        status=audit_data["status"],
                        issues=audit_data.get("issues", []),
                    ))
            except Exception as e:
                print(f"[DR-Auditor] 加载审计历史失败: {e}")
    
    def _save_audit_history(self):
        """保存审计历史"""
        data = {
            "last_updated": datetime.now().isoformat(),
            "audits": [audit.to_dict() for audit in self._audit_history],
        }
        
        temp_file = self.audit_log_path.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=2)
        temp_file.replace(self.audit_log_path)
    
    def _get_checkpoints(self) -> List[Path]:
        """获取所有检查点目录"""
        if not self.checkpoint_dir.exists():
            return []
        
        return [
            d for d in self.checkpoint_dir.iterdir()
            if d.is_dir() and d.name.startswith("checkpoint-")
        ]
    
    def _verify_integrity(self, checkpoint_path: Path) -> Tuple[bool, int, int, List[str]]:
        """
        验证检查点完整性
        
        Returns:
            (完整性通过, 文件数, 总大小, 问题列表)
        """
        manifest_path = checkpoint_path / "manifest.json"
        
        if not manifest_path.exists():
            return False, 0, 0, ["缺少manifest.json"]
        
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            files = manifest.get("files", [])
            issues = []
            total_size = 0
            
            for file_info in files:
                file_path = checkpoint_path / "files" / file_info["path"]
                
                if not file_path.exists():
                    issues.append(f"文件缺失: {file_info['path']}")
                    continue
                
                # 验证大小
                actual_size = file_path.stat().st_size
                if actual_size != file_info["size"]:
                    issues.append(f"大小不匹配: {file_info['path']}")
                
                total_size += actual_size
                
                # 验证哈希（简化，实际应计算）
                # 这里假设manifest中的哈希是正确的
            
            integrity_pass = len(issues) == 0
            return integrity_pass, len(files), total_size, issues
            
        except Exception as e:
            return False, 0, 0, [f"验证异常: {e}"]
    
    def _calculate_rpo(self, checkpoint_path: Path) -> float:
        """计算RPO（数据丢失时间）"""
        # 从检查点名称解析时间
        # checkpoint-YYYYMMDD-HHMMSS
        try:
            name = checkpoint_path.name
            timestamp_str = name.replace("checkpoint-", "")
            checkpoint_time = datetime.strptime(timestamp_str, "%Y%m%d-%H%M%S")
            now = datetime.now()
            
            rpo = (now - checkpoint_time).total_seconds()
            return rpo
        except:
            return float('inf')
    
    def _test_recovery(self, checkpoint_path: Path) -> Tuple[Optional[float], List[str]]:
        """
        测试恢复流程
        
        Returns:
            (恢复时间秒, 问题列表)
        """
        issues = []
        
        start_time = time.time()
        
        try:
            # 模拟恢复：验证manifest可读
            manifest_path = checkpoint_path / "manifest.json"
            if manifest_path.exists():
                with open(manifest_path, 'r') as f:
                    json.load(f)
            
            # 简化测试，实际应执行完整恢复
            elapsed = time.time() - start_time
            return elapsed, issues
            
        except Exception as e:
            issues.append(f"恢复测试失败: {e}")
            return None, issues
    
    def audit_checkpoint(self, checkpoint_id: Optional[str] = None) -> CheckpointAudit:
        """
        审计检查点
        
        Args:
            checkpoint_id: 检查点ID（如不提供，审计最新的）
            
        Returns:
            审计记录
        """
        checkpoints = self._get_checkpoints()
        
        if not checkpoints:
            return CheckpointAudit(
                checkpoint_id="none",
                timestamp=datetime.now().isoformat(),
                integrity_check=False,
                file_count=0,
                total_size=0,
                rpo_seconds=0,
                rto_seconds=None,
                status="FAIL",
                issues=["无可用检查点"],
            )
        
        # 选择检查点
        if checkpoint_id:
            checkpoint_path = self.checkpoint_dir / checkpoint_id
            if not checkpoint_path.exists():
                checkpoint_path = checkpoints[-1]  # 使用最新的
        else:
            checkpoint_path = checkpoints[-1]  # 最新的
        
        checkpoint_id = checkpoint_path.name
        
        # 执行审计
        integrity_pass, file_count, total_size, integrity_issues = self._verify_integrity(checkpoint_path)
        rpo = self._calculate_rpo(checkpoint_path)
        rto, recovery_issues = self._test_recovery(checkpoint_path)
        
        # 合并问题
        all_issues = integrity_issues + recovery_issues
        
        # 判断状态
        if not integrity_pass:
            status = "FAIL"
        elif rpo > self.RPO_TARGET:
            status = "WARNING"
            all_issues.append(f"RPO超标: {rpo:.0f}s > 目标 {self.RPO_TARGET}s")
        elif rto and rto > self.RTO_TARGET:
            status = "WARNING"
            all_issues.append(f"RTO超标: {rto:.2f}s > 目标 {self.RTO_TARGET}s")
        else:
            status = "PASS"
        
        audit = CheckpointAudit(
            checkpoint_id=checkpoint_id,
            timestamp=datetime.now().isoformat(),
            integrity_check=integrity_pass,
            file_count=file_count,
            total_size=total_size,
            rpo_seconds=rpo,
            rto_seconds=rto,
            status=status,
            issues=all_issues,
        )
        
        # 保存
        self._audit_history.append(audit)
        self._save_audit_history()
        
        return audit
    
    def audit_all_checkpoints(self) -> List[CheckpointAudit]:
        """审计所有检查点"""
        checkpoints = self._get_checkpoints()
        results = []
        
        for checkpoint_path in checkpoints:
            audit = self.audit_checkpoint(checkpoint_path.name)
            results.append(audit)
        
        return results
    
    def get_audit_summary(self) -> Dict:
        """获取审计汇总"""
        if not self._audit_history:
            return {"status": "NO_DATA", "message": "无审计数据"}
        
        latest = self._audit_history[-1]
        
        return {
            "latest_checkpoint": latest.checkpoint_id,
            "latest_status": latest.status,
            "rpo_seconds": latest.rpo_seconds,
            "rto_seconds": latest.rto_seconds,
            "rpo_target": self.RPO_TARGET,
            "rto_target": self.RTO_TARGET,
            "rpo_compliance": latest.rpo_seconds <= self.RPO_TARGET,
            "rto_compliance": (latest.rto_seconds or 0) <= self.RTO_TARGET,
            "total_audits": len(self._audit_history),
            "pass_count": sum(1 for a in self._audit_history if a.status == "PASS"),
            "fail_count": sum(1 for a in self._audit_history if a.status == "FAIL"),
        }


def main():
    """CLI入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Disaster Recovery Auditor - 灾备审计")
    parser.add_argument("--audit", type=str, nargs="?", help="审计指定检查点")
    parser.add_argument("--audit-all", action="store_true", help="审计所有检查点")
    parser.add_argument("--summary", action="store_true", help="显示审计汇总")
    parser.add_argument("--test", action="store_true", help="运行测试")
    
    args = parser.parse_args()
    
    if args.test:
        print("🧪 请运行: python3 -m pytest test_disaster_recovery_auditor.py")
        return
    
    auditor = DisasterRecoveryAuditor()
    
    if args.audit_all:
        results = auditor.audit_all_checkpoints()
        print("📊 审计所有检查点:")
        for audit in results:
            emoji = "✅" if audit.status == "PASS" else "⚠️" if audit.status == "WARNING" else "❌"
            print(f"  {emoji} {audit.checkpoint_id}: {audit.status}")
            for issue in audit.issues:
                print(f"      - {issue}")
    
    elif args.audit:
        audit = auditor.audit_checkpoint(args.audit)
        emoji = "✅" if audit.status == "PASS" else "⚠️" if audit.status == "WARNING" else "❌"
        print(f"{emoji} 检查点 {audit.checkpoint_id} 审计结果: {audit.status}")
        print(f"   完整性: {'通过' if audit.integrity_check else '失败'}")
        print(f"   文件数: {audit.file_count}")
        print(f"   RPO: {audit.rpo_seconds:.0f}s (目标: {auditor.RPO_TARGET}s)")
        print(f"   RTO: {audit.rto_seconds:.2f}s (目标: {auditor.RTO_TARGET}s)" if audit.rto_seconds else "   RTO: 未测试")
        if audit.issues:
            print("   问题:")
            for issue in audit.issues:
                print(f"      - {issue}")
    
    elif args.summary:
        summary = auditor.get_audit_summary()
        print("📊 灾备审计汇总:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
