import sys
sys.path.insert(0, "/root/.openclaw/workspace/skills/universal-task-executor-v3")
"""
Universal Task Executor V3.0 - Category 3: Skill虚报审计处理器
处理Skill完成度虚报的检测、审计和整改
"""

import os
import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

from core.registry import TaskHandler
from core.structures import Task, TaskResult, TaskStatus, AuditRecord
from core.token_engine import TokenEngine

logger = logging.getLogger(__name__)


class Category3SkillHandler(TaskHandler):
    """
    第3类处理器：Skill虚报审计处理器
    
    职责：
    1. 检测Skill声称完成度与实际完成度的差异
    2. 审计Skill文件的物理存在性
    3. 验证Skill功能的可执行性
    4. 标记和整改虚报问题
    
    虚报检测维度：
    - 文件存在性（声称有，实际没有）
    - 功能实现性（声称完成，实际不可执行）
    - 文档完整性（声称文档化，实际缺失）
    - 测试覆盖度（声称测试，实际未测）
    """
    
    handler_name = "category3_skill_handler"
    supported_categories = ["category_3"]
    version = "3.0.0"
    
    # 虚报严重程度
    MISREPRESENTATION_LEVELS = {
        "severe": "严重虚报 - 声称100%实际<50%",
        "significant": "显著虚报 - 声称完成实际未完成",
        "minor": "轻微虚报 - 部分声称未完全实现",
        "documentation": "文档虚报 - 文档声称存在实际缺失"
    }
    
    # Skill声称关键词映射
    CLAIM_PATTERNS = {
        "file_exists": [
            r"已创建\s*[:：]?\s*(\S+)",
            r"文件[:：]\s*(\S+)\s*已生成",
            r"输出[:：]\s*(\S+)",
        ],
        "function_complete": [
            r"已实现\s*[:：]?\s*(\S+)",
            r"功能[:：]\s*(\S+)\s*完成",
            r"完成[:：]\s*(\S+)",
        ],
        "documented": [
            r"已文档化",
            r"文档[:：]\s*完成",
            r"README\s*已更新",
        ],
        "tested": [
            r"已测试",
            r"测试[:：]\s*通过",
            r"测试覆盖率[:：]",
        ]
    }
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.audit_dir = self.config.get("audit_dir", "memory/skill_audits/")
        self.skill_base_path = self.config.get("skill_base_path", 
                                               "/root/.openclaw/workspace/skills/")
        self.audit_history: Dict[str, Dict] = {}
        
        os.makedirs(self.audit_dir, exist_ok=True)
        
        logger.info(f"Category3SkillHandler initialized: audit_dir={self.audit_dir}")
    
    def validate(self, task: Task) -> bool:
        """验证Skill审计任务数据"""
        if not super().validate(task):
            return False
        
        data = task.data
        
        # 检查是否有Skill名称或审计内容
        if "skill_name" not in data and "skill_claims" not in data:
            logger.error("Task validation failed: missing skill_name or skill_claims")
            return False
        
        return True
    
    def execute(self, task: Task, checkpoint_state: Optional[Dict] = None) -> TaskResult:
        """执行Skill虚报审计"""
        start_time = datetime.now()
        task_id = task.task_id
        
        if checkpoint_state:
            self._restore_state(checkpoint_state)
        
        try:
            data = task.data
            skill_name = data.get("skill_name", f"skill_{task_id}")
            skill_claims = data.get("skill_claims", {})
            conversation_content = data.get("conversation_content", "")
            audit_scope = data.get("audit_scope", ["file_exists", "function_complete", "documented", "tested"])
            
            # 1. 解析声称内容
            if not skill_claims and conversation_content:
                skill_claims = self._parse_claims_from_conversation(conversation_content)
            
            # 2. 验证各项声称
            verification_results = {}
            misrepresentations = []
            
            if "file_exists" in audit_scope:
                file_results, file_misrep = self._verify_file_claims(skill_name, skill_claims)
                verification_results["file_exists"] = file_results
                misrepresentations.extend(file_misrep)
            
            if "function_complete" in audit_scope:
                func_results, func_misrep = self._verify_function_claims(skill_name, skill_claims)
                verification_results["function_complete"] = func_results
                misrepresentations.extend(func_misrep)
            
            if "documented" in audit_scope:
                doc_results, doc_misrep = self._verify_documentation_claims(skill_name, skill_claims)
                verification_results["documented"] = doc_results
                misrepresentations.extend(doc_misrep)
            
            if "tested" in audit_scope:
                test_results, test_misrep = self._verify_test_claims(skill_name, skill_claims)
                verification_results["tested"] = test_results
                misrepresentations.extend(test_misrep)
            
            # 3. 计算虚报率
            misrepresentation_rate = self._calculate_misrepresentation_rate(verification_results)
            
            # 4. 生成审计报告
            audit_report = self._generate_audit_report(task_id, skill_name, 
                                                       skill_claims, verification_results, 
                                                       misrepresentations, misrepresentation_rate)
            
            # 5. 如果需要整改，生成整改建议
            remediation_plan = None
            if misrepresentations:
                remediation_plan = self._generate_remediation_plan(skill_name, misrepresentations)
            
            # 6. 保存审计结果
            self.audit_history[task_id] = {
                "skill_name": skill_name,
                "audit_report": audit_report,
                "misrepresentation_rate": misrepresentation_rate,
                "misrepresentation_count": len(misrepresentations),
                "timestamp": datetime.now().isoformat()
            }
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            return TaskResult(
                task_id=task_id,
                status="completed",
                output={
                    "skill_name": skill_name,
                    "misrepresentation_rate": f"{misrepresentation_rate:.1%}",
                    "misrepresentation_count": len(misrepresentations),
                    "misrepresentations": misrepresentations,
                    "verification_summary": self._summarize_verification(verification_results),
                    "audit_report_path": audit_report.get("report_path"),
                    "remediation_required": bool(misrepresentations),
                    "remediation_plan": remediation_plan,
                    "severity": self._assess_severity(misrepresentation_rate, misrepresentations)
                },
                token_consumed=2500,
                time_elapsed=elapsed,
                audit_required=True
            )
            
        except Exception as e:
            logger.error(f"Skill audit failed: {task_id}, error={e}")
            elapsed = (datetime.now() - start_time).total_seconds()
            return TaskResult(
                task_id=task_id,
                status="failed",
                output={},
                token_consumed=1200,
                time_elapsed=elapsed,
                error=str(e)
            )
    
    def _parse_claims_from_conversation(self, content: str) -> Dict[str, Any]:
        """从对话内容解析声称"""
        claims = {
            "files_created": [],
            "functions_completed": [],
            "documented": False,
            "tested": False
        }
        
        # 解析文件创建声称
        for pattern in self.CLAIM_PATTERNS["file_exists"]:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                file_path = match.group(1) if match.groups() else ""
                if file_path and not file_path.endswith(("完成", "已生成")):
                    claims["files_created"].append(file_path)
        
        # 解析功能完成声称
        for pattern in self.CLAIM_PATTERNS["function_complete"]:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                func_name = match.group(1) if match.groups() else ""
                if func_name and not func_name.endswith(("完成", "实现")):
                    claims["functions_completed"].append(func_name)
        
        # 解析文档化声称
        for pattern in self.CLAIM_PATTERNS["documented"]:
            if re.search(pattern, content, re.IGNORECASE):
                claims["documented"] = True
                break
        
        # 解析测试声称
        for pattern in self.CLAIM_PATTERNS["tested"]:
            if re.search(pattern, content, re.IGNORECASE):
                claims["tested"] = True
                break
        
        return claims
    
    def _verify_file_claims(self, skill_name: str, claims: Dict) -> Tuple[List[Dict], List[Dict]]:
        """验证文件存在性声称"""
        results = []
        misrepresentations = []
        
        files_claimed = claims.get("files_created", [])
        
        for file_path in files_claimed:
            # 处理相对路径和绝对路径
            if not file_path.startswith("/"):
                full_path = os.path.join(self.skill_base_path, skill_name, file_path)
            else:
                full_path = file_path
            
            exists = os.path.exists(full_path)
            
            result = {
                "claimed_file": file_path,
                "full_path": full_path,
                "exists": exists,
                "size_bytes": os.path.getsize(full_path) if exists else 0
            }
            results.append(result)
            
            if not exists:
                misrepresentations.append({
                    "type": "file_not_exists",
                    "claimed": file_path,
                    "actual": "文件不存在",
                    "severity": "significant"
                })
        
        return results, misrepresentations
    
    def _verify_function_claims(self, skill_name: str, claims: Dict) -> Tuple[List[Dict], List[Dict]]:
        """验证功能实现声称"""
        results = []
        misrepresentations = []
        
        functions_claimed = claims.get("functions_completed", [])
        
        # 查找Skill的主要Python文件
        skill_path = os.path.join(self.skill_base_path, skill_name)
        py_files = []
        if os.path.exists(skill_path):
            for root, _, files in os.walk(skill_path):
                for file in files:
                    if file.endswith(".py"):
                        py_files.append(os.path.join(root, file))
        
        for func_name in functions_claimed:
            found = False
            implementation_quality = "not_found"
            
            # 在Python文件中查找函数定义
            for py_file in py_files:
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # 查找函数定义
                    pattern = rf'def\s+{re.escape(func_name)}\s*\('
                    if re.search(pattern, content):
                        found = True
                        # 检查实现质量
                        if '"""' in content or "'''" in content:
                            implementation_quality = "with_docstring"
                        elif len(re.findall(r'\n', content)) > 10:
                            implementation_quality = "basic"
                        else:
                            implementation_quality = "minimal"
                        break
                except Exception:
                    continue
            
            result = {
                "claimed_function": func_name,
                "found": found,
                "implementation_quality": implementation_quality
            }
            results.append(result)
            
            if not found:
                misrepresentations.append({
                    "type": "function_not_implemented",
                    "claimed": func_name,
                    "actual": "函数未找到",
                    "severity": "significant"
                })
            elif implementation_quality == "minimal":
                misrepresentations.append({
                    "type": "function_minimal_implementation",
                    "claimed": func_name,
                    "actual": "实现过于简单",
                    "severity": "minor"
                })
        
        return results, misrepresentations
    
    def _verify_documentation_claims(self, skill_name: str, claims: Dict) -> Tuple[List[Dict], List[Dict]]:
        """验证文档化声称"""
        results = []
        misrepresentations = []
        
        doc_claimed = claims.get("documented", False)
        
        skill_path = os.path.join(self.skill_base_path, skill_name)
        
        # 检查常见文档文件
        doc_files = ["SKILL.md", "README.md", "README", "docs/", "doc/"]
        found_docs = []
        
        for doc in doc_files:
            doc_path = os.path.join(skill_path, doc)
            if os.path.exists(doc_path):
                found_docs.append(doc)
        
        actually_documented = len(found_docs) > 0
        
        result = {
            "documentation_claimed": doc_claimed,
            "documentation_found": actually_documented,
            "doc_files": found_docs
        }
        results.append(result)
        
        if doc_claimed and not actually_documented:
            misrepresentations.append({
                "type": "documentation_missing",
                "claimed": "已文档化",
                "actual": f"未找到文档文件 (skill_path: {skill_path})",
                "severity": "documentation"
            })
        
        return results, misrepresentations
    
    def _verify_test_claims(self, skill_name: str, claims: Dict) -> Tuple[List[Dict], List[Dict]]:
        """验证测试声称"""
        results = []
        misrepresentations = []
        
        test_claimed = claims.get("tested", False)
        
        skill_path = os.path.join(self.skill_base_path, skill_name)
        
        # 检查测试相关文件和目录
        test_indicators = ["test_", "_test.py", "tests/", "test/", "pytest", "unittest"]
        found_tests = []
        
        if os.path.exists(skill_path):
            for root, dirs, files in os.walk(skill_path):
                for item in dirs + files:
                    for indicator in test_indicators:
                        if indicator in item:
                            found_tests.append(os.path.join(root, item))
        
        actually_tested = len(found_tests) > 0
        
        result = {
            "testing_claimed": test_claimed,
            "testing_found": actually_tested,
            "test_files": found_tests[:5]  # 最多显示5个
        }
        results.append(result)
        
        if test_claimed and not actually_tested:
            misrepresentations.append({
                "type": "testing_missing",
                "claimed": "已测试",
                "actual": "未找到测试相关文件",
                "severity": "minor"
            })
        
        return results, misrepresentations
    
    def _calculate_misrepresentation_rate(self, verification_results: Dict) -> float:
        """计算虚报率"""
        total_claims = 0
        verified_claims = 0
        
        for category, results in verification_results.items():
            if category == "file_exists":
                for r in results:
                    total_claims += 1
                    if r.get("exists"):
                        verified_claims += 1
            
            elif category == "function_complete":
                for r in results:
                    total_claims += 1
                    if r.get("found") and r.get("implementation_quality") != "minimal":
                        verified_claims += 1
            
            elif category in ["documented", "tested"]:
                for r in results:
                    if r.get(f"{category}_claimed"):
                        total_claims += 1
                        if r.get(f"{category}_found"):
                            verified_claims += 1
        
        if total_claims == 0:
            return 0.0
        
        return 1.0 - (verified_claims / total_claims)
    
    def _generate_audit_report(self, task_id: str, skill_name: str,
                               claims: Dict, verification_results: Dict,
                               misrepresentations: List[Dict], 
                               misrep_rate: float) -> Dict:
        """生成审计报告"""
        report = {
            "task_id": task_id,
            "skill_name": skill_name,
            "audit_time": datetime.now().isoformat(),
            "parsed_claims": claims,
            "verification_results": verification_results,
            "misrepresentations": misrepresentations,
            "summary": {
                "total_misrepresentations": len(misrepresentations),
                "misrepresentation_rate": f"{misrep_rate:.1%}",
                "severe": sum(1 for m in misrepresentations if m["severity"] == "severe"),
                "significant": sum(1 for m in misrepresentations if m["severity"] == "significant"),
                "minor": sum(1 for m in misrepresentations if m["severity"] == "minor"),
                "documentation": sum(1 for m in misrepresentations if m["severity"] == "documentation")
            }
        }
        
        # 保存报告
        report_path = os.path.join(self.audit_dir, f"{skill_name}_audit.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        report["report_path"] = report_path
        logger.info(f"Skill audit report generated: {report_path}")
        return report
    
    def _generate_remediation_plan(self, skill_name: str, 
                                   misrepresentations: List[Dict]) -> Dict:
        """生成整改计划"""
        plan = {
            "skill_name": skill_name,
            "generated_at": datetime.now().isoformat(),
            "actions": []
        }
        
        for misrep in misrepresentations:
            action = {
                "issue_type": misrep["type"],
                "severity": misrep["severity"],
                "claimed": misrep["claimed"],
                "action": self._get_remediation_action(misrep["type"])
            }
            plan["actions"].append(action)
        
        # 按严重度排序
        severity_order = {"severe": 0, "significant": 1, "documentation": 2, "minor": 3}
        plan["actions"].sort(key=lambda x: severity_order.get(x["severity"], 4))
        
        return plan
    
    def _get_remediation_action(self, issue_type: str) -> str:
        """获取整改建议"""
        actions = {
            "file_not_exists": "创建声称的文件，或更新声称移除该文件",
            "function_not_implemented": "实现声称的功能函数",
            "function_minimal_implementation": "完善函数实现，添加必要的逻辑和文档",
            "documentation_missing": "创建SKILL.md或README.md文档",
            "testing_missing": "创建测试文件或使用--test参数验证功能"
        }
        return actions.get(issue_type, "核实声称并修正差异")
    
    def _summarize_verification(self, verification_results: Dict) -> str:
        """汇总验证结果"""
        summaries = []
        
        if "file_exists" in verification_results:
            files = verification_results["file_exists"]
            exists_count = sum(1 for f in files if f["exists"])
            summaries.append(f"文件: {exists_count}/{len(files)}存在")
        
        if "function_complete" in verification_results:
            funcs = verification_results["function_complete"]
            found_count = sum(1 for f in funcs if f["found"])
            summaries.append(f"功能: {found_count}/{len(funcs)}实现")
        
        if "documented" in verification_results:
            doc = verification_results["documented"][0] if verification_results["documented"] else {}
            doc_status = "✓" if doc.get("documentation_found") else "✗"
            summaries.append(f"文档: {doc_status}")
        
        if "tested" in verification_results:
            test = verification_results["tested"][0] if verification_results["tested"] else {}
            test_status = "✓" if test.get("testing_found") else "✗"
            summaries.append(f"测试: {test_status}")
        
        return "; ".join(summaries)
    
    def _assess_severity(self, misrep_rate: float, misrepresentations: List[Dict]) -> str:
        """评估严重程度"""
        if misrep_rate >= 0.5:
            return "severe"
        elif any(m["severity"] == "significant" for m in misrepresentations):
            return "significant"
        elif misrep_rate > 0:
            return "minor"
        return "none"
    
    def _restore_state(self, state: Dict) -> None:
        """从检查点恢复状态"""
        if "audit_history" in state:
            self.audit_history = state["audit_history"]
    
    def estimate_cost(self, task: Task) -> Dict[str, int]:
        """估算Token和时间成本"""
        return {
            "tokens": 2500,
            "time_seconds": 35
        }
    
    def get_checkpoint_state(self) -> Dict[str, Any]:
        """获取检查点状态"""
        state = super().get_checkpoint_state()
        state["audit_history"] = self.audit_history
        return state
    
    def restore_from_checkpoint(self, state: Dict[str, Any]) -> None:
        """从检查点恢复"""
        super().restore_from_checkpoint(state)
        if "audit_history" in state:
            self.audit_history = state["audit_history"]
    
    def audit(self, task_id: Optional[str] = None) -> AuditRecord:
        """
        蓝军审计方法
        
        审计标准：
        1. 声称解析准确性
        2. 验证逻辑完整性
        3. 虚报判定合理性
        4. 整改建议可行性
        """
        audit = AuditRecord(
            task_id=task_id,
            auditor="blue_army_category3",
            audit_type="blue_army",
            criteria=[
                "claim_parsing_accuracy",
                "verification_completeness",
                "misrepresentation_judgment",
                "remediation_feasibility"
            ]
        )
        
        # 检查审计历史
        for tid, result in self.audit_history.items():
            audit_report = result.get("audit_report", {})
            
            # 检查虚报率计算
            summary = audit_report.get("summary", {})
            reported_rate = summary.get("misrepresentation_rate", "0%")
            
            # 验证虚报率格式
            if not isinstance(reported_rate, str) or not reported_rate.endswith("%"):
                audit.add_finding(
                    item=f"虚报率格式错误: {result.get('skill_name')}",
                    expected="百分比格式如'15.0%'",
                    actual=reported_rate,
                    severity="warning"
                )
            
            # 检查审计报告文件
            report_path = audit_report.get("report_path", "")
            if report_path and not os.path.exists(report_path):
                audit.add_finding(
                    item=f"审计报告文件不存在: {result.get('skill_name')}",
                    expected="报告文件存在",
                    actual="文件不存在",
                    severity="high"
                )
            
            # 检查是否有虚报但未记录
            misrepresentations = audit_report.get("misrepresentations", [])
            verification_results = audit_report.get("verification_results", {})
            
            # 简单验证：如果有验证失败但misrepresentations为空，可能漏报
            for category, results in verification_results.items():
                if category == "file_exists":
                    for r in results:
                        if not r.get("exists"):
                            # 检查是否已在misrepresentations中
                            if not any(m.get("claimed") == r.get("claimed_file") for m in misrepresentations):
                                audit.add_finding(
                                    item=f"可能漏报虚报: {r.get('claimed_file')}",
                                    expected="文件不存在应记录在misrepresentations",
                                    actual="未记录",
                                    severity="warning"
                                )
        
        # 决定审计结果
        critical_count = sum(1 for f in audit.findings if f["severity"] == "critical")
        
        audit.passed = critical_count == 0
        audit.severity = "critical" if critical_count > 0 else (
            "warning" if audit.findings else "info"
        )
        
        if critical_count > 0:
            audit.recommendations.append("立即修复关键问题")
        elif audit.findings:
            audit.recommendations.append("关注发现的警告问题")
        else:
            audit.recommendations.append("Skill虚报审计流程运行正常")
        
        logger.info(f"Category3 audit completed: {audit.passed}, findings={len(audit.findings)}")
        return audit


def register_handler(registry):
    """注册处理器到注册表"""
    registry.register_handler(Category3SkillHandler)
    logger.info("Category3SkillHandler registered")
