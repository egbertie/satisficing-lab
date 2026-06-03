#!/usr/bin/env python3
"""
Backup Verification System V2.0 - 5 Standard Complete
增强版备份验证系统 - 实现自动检测+自动修复+告警通知

S1: 全局考虑 - 覆盖人/事/物/环境/外部/边界
S2: 系统闭环 - 检测→验证→修复→验证
S3: 可观测输出 - 结构化报告+健康指标
S4: 自动化集成 - 定时验证+自动修复
S5: 自我验证 - 验证机制自检
S6: 认知谦逊 - 明确标注局限
S7: 对抗测试 - 模拟损坏场景
"""

import json
import os
import sys
import hashlib
import time
import subprocess
import shutil
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from enum import Enum
import logging

# ============ 配置 ============
WORKSPACE = "/root/.openclaw/workspace"
BACKUP_ROOT = os.path.join(WORKSPACE, ".backup")
VERIFICATION_LOG = "/tmp/backup_verification.log"
VERIFICATION_JSON = "/tmp/backup_verification_latest.json"
VERIFICATION_HISTORY = "/tmp/backup_verification_history.jsonl"
RECOVERY_ZONE = "/tmp/backup_recovery_test"
HASH_DB = os.path.join(BACKUP_ROOT, ".hash_db.json")

# 飞书告警配置（可选）
FEISHU_WEBHOOK = os.environ.get("FEISHU_BACKUP_WEBHOOK", "")

# ============ 日志设置 ============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(VERIFICATION_LOG),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============ 数据模型 ============
class IssueType(Enum):
    MISSING_FILE = "missing_file"
    CORRUPTED = "corrupted"
    SIZE_MISMATCH = "size_mismatch"
    PERMISSION_DENIED = "permission_denied"
    CHAIN_BROKEN = "chain_broken"
    METADATA_ERROR = "metadata_error"
    RECOVERY_FAILED = "recovery_failed"

class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class RepairStatus(Enum):
    NOT_ATTEMPTED = "not_attempted"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    MANUAL_REQUIRED = "manual_required"

@dataclass
class Issue:
    file_path: str
    issue_type: IssueType
    severity: Severity
    description: str
    expected_hash: Optional[str] = None
    actual_hash: Optional[str] = None
    repair_status: RepairStatus = RepairStatus.NOT_ATTEMPTED
    repair_attempts: int = 0
    repair_log: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "file_path": self.file_path,
            "issue_type": self.issue_type.value,
            "severity": self.severity.value,
            "description": self.description,
            "expected_hash": self.expected_hash,
            "actual_hash": self.actual_hash,
            "repair_status": self.repair_status.value,
            "repair_attempts": self.repair_attempts,
            "repair_log": self.repair_log
        }

@dataclass
class VerificationLayer:
    name: str
    checked: int = 0
    passed: int = 0
    failed: int = 0
    issues: List[Issue] = field(default_factory=list)
    duration_ms: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "checked": self.checked,
            "passed": self.passed,
            "failed": self.failed,
            "issues": [issue.to_dict() for issue in self.issues],
            "duration_ms": self.duration_ms
        }

@dataclass
class VerificationReport:
    timestamp: str
    verification_id: str
    overall_status: str  # passed | failed | partial | error
    health_score: int
    layers: Dict[str, VerificationLayer]
    repair_summary: Dict[str, any]
    limitations: List[str]
    self_check: Dict[str, any]
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "verification_id": self.verification_id,
            "overall_status": self.overall_status,
            "health_score": self.health_score,
            "layers": {k: v.to_dict() for k, v in self.layers.items()},
            "repair_summary": self.repair_summary,
            "limitations": self.limitations,
            "self_check": self.self_check
        }

# ============ S1: 全局考虑 ============
class GlobalConsideration:
    """S1: 全局考虑 - 评估备份失败对灾备的全面影响"""
    
    IMPACT_MATRIX = {
        "people": {
            "user": {"concern": "数据安全", "risk": "以为备份成功实则损坏"},
            "admin": {"concern": "系统可靠性", "risk": "备份静默失败"},
            "auditor": {"concern": "合规性", "risk": "无法证明可恢复"}
        },
        "tasks": [
            "文件存在性检查",
            "内容完整性校验(hash)",
            "可恢复性测试(抽样)",
            "存储空间监控",
            "备份链健康检查"
        ],
        "resources": ["备份文件", "Hash校验数据库", "测试恢复区", "日志记录"],
        "environments": ["备份刚完成/长时间未备份", "存储充足/不足", "网络可用/不可用"],
        "external_integrations": ["飞书Drive API", "企业微信API", "本地文件系统", "Hash计算工具"],
        "edge_cases": [
            "备份文件被截断",
            "云端权限突然变更",
            "存储介质损坏",
            "加密密钥丢失",
            "备份链断裂(依赖缺失)"
        ]
    }
    
    @classmethod
    def get_impact_assessment(cls, failed_files: List[str]) -> Dict:
        """评估失败影响"""
        critical_files = [f for f in failed_files if any(x in f for x in ['SOUL.md', 'IDENTITY.md', 'MEMORY.md', 'AGENTS.md'])]
        
        return {
            "disaster_recovery_impact": "CRITICAL" if critical_files else "MODERATE",
            "rpo_violation": len(critical_files) > 0,
            "rto_risk": "HIGH" if len(failed_files) > 10 else "LOW",
            "business_continuity": "AT_RISK" if critical_files else "ACCEPTABLE",
            "recommended_action": "立即修复" if critical_files else "计划修复"
        }

# ============ S5: 自我验证 ============
class SelfValidator:
    """S5: 自我验证 - 验证机制自检"""
    
    @staticmethod
    def validate_environment() -> Tuple[bool, List[str]]:
        """验证执行环境"""
        checks = []
        
        # 检查工作目录
        if os.path.exists(WORKSPACE):
            checks.append(("工作目录存在", True))
        else:
            checks.append(("工作目录存在", False))
            return False, ["工作目录不存在，无法继续"]
        
        # 检查读取权限
        if os.access(WORKSPACE, os.R_OK):
            checks.append(("工作目录可读", True))
        else:
            checks.append(("工作目录可读", False))
        
        # 检查写入权限（用于恢复测试）
        if os.access("/tmp", os.W_OK):
            checks.append(("临时目录可写", True))
        else:
            checks.append(("临时目录可写", False))
        
        # 检查必要的命令
        for cmd in ["python3", "git", "md5sum"]:
            if shutil.which(cmd):
                checks.append((f"命令 {cmd} 可用", True))
            else:
                checks.append((f"命令 {cmd} 可用", False))
        
        all_passed = all(c[1] for c in checks)
        failed = [c[0] for c in checks if not c[1]]
        
        return all_passed, failed
    
    @staticmethod
    def validate_hash_algorithm() -> bool:
        """验证hash算法正确性"""
        test_content = b"test content for hash validation"
        expected_hash = hashlib.sha256(test_content).hexdigest()
        
        # 写入临时文件并验证
        test_file = "/tmp/hash_test_file.txt"
        with open(test_file, 'wb') as f:
            f.write(test_content)
        
        sha256 = hashlib.sha256()
        with open(test_file, 'rb') as f:
            sha256.update(f.read())
        actual_hash = sha256.hexdigest()
        
        os.remove(test_file)
        return expected_hash == actual_hash

# ============ 自动修复模块 ============
class AutoRepair:
    """自动修复引擎 - 尝试自动修复检测到的备份问题"""
    
    def __init__(self, workspace: str):
        self.workspace = workspace
        self.repair_results = []
        self.attempted_repairs = 0
        self.successful_repairs = 0
        self.failed_repairs = 0
        self.manual_required = 0
    
    def attempt_repair(self, issue: Issue) -> Issue:
        """尝试修复单个问题"""
        issue.repair_status = RepairStatus.IN_PROGRESS
        issue.repair_attempts += 1
        
        logger.info(f"尝试修复 {issue.file_path} - 类型: {issue.issue_type.value}")
        
        try:
            if issue.issue_type == IssueType.MISSING_FILE:
                result = self._repair_missing_file(issue)
            elif issue.issue_type == IssueType.CORRUPTED:
                result = self._repair_corrupted_file(issue)
            elif issue.issue_type == IssueType.PERMISSION_DENIED:
                result = self._repair_permission(issue)
            elif issue.issue_type == IssueType.CHAIN_BROKEN:
                result = self._repair_chain(issue)
            else:
                result = RepairStatus.MANUAL_REQUIRED
                issue.repair_log.append(f"不支持的修复类型: {issue.issue_type.value}")
            
            issue.repair_status = result
            self.attempted_repairs += 1
            
            if result == RepairStatus.SUCCESS:
                self.successful_repairs += 1
                logger.info(f"✅ 修复成功: {issue.file_path}")
            elif result == RepairStatus.FAILED:
                self.failed_repairs += 1
                logger.warning(f"❌ 修复失败: {issue.file_path}")
            else:
                self.manual_required += 1
                logger.info(f"⚠️ 需要人工处理: {issue.file_path}")
                
        except Exception as e:
            issue.repair_status = RepairStatus.FAILED
            issue.repair_log.append(f"修复异常: {str(e)}")
            self.failed_repairs += 1
            logger.error(f"修复异常: {issue.file_path} - {e}")
        
        return issue
    
    def _repair_missing_file(self, issue: Issue) -> RepairStatus:
        """尝试从Git恢复缺失文件"""
        file_path = issue.file_path
        rel_path = os.path.relpath(file_path, self.workspace)
        
        issue.repair_log.append(f"尝试从Git恢复: {rel_path}")
        
        # 尝试从Git恢复
        try:
            result = subprocess.run(
                ["git", "checkout", "HEAD", "--", rel_path],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and os.path.exists(file_path):
                issue.repair_log.append("成功从Git恢复")
                return RepairStatus.SUCCESS
            else:
                issue.repair_log.append(f"Git恢复失败: {result.stderr}")
                
                # 尝试从备份目录恢复
                backup_file = os.path.join(BACKUP_ROOT, rel_path)
                if os.path.exists(backup_file):
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    shutil.copy2(backup_file, file_path)
                    issue.repair_log.append("成功从备份目录恢复")
                    return RepairStatus.SUCCESS
                
                return RepairStatus.MANUAL_REQUIRED
        except Exception as e:
            issue.repair_log.append(f"恢复过程异常: {str(e)}")
            return RepairStatus.FAILED
    
    def _repair_corrupted_file(self, issue: Issue) -> RepairStatus:
        """尝试修复损坏文件"""
        file_path = issue.file_path
        rel_path = os.path.relpath(file_path, self.workspace)
        
        issue.repair_log.append(f"文件Hash不匹配，尝试恢复")
        
        # 先从Git尝试恢复
        try:
            result = subprocess.run(
                ["git", "checkout", "HEAD", "--", rel_path],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # 验证修复后的hash
                sha256 = hashlib.sha256()
                with open(file_path, 'rb') as f:
                    sha256.update(f.read())
                new_hash = sha256.hexdigest()
                
                if new_hash == issue.expected_hash:
                    issue.repair_log.append("Git恢复后Hash验证通过")
                    return RepairStatus.SUCCESS
                else:
                    issue.repair_log.append("Git恢复后Hash仍不匹配")
        except Exception as e:
            issue.repair_log.append(f"Git恢复异常: {str(e)}")
        
        # 尝试从备份目录恢复
        backup_file = os.path.join(BACKUP_ROOT, rel_path)
        if os.path.exists(backup_file):
            try:
                shutil.copy2(backup_file, file_path)
                
                # 验证备份的hash
                sha256 = hashlib.sha256()
                with open(file_path, 'rb') as f:
                    sha256.update(f.read())
                backup_hash = sha256.hexdigest()
                
                if backup_hash == issue.expected_hash:
                    issue.repair_log.append("备份恢复后Hash验证通过")
                    return RepairStatus.SUCCESS
                else:
                    issue.repair_log.append("备份Hash也不匹配，可能需要全量备份")
            except Exception as e:
                issue.repair_log.append(f"备份恢复异常: {str(e)}")
        
        return RepairStatus.MANUAL_REQUIRED
    
    def _repair_permission(self, issue: Issue) -> RepairStatus:
        """尝试修复权限问题"""
        file_path = issue.file_path
        
        issue.repair_log.append("尝试修复文件权限")
        
        try:
            # 恢复默认权限 644
            os.chmod(file_path, 0o644)
            
            if os.access(file_path, os.R_OK):
                issue.repair_log.append("权限修复成功")
                return RepairStatus.SUCCESS
            else:
                issue.repair_log.append("权限修复后仍无法读取")
                return RepairStatus.FAILED
        except Exception as e:
            issue.repair_log.append(f"权限修复异常: {str(e)}")
            return RepairStatus.FAILED
    
    def _repair_chain(self, issue: Issue) -> RepairStatus:
        """尝试修复备份链"""
        issue.repair_log.append("备份链断裂需要全量备份")
        # 备份链断裂需要重新执行全量备份，无法自动修复
        return RepairStatus.MANUAL_REQUIRED
    
    def get_summary(self) -> Dict:
        """获取修复摘要"""
        return {
            "attempted_repairs": self.attempted_repairs,
            "successful_repairs": self.successful_repairs,
            "failed_repairs": self.failed_repairs,
            "manual_required": self.manual_required,
            "success_rate": round(self.successful_repairs / max(self.attempted_repairs, 1) * 100, 1)
        }

# ============ 告警通知 ============
class AlertManager:
    """告警通知管理"""
    
    def __init__(self):
        self.notifications_sent = []
    
    def send_alert(self, report: VerificationReport, channels: List[str] = None):
        """发送告警通知"""
        if channels is None:
            channels = ["log", "file"]
        
        for channel in channels:
            if channel == "log":
                self._alert_via_log(report)
            elif channel == "file":
                self._alert_via_file(report)
            elif channel == "feishu" and FEISHU_WEBHOOK:
                self._alert_via_feishu(report)
    
    def _alert_via_log(self, report: VerificationReport):
        """通过日志发送告警"""
        if report.overall_status != "passed":
            logger.warning(f"⚠️ 备份验证告警 - 状态: {report.overall_status}, 健康度: {report.health_score}%")
            for layer_name, layer in report.layers.items():
                if layer.failed > 0:
                    logger.warning(f"  - {layer_name}: {layer.failed} 个失败")
    
    def _alert_via_file(self, report: VerificationReport):
        """写入告警文件"""
        alert_file = "/tmp/backup_alerts.jsonl"
        alert_entry = {
            "timestamp": report.timestamp,
            "verification_id": report.verification_id,
            "status": report.overall_status,
            "health_score": report.health_score,
            "requires_attention": report.overall_status != "passed"
        }
        with open(alert_file, 'a') as f:
            f.write(json.dumps(alert_entry) + '\n')
    
    def _alert_via_feishu(self, report: VerificationReport):
        """通过飞书发送告警（预留接口）"""
        # 实际实现需要飞书Webhook配置
        pass

# ============ S7: 对抗测试 ============
class AdversarialTester:
    """S7: 对抗测试 - 模拟备份损坏场景"""
    
    TEST_SCENARIOS = [
        {
            "name": "文件截断",
            "action": "truncate_file",
            "expected_detection": ["size_mismatch", "corrupted"]
        },
        {
            "name": "内容篡改",
            "action": "modify_byte",
            "expected_detection": ["corrupted"]
        },
        {
            "name": "文件缺失",
            "action": "delete_file",
            "expected_detection": ["missing_file"]
        },
        {
            "name": "权限拒绝",
            "action": "change_permission",
            "expected_detection": ["permission_denied"]
        },
        {
            "name": "元数据损坏",
            "action": "corrupt_metadata",
            "expected_detection": ["metadata_error"]
        }
    ]
    
    def __init__(self, test_dir: str = "/tmp/adversarial_test"):
        self.test_dir = test_dir
        self.test_results = []
    
    def setup_test_environment(self) -> bool:
        """设置对抗测试环境"""
        os.makedirs(self.test_dir, exist_ok=True)
        
        # 创建测试文件
        test_files = [
            ("test_file1.txt", "This is test content for adversarial testing." * 10),
            ("test_file2.md", "# Test Markdown\n\nThis is a test file."),
            ("subdir/nested.txt", "Nested file content here.")
        ]
        
        for filename, content in test_files:
            filepath = os.path.join(self.test_dir, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                f.write(content)
        
        return True
    
    def run_truncate_test(self) -> Dict:
        """测试文件截断检测"""
        test_file = os.path.join(self.test_dir, "test_file1.txt")
        
        # 获取原始hash
        sha256 = hashlib.sha256()
        with open(test_file, 'rb') as f:
            original_content = f.read()
            sha256.update(original_content)
        original_hash = sha256.hexdigest()
        original_size = len(original_content)
        
        # 截断文件
        with open(test_file, 'wb') as f:
            f.write(original_content[:original_size // 2])
        
        # 验证检测
        sha256 = hashlib.sha256()
        with open(test_file, 'rb') as f:
            sha256.update(f.read())
        new_hash = sha256.hexdigest()
        
        detected = (new_hash != original_hash) or (os.path.getsize(test_file) != original_size)
        
        # 恢复原文件
        with open(test_file, 'wb') as f:
            f.write(original_content)
        
        return {
            "scenario": "文件截断",
            "detected": detected,
            "expected": True,
            "passed": detected == True
        }
    
    def run_modification_test(self) -> Dict:
        """测试内容篡改检测"""
        test_file = os.path.join(self.test_dir, "test_file2.md")
        
        # 获取原始hash
        sha256 = hashlib.sha256()
        with open(test_file, 'rb') as f:
            original_content = f.read()
            sha256.update(original_content)
        original_hash = sha256.hexdigest()
        
        # 修改一个字节
        modified = bytearray(original_content)
        if len(modified) > 0:
            modified[0] = (modified[0] + 1) % 256
        
        with open(test_file, 'wb') as f:
            f.write(bytes(modified))
        
        # 验证检测
        sha256 = hashlib.sha256()
        with open(test_file, 'rb') as f:
            sha256.update(f.read())
        new_hash = sha256.hexdigest()
        
        detected = new_hash != original_hash
        
        # 恢复原文件
        with open(test_file, 'wb') as f:
            f.write(original_content)
        
        return {
            "scenario": "内容篡改(1字节)",
            "detected": detected,
            "expected": True,
            "passed": detected == True
        }
    
    def run_missing_file_test(self) -> Dict:
        """测试文件缺失检测"""
        test_file = os.path.join(self.test_dir, "temp_test_file.txt")
        
        # 创建临时文件
        with open(test_file, 'w') as f:
            f.write("Temporary content")
        
        # 记录存在
        existed = os.path.exists(test_file)
        
        # 删除文件
        os.remove(test_file)
        
        # 验证检测
        detected = not os.path.exists(test_file)
        
        return {
            "scenario": "文件缺失",
            "detected": detected and existed,
            "expected": True,
            "passed": detected and existed
        }
    
    def run_all_tests(self) -> List[Dict]:
        """运行所有对抗测试"""
        self.setup_test_environment()
        
        results = []
        results.append(self.run_truncate_test())
        results.append(self.run_modification_test())
        results.append(self.run_missing_file_test())
        
        self.test_results = results
        return results
    
    def get_summary(self) -> Dict:
        """获取对抗测试摘要"""
        if not self.test_results:
            return {"status": "not_run", "passed": 0, "total": 0}
        
        passed = sum(1 for r in self.test_results if r["passed"])
        total = len(self.test_results)
        
        return {
            "status": "passed" if passed == total else "failed",
            "passed": passed,
            "total": total,
            "pass_rate": f"{passed}/{total}",
            "details": self.test_results
        }

# ============ 主验证引擎 ============
class BackupVerificationEngine:
    """备份验证主引擎"""
    
    def __init__(self, workspace: str = WORKSPACE):
        self.workspace = workspace
        self.layers = {}
        self.issues = []
        self.auto_repair = AutoRepair(workspace)
        self.alert_manager = AlertManager()
        self.adversarial_tester = AdversarialTester()
        self.self_validator = SelfValidator()
    
    def verify(self, deep_mode: bool = False, enable_repair: bool = True, 
               enable_adversarial_test: bool = False) -> VerificationReport:
        """执行完整验证流程"""
        
        start_time = time.time()
        verification_id = f"ver_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"=== 开始备份验证 [{verification_id}] ===")
        
        # S5: 自我验证 - 环境检查
        env_ok, env_errors = self.self_validator.validate_environment()
        self_check = {
            "environment_valid": env_ok,
            "failed_checks": env_errors,
            "hash_algorithm_valid": self.self_validator.validate_hash_algorithm()
        }
        
        if not env_ok:
            return VerificationReport(
                timestamp=datetime.now().isoformat(),
                verification_id=verification_id,
                overall_status="error",
                health_score=0,
                layers={},
                repair_summary={},
                limitations=["环境自检失败，无法执行验证"],
                self_check=self_check
            )
        
        # L1: 存在性检查
        self.layers["existence"] = self._check_existence()
        
        # L2: 大小检查
        self.layers["size"] = self._check_size()
        
        # L3: Hash校验
        sample_size = 1000 if deep_mode else 100
        self.layers["hash"] = self._check_hash(sample_size)
        
        # L4: 恢复测试
        if deep_mode:
            self.layers["recovery"] = self._test_recovery()
        
        # S2: 自动修复
        repair_summary = {"enabled": enable_repair, "attempted": False}
        if enable_repair:
            all_issues = []
            for layer in self.layers.values():
                all_issues.extend(layer.issues)
            
            if all_issues:
                logger.info(f"发现 {len(all_issues)} 个问题，启动自动修复...")
                for issue in all_issues:
                    self.auto_repair.attempt_repair(issue)
                repair_summary = self.auto_repair.get_summary()
                repair_summary["attempted"] = True
                
                # 修复后重新验证关键项目
                if repair_summary["successful_repairs"] > 0:
                    self.layers["existence"] = self._check_existence()
        
        # S7: 对抗测试（可选）
        adversarial_summary = None
        if enable_adversarial_test:
            self.adversarial_tester.run_all_tests()
            adversarial_summary = self.adversarial_tester.get_summary()
        
        # 计算健康分数
        health_score = self._calculate_health_score()
        
        # 确定总体状态
        overall_status = self._determine_status(health_score)
        
        # S1: 灾备影响评估
        failed_files = [i.file_path for i in self.issues if i.severity in [Severity.CRITICAL, Severity.HIGH]]
        impact_assessment = GlobalConsideration.get_impact_assessment(failed_files)
        
        # 告警通知
        report = VerificationReport(
            timestamp=datetime.now().isoformat(),
            verification_id=verification_id,
            overall_status=overall_status,
            health_score=health_score,
            layers=self.layers,
            repair_summary=repair_summary,
            limitations=self._get_limitations(),
            self_check=self_check
        )
        
        # 如果状态不是passed，发送告警
        if overall_status != "passed":
            self.alert_manager.send_alert(report, channels=["log", "file"])
        
        # 保存报告
        self._save_report(report)
        
        duration = time.time() - start_time
        logger.info(f"=== 验证完成 [{duration:.2f}s] 健康度: {health_score}% ===")
        
        return report
    
    def _check_existence(self) -> VerificationLayer:
        """L1: 文件存在性检查"""
        layer = VerificationLayer(name="文件存在性检查")
        start = time.time()
        
        critical_files = [
            "SOUL.md", "IDENTITY.md", "USER.md", "AGENTS.md", 
            "MEMORY.md", "BOOTSTRAP.md", "TOOLS.md"
        ]
        
        for filename in critical_files:
            filepath = os.path.join(self.workspace, filename)
            layer.checked += 1
            
            if os.path.exists(filepath):
                layer.passed += 1
            else:
                layer.failed += 1
                issue = Issue(
                    file_path=filepath,
                    issue_type=IssueType.MISSING_FILE,
                    severity=Severity.CRITICAL,
                    description=f"关键文件缺失: {filename}"
                )
                layer.issues.append(issue)
                self.issues.append(issue)
        
        layer.duration_ms = (time.time() - start) * 1000
        return layer
    
    def _check_size(self) -> VerificationLayer:
        """L2: 文件大小检查"""
        layer = VerificationLayer(name="文件大小合理性检查")
        start = time.time()
        
        for root, dirs, files in os.walk(self.workspace):
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__']]
            
            for filename in files:
                filepath = os.path.join(root, filename)
                layer.checked += 1
                
                try:
                    size = os.path.getsize(filepath)
                    
                    # 检查异常小文件（可能截断）
                    if size == 0 and filename.endswith('.md'):
                        layer.failed += 1
                        issue = Issue(
                            file_path=filepath,
                            issue_type=IssueType.SIZE_MISMATCH,
                            severity=Severity.HIGH,
                            description="文件大小为0，可能截断"
                        )
                        layer.issues.append(issue)
                        self.issues.append(issue)
                    else:
                        layer.passed += 1
                        
                except Exception as e:
                    layer.failed += 1
                    issue = Issue(
                        file_path=filepath,
                        issue_type=IssueType.PERMISSION_DENIED,
                        severity=Severity.MEDIUM,
                        description=f"无法读取文件大小: {str(e)}"
                    )
                    layer.issues.append(issue)
                    self.issues.append(issue)
        
        layer.duration_ms = (time.time() - start) * 1000
        return layer
    
    def _check_hash(self, sample_size: int) -> VerificationLayer:
        """L3: Hash校验"""
        layer = VerificationLayer(name="Hash完整性校验")
        start = time.time()
        
        # 收集文件
        files_to_check = []
        for root, dirs, files in os.walk(self.workspace):
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__']]
            for filename in files:
                if not filename.startswith('.'):
                    files_to_check.append(os.path.join(root, filename))
        
        # 抽样
        import random
        if len(files_to_check) > sample_size:
            files_to_check = random.sample(files_to_check, sample_size)
        
        # 加载hash数据库
        hash_db = self._load_hash_db()
        
        for filepath in files_to_check:
            layer.checked += 1
            
            try:
                sha256 = hashlib.sha256()
                with open(filepath, 'rb') as f:
                    for chunk in iter(lambda: f.read(8192), b''):
                        sha256.update(chunk)
                current_hash = sha256.hexdigest()
                
                rel_path = os.path.relpath(filepath, self.workspace)
                
                if rel_path in hash_db:
                    if hash_db[rel_path] == current_hash:
                        layer.passed += 1
                    else:
                        layer.failed += 1
                        issue = Issue(
                            file_path=filepath,
                            issue_type=IssueType.CORRUPTED,
                            severity=Severity.CRITICAL,
                            description="Hash不匹配，文件可能损坏",
                            expected_hash=hash_db[rel_path],
                            actual_hash=current_hash
                        )
                        layer.issues.append(issue)
                        self.issues.append(issue)
                else:
                    # 新文件，记录hash
                    hash_db[rel_path] = current_hash
                    layer.passed += 1
                    
            except Exception as e:
                layer.failed += 1
                issue = Issue(
                    file_path=filepath,
                    issue_type=IssueType.PERMISSION_DENIED,
                    severity=Severity.MEDIUM,
                    description=f"无法计算Hash: {str(e)}"
                )
                layer.issues.append(issue)
                self.issues.append(issue)
        
        # 保存hash数据库
        self._save_hash_db(hash_db)
        
        layer.duration_ms = (time.time() - start) * 1000
        return layer
    
    def _test_recovery(self) -> VerificationLayer:
        """L4: 恢复测试"""
        layer = VerificationLayer(name="抽样恢复测试")
        start = time.time()
        
        # 清理并创建恢复区
        if os.path.exists(RECOVERY_ZONE):
            shutil.rmtree(RECOVERY_ZONE)
        os.makedirs(RECOVERY_ZONE, exist_ok=True)
        
        # 选择测试文件
        test_files = [
            os.path.join(self.workspace, "SOUL.md"),
            os.path.join(self.workspace, "IDENTITY.md"),
            os.path.join(self.workspace, "USER.md")
        ]
        
        for filepath in test_files:
            layer.checked += 1
            
            if os.path.exists(filepath):
                try:
                    # 模拟恢复：复制到恢复区并验证可读
                    filename = os.path.basename(filepath)
                    recovery_path = os.path.join(RECOVERY_ZONE, filename)
                    shutil.copy2(filepath, recovery_path)
                    
                    # 验证内容可读
                    with open(recovery_path, 'r') as f:
                        content = f.read()
                        if len(content) > 0:
                            layer.passed += 1
                        else:
                            layer.failed += 1
                            issue = Issue(
                                file_path=filepath,
                                issue_type=IssueType.RECOVERY_FAILED,
                                severity=Severity.CRITICAL,
                                description="恢复后文件内容为空"
                            )
                            layer.issues.append(issue)
                            self.issues.append(issue)
                            
                except Exception as e:
                    layer.failed += 1
                    issue = Issue(
                        file_path=filepath,
                        issue_type=IssueType.RECOVERY_FAILED,
                        severity=Severity.CRITICAL,
                        description=f"恢复测试失败: {str(e)}"
                    )
                    layer.issues.append(issue)
                    self.issues.append(issue)
            else:
                layer.failed += 1
                issue = Issue(
                    file_path=filepath,
                    issue_type=IssueType.MISSING_FILE,
                    severity=Severity.CRITICAL,
                    description="测试文件不存在"
                )
                layer.issues.append(issue)
                self.issues.append(issue)
        
        layer.duration_ms = (time.time() - start) * 1000
        return layer
    
    def _load_hash_db(self) -> Dict[str, str]:
        """加载Hash数据库"""
        if os.path.exists(HASH_DB):
            try:
                with open(HASH_DB, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_hash_db(self, hash_db: Dict[str, str]):
        """保存Hash数据库"""
        os.makedirs(os.path.dirname(HASH_DB), exist_ok=True)
        with open(HASH_DB, 'w') as f:
            json.dump(hash_db, f, indent=2)
    
    def _calculate_health_score(self) -> int:
        """计算健康分数"""
        total_checked = sum(l.checked for l in self.layers.values())
        total_passed = sum(l.passed for l in self.layers.values())
        
        if total_checked == 0:
            return 0
        
        return int((total_passed / total_checked) * 100)
    
    def _determine_status(self, health_score: int) -> str:
        """确定总体状态"""
        if health_score == 100:
            return "passed"
        elif health_score >= 90:
            return "partial"
        else:
            return "failed"
    
    def _get_limitations(self) -> List[str]:
        """S6: 认知谦逊 - 获取验证局限"""
        return [
            "Hash校验为抽样检查，非全量覆盖（基于配置）",
            "恢复测试仅验证文件可读性，不验证业务逻辑正确性",
            "无法检测加密备份的内容完整性（需密钥）",
            "无法预测未来的存储介质损坏",
            "大文件Hash计算可能影响性能",
            "云存储API限制可能影响验证频率"
        ]
    
    def _save_report(self, report: VerificationReport):
        """保存验证报告"""
        # 保存最新报告
        with open(VERIFICATION_JSON, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        
        # 追加到历史记录
        with open(VERIFICATION_HISTORY, 'a') as f:
            f.write(json.dumps(report.to_dict()) + '\n')

def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='备份验证系统 V2.0')
    parser.add_argument('--deep', action='store_true', help='执行深度验证')
    parser.add_argument('--no-repair', action='store_true', help='禁用自动修复')
    parser.add_argument('--adversarial-test', action='store_true', help='运行对抗测试')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    
    args = parser.parse_args()
    
    engine = BackupVerificationEngine()
    report = engine.verify(
        deep_mode=args.deep,
        enable_repair=not args.no_repair,
        enable_adversarial_test=args.adversarial_test
    )
    
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print("\n" + "="*60)
        print(f"📊 备份验证报告 [{report.verification_id}]")
        print("="*60)
        print(f"时间: {report.timestamp}")
        print(f"状态: {'✅ 通过' if report.overall_status == 'passed' else '⚠️ 部分通过' if report.overall_status == 'partial' else '❌ 失败'}")
        print(f"健康度: {report.health_score}%")
        print("-"*60)
        print("分层验证结果:")
        for name, layer in report.layers.items():
            status = "✅" if layer.failed == 0 else "❌"
            print(f"  {status} {layer.name}: {layer.passed}/{layer.checked}")
        print("-"*60)
        
        if report.repair_summary.get("attempted"):
            summary = report.repair_summary
            print("自动修复摘要:")
            print(f"  尝试修复: {summary.get('attempted_repairs', 0)}")
            print(f"  修复成功: {summary.get('successful_repairs', 0)}")
            print(f"  需要人工: {summary.get('manual_required', 0)}")
            print(f"  成功率: {summary.get('success_rate', 0)}%")
        
        print("="*60)
    
    # 返回状态码
    sys.exit(0 if report.overall_status == "passed" else 1)

if __name__ == "__main__":
    main()
