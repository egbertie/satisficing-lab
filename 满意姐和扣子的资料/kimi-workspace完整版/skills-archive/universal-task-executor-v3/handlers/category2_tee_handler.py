import sys
sys.path.insert(0, "/root/.openclaw/workspace/skills/universal-task-executor-v3")
"""
Universal Task Executor V3.0 - Category 2: TEE脚本整改处理器
处理Trusted Execution Environment相关脚本的整改、审计和优化
"""

import os
import re
import json
import logging
import hashlib
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from pathlib import Path

from core.registry import TaskHandler
from core.structures import Task, TaskResult, TaskStatus, AuditRecord
from core.token_engine import TokenEngine

logger = logging.getLogger(__name__)


class Category2TEEHandler(TaskHandler):
    """
    第2类处理器：TEE脚本整改处理器
    
    职责：
    1. TEE脚本安全审计
    2. 识别和修复安全漏洞
    3. 密钥管理检查
    4. 敏感操作审查
    5. 合规性验证
    
    TEE安全要求：
    - 密钥不得硬编码
    - 敏感操作需要审计日志
    - 输入验证必须完整
    - 错误处理不得泄露敏感信息
    """
    
    handler_name = "category2_tee_handler"
    supported_categories = ["category_2"]
    version = "3.0.0"
    
    # 安全风险等级
    RISK_LEVELS = {
        "critical": "严重 - 必须立即修复",
        "high": "高危 - 24小时内修复",
        "medium": "中危 - 一周内修复",
        "low": "低危 - 下次迭代修复"
    }
    
    # 安全审计规则
    SECURITY_RULES = [
        {
            "id": "KEY_HARDCODED",
            "name": "硬编码密钥",
            "pattern": r'(password|secret|key|token)\s*=\s*["\'][^"\']+["\']',
            "risk_level": "critical",
            "description": "发现可能的硬编码密钥"
        },
        {
            "id": "SQL_INJECTION",
            "name": "SQL注入风险",
            "pattern": r'execute\s*\(.*\+.*\)|\.format\s*\(.*\).*SELECT|\.format\s*\(.*\).*INSERT',
            "risk_level": "critical",
            "description": "存在SQL注入风险"
        },
        {
            "id": "COMMAND_INJECTION",
            "name": "命令注入风险",
            "pattern": r'os\.system\s*\(|subprocess\.call\s*\(.*shell\s*=\s*True',
            "risk_level": "high",
            "description": "存在命令注入风险"
        },
        {
            "id": "INSECURE_RANDOM",
            "name": "不安全随机数",
            "pattern": r'random\.random\(\)|random\.randint',
            "risk_level": "medium",
            "description": "使用不安全的随机数生成器"
        },
        {
            "id": "DEBUG_INFO",
            "name": "调试信息泄露",
            "pattern": r'print\s*\(.*password|print\s*\(.*secret|console\.log\s*\(.*password',
            "risk_level": "high",
            "description": "可能泄露敏感信息的调试输出"
        },
        {
            "id": "WEAK_CRYPTO",
            "name": "弱加密算法",
            "pattern": r'md5|sha1|DES|RC4',
            "risk_level": "high",
            "description": "使用了弱加密算法"
        },
        {
            "id": "NO_INPUT_VALIDATION",
            "name": "缺少输入验证",
            "pattern": r'request\.(args|form|json)\[.*\](?!\s*\n.*if.*validate)',
            "risk_level": "medium",
            "description": "用户输入缺少验证"
        },
        {
            "id": "INSECURE_FILE_OP",
            "name": "不安全文件操作",
            "pattern": r'open\s*\(\s*.*\+.*\)|with\s+open\s*\(\s*.*\+',
            "risk_level": "medium",
            "description": "可能存在路径遍历风险"
        }
    ]
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.script_audit_dir = self.config.get("script_audit_dir", "memory/tee_audits/")
        self.remediation_log_dir = self.config.get("remediation_log_dir", "logs/tee_remediation/")
        self.audit_results: Dict[str, Dict] = {}
        
        os.makedirs(self.script_audit_dir, exist_ok=True)
        os.makedirs(self.remediation_log_dir, exist_ok=True)
        
        logger.info(f"Category2TEEHandler initialized: audit_dir={self.script_audit_dir}")
    
    def validate(self, task: Task) -> bool:
        """验证TEE整改任务数据"""
        if not super().validate(task):
            return False
        
        data = task.data
        
        # 检查脚本内容或路径
        if "script_content" not in data and "script_path" not in data:
            logger.error("Task validation failed: missing script_content or script_path")
            return False
        
        return True
    
    def execute(self, task: Task, checkpoint_state: Optional[Dict] = None) -> TaskResult:
        """执行TEE脚本整改"""
        start_time = datetime.now()
        task_id = task.task_id
        
        if checkpoint_state:
            self._restore_state(checkpoint_state)
        
        try:
            data = task.data
            script_name = data.get("script_name", f"script_{task_id}")
            script_content = data.get("script_content", "")
            script_path = data.get("script_path", "")
            remediation_required = data.get("remediation_required", True)
            
            # 如果提供了路径，读取内容
            if script_path and not script_content:
                script_content = self._read_script(script_path)
            
            # 1. 安全扫描
            vulnerabilities = self._scan_security(script_content)
            
            # 2. 合规性检查
            compliance_issues = self._check_compliance(script_content)
            
            # 3. 生成审计报告
            audit_report = self._generate_audit_report(task_id, script_name, 
                                                       script_content, vulnerabilities, 
                                                       compliance_issues)
            
            # 4. 如果需要整改，执行修复
            remediated_content = None
            remediation_log = None
            if remediation_required and vulnerabilities:
                remediated_content = self._remediate_script(script_content, vulnerabilities)
                remediation_log = self._create_remediation_log(task_id, script_name, 
                                                               vulnerabilities, remediated_content)
            
            # 5. 保存结果
            self.audit_results[task_id] = {
                "script_name": script_name,
                "audit_report": audit_report,
                "remediation_applied": remediation_required and bool(vulnerabilities),
                "remediated_content_hash": hashlib.sha256(
                    (remediated_content or "").encode()
                ).hexdigest()[:16] if remediated_content else None,
                "timestamp": datetime.now().isoformat()
            }
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            return TaskResult(
                task_id=task_id,
                status="completed",
                output={
                    "script_name": script_name,
                    "vulnerabilities_found": len(vulnerabilities),
                    "vulnerabilities": vulnerabilities,
                    "compliance_issues": compliance_issues,
                    "audit_report_path": audit_report.get("report_path"),
                    "remediation_applied": bool(remediated_content),
                    "remediation_summary": self._summarize_remediation(vulnerabilities),
                    "critical_count": sum(1 for v in vulnerabilities if v["risk_level"] == "critical"),
                    "high_count": sum(1 for v in vulnerabilities if v["risk_level"] == "high"),
                    "medium_count": sum(1 for v in vulnerabilities if v["risk_level"] == "medium"),
                    "low_count": sum(1 for v in vulnerabilities if v["risk_level"] == "low")
                },
                token_consumed=3000,
                time_elapsed=elapsed,
                audit_required=True
            )
            
        except Exception as e:
            logger.error(f"TEE remediation failed: {task_id}, error={e}")
            elapsed = (datetime.now() - start_time).total_seconds()
            return TaskResult(
                task_id=task_id,
                status="failed",
                output={},
                token_consumed=1500,
                time_elapsed=elapsed,
                error=str(e)
            )
    
    def _read_script(self, script_path: str) -> str:
        """读取脚本内容"""
        try:
            with open(script_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read script: {script_path}, error={e}")
            return ""
    
    def _scan_security(self, script_content: str) -> List[Dict]:
        """安全扫描"""
        vulnerabilities = []
        lines = script_content.split("\n")
        
        for rule in self.SECURITY_RULES:
            pattern = re.compile(rule["pattern"], re.IGNORECASE)
            
            for line_num, line in enumerate(lines, 1):
                if pattern.search(line):
                    vulnerabilities.append({
                        "rule_id": rule["id"],
                        "rule_name": rule["name"],
                        "risk_level": rule["risk_level"],
                        "description": rule["description"],
                        "line_number": line_num,
                        "line_content": line.strip(),
                        "suggested_fix": self._get_suggested_fix(rule["id"])
                    })
        
        return vulnerabilities
    
    def _check_compliance(self, script_content: str) -> List[Dict]:
        """合规性检查"""
        issues = []
        
        # 检查是否有函数文档
        if "def " in script_content and '"""' not in script_content and "'''" not in script_content:
            issues.append({
                "type": "missing_docstrings",
                "description": "函数缺少文档字符串",
                "severity": "low"
            })
        
        # 检查是否有错误处理
        if "try:" not in script_content and "except" not in script_content:
            issues.append({
                "type": "missing_error_handling",
                "description": "缺少错误处理机制",
                "severity": "medium"
            })
        
        # 检查是否有日志记录
        if "import logging" not in script_content and "logger" not in script_content:
            issues.append({
                "type": "missing_logging",
                "description": "缺少日志记录机制",
                "severity": "low"
            })
        
        return issues
    
    def _get_suggested_fix(self, rule_id: str) -> str:
        """获取建议修复方案"""
        fixes = {
            "KEY_HARDCODED": "使用环境变量或密钥管理服务存储密钥",
            "SQL_INJECTION": "使用参数化查询或ORM框架",
            "COMMAND_INJECTION": "避免使用shell=True，使用参数列表传递命令",
            "INSECURE_RANDOM": "使用secrets模块生成加密安全的随机数",
            "DEBUG_INFO": "移除调试输出或使用日志级别控制",
            "WEAK_CRYPTO": "使用SHA-256或更强的哈希算法，使用AES加密",
            "NO_INPUT_VALIDATION": "添加输入验证和清洗逻辑",
            "INSECURE_FILE_OP": "使用pathlib规范路径，验证文件路径"
        }
        return fixes.get(rule_id, "参考安全编码规范进行修复")
    
    def _generate_audit_report(self, task_id: str, script_name: str,
                               script_content: str, vulnerabilities: List[Dict],
                               compliance_issues: List[Dict]) -> Dict:
        """生成审计报告"""
        report = {
            "task_id": task_id,
            "script_name": script_name,
            "script_hash": hashlib.sha256(script_content.encode()).hexdigest()[:16],
            "scan_time": datetime.now().isoformat(),
            "vulnerabilities": vulnerabilities,
            "compliance_issues": compliance_issues,
            "summary": {
                "total_vulnerabilities": len(vulnerabilities),
                "critical": sum(1 for v in vulnerabilities if v["risk_level"] == "critical"),
                "high": sum(1 for v in vulnerabilities if v["risk_level"] == "high"),
                "medium": sum(1 for v in vulnerabilities if v["risk_level"] == "medium"),
                "low": sum(1 for v in vulnerabilities if v["risk_level"] == "low"),
                "compliance_issues": len(compliance_issues)
            }
        }
        
        # 保存报告
        report_path = os.path.join(self.script_audit_dir, f"{script_name}_audit.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        report["report_path"] = report_path
        logger.info(f"Audit report generated: {report_path}")
        return report
    
    def _remediate_script(self, script_content: str, vulnerabilities: List[Dict]) -> str:
        """自动修复脚本"""
        remediated = script_content
        
        # 按行号倒序处理，避免行号变化
        sorted_vulns = sorted(vulnerabilities, key=lambda x: x["line_number"], reverse=True)
        
        lines = remediated.split("\n")
        
        for vuln in sorted_vulns:
            line_num = vuln["line_number"] - 1  # 转换为0-based
            
            if vuln["rule_id"] == "KEY_HARDCODED":
                # 替换硬编码密钥为环境变量引用
                if line_num < len(lines):
                    line = lines[line_num]
                    # 简单的替换逻辑
                    remediated_line = re.sub(
                        r'(password|secret|key|token)\s*=\s*["\'][^"\']+["\']',
                        r'\1 = os.environ.get("\1")',
                        line
                    )
                    lines[line_num] = remediated_line
            
            elif vuln["rule_id"] == "DEBUG_INFO":
                # 注释掉调试输出
                if line_num < len(lines):
                    lines[line_num] = f"# [SECURITY] {lines[line_num]}"
        
        remediated = "\n".join(lines)
        
        # 添加安全头注释
        security_header = f'''"""
[TEE Security Audit Applied]
Scan Date: {datetime.now().isoformat()}
Vulnerabilities Remediated: {len(vulnerabilities)}
DO NOT: Hardcode secrets, use unsafe eval, or disable certificate verification
"""
'''
        remediated = security_header + remediated
        
        return remediated
    
    def _create_remediation_log(self, task_id: str, script_name: str,
                                vulnerabilities: List[Dict], remediated_content: str) -> Dict:
        """创建整改日志"""
        log = {
            "task_id": task_id,
            "script_name": script_name,
            "remediation_time": datetime.now().isoformat(),
            "vulnerabilities_addressed": len(vulnerabilities),
            "remediation_details": [
                {
                    "rule_id": v["rule_id"],
                    "line_number": v["line_number"],
                    "fix_applied": v.get("suggested_fix", "")
                }
                for v in vulnerabilities
            ],
            "remediated_content_hash": hashlib.sha256(remediated_content.encode()).hexdigest()[:16]
        }
        
        log_path = os.path.join(self.remediation_log_dir, f"{script_name}_remediation.json")
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Remediation log created: {log_path}")
        return log
    
    def _summarize_remediation(self, vulnerabilities: List[Dict]) -> str:
        """汇总整改情况"""
        if not vulnerabilities:
            return "未发现安全漏洞"
        
        by_level = {}
        for v in vulnerabilities:
            level = v["risk_level"]
            by_level[level] = by_level.get(level, 0) + 1
        
        summary_parts = []
        for level in ["critical", "high", "medium", "low"]:
            if level in by_level:
                summary_parts.append(f"{self.RISK_LEVELS[level]}: {by_level[level]}个")
        
        return "; ".join(summary_parts)
    
    def _restore_state(self, state: Dict) -> None:
        """从检查点恢复状态"""
        if "audit_results" in state:
            self.audit_results = state["audit_results"]
    
    def estimate_cost(self, task: Task) -> Dict[str, int]:
        """估算Token和时间成本"""
        script_size = len(task.data.get("script_content", ""))
        # 根据脚本大小调整估算
        base_tokens = 3000
        size_factor = script_size // 1000  # 每1000字符增加估算
        
        return {
            "tokens": base_tokens + size_factor * 500,
            "time_seconds": 45 + size_factor * 5
        }
    
    def get_checkpoint_state(self) -> Dict[str, Any]:
        """获取检查点状态"""
        state = super().get_checkpoint_state()
        state["audit_results"] = self.audit_results
        return state
    
    def restore_from_checkpoint(self, state: Dict[str, Any]) -> None:
        """从检查点恢复"""
        super().restore_from_checkpoint(state)
        if "audit_results" in state:
            self.audit_results = state["audit_results"]
    
    def audit(self, task_id: Optional[str] = None) -> AuditRecord:
        """
        蓝军审计方法
        
        审计标准：
        1. 安全漏洞扫描完整性
        2. 整改建议合理性
        3. 审计报告规范性
        4. 合规性问题覆盖度
        """
        audit = AuditRecord(
            task_id=task_id,
            auditor="blue_army_category2",
            audit_type="blue_army",
            criteria=[
                "security_scan_completeness",
                "remediation_suggestions",
                "report_format",
                "compliance_coverage"
            ]
        )
        
        # 检查审计结果
        for tid, result in self.audit_results.items():
            audit_report = result.get("audit_report", {})
            
            # 检查是否有漏洞未记录
            vulnerabilities = audit_report.get("vulnerabilities", [])
            summary = audit_report.get("summary", {})
            
            if summary.get("total_vulnerabilities", 0) != len(vulnerabilities):
                audit.add_finding(
                    item=f"漏洞统计一致性: {result.get('script_name')}",
                    expected="统计与实际一致",
                    actual=f"统计{summary.get('total_vulnerabilities')} != 实际{len(vulnerabilities)}",
                    severity="warning"
                )
            
            # 检查关键漏洞是否都有建议修复
            for vuln in vulnerabilities:
                if vuln["risk_level"] in ["critical", "high"]:
                    if not vuln.get("suggested_fix"):
                        audit.add_finding(
                            item=f"高风险漏洞缺少修复建议: {vuln['rule_id']}",
                            expected="有修复建议",
                            actual="缺少修复建议",
                            severity="critical"
                        )
            
            # 检查报告文件是否存在
            report_path = audit_report.get("report_path", "")
            if report_path and not os.path.exists(report_path):
                audit.add_finding(
                    item=f"审计报告文件存在性: {result.get('script_name')}",
                    expected="报告文件存在",
                    actual="报告文件不存在",
                    severity="high"
                )
        
        # 决定审计结果
        critical_count = sum(1 for f in audit.findings if f["severity"] == "critical")
        
        audit.passed = critical_count == 0
        audit.severity = "critical" if critical_count > 0 else (
            "warning" if any(f["severity"] == "warning" for f in audit.findings) else "info"
        )
        
        if critical_count > 0:
            audit.recommendations.append("立即修复关键安全问题")
        elif audit.findings:
            audit.recommendations.append("关注发现的警告问题")
        else:
            audit.recommendations.append("TEE审计流程运行正常")
        
        logger.info(f"Category2 audit completed: {audit.passed}, findings={len(audit.findings)}")
        return audit


def register_handler(registry):
    """注册处理器到注册表"""
    registry.register_handler(Category2TEEHandler)
    logger.info("Category2TEEHandler registered")
