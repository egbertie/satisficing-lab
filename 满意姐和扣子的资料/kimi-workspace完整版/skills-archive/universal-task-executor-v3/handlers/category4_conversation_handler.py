import sys
sys.path.insert(0, "/root/.openclaw/workspace/skills/universal-task-executor-v3")
"""
Universal Task Executor V3.0 - Category 4: 对话/反思整改处理器
处理对话内容的分析、反思生成和整改建议
"""

import os
import re
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from core.registry import TaskHandler
from core.structures import Task, TaskResult, TaskStatus, AuditRecord
from core.token_engine import TokenEngine

logger = logging.getLogger(__name__)


class Category4ConversationHandler(TaskHandler):
    """
    第4类处理器：对话/反思整改处理器
    
    职责：
    1. 分析对话内容中的问题和改进点
    2. 生成结构化反思报告
    3. 提取可执行的行动项
    4. 追踪整改执行情况
    
    反思维度：
    - 沟通效率（信息清晰度、理解准确性）
    - 任务执行（完成度、质量、及时性）
    - 问题识别（是否发现潜在问题）
    - 改进机会（是否有更好的解决方案）
    """
    
    handler_name = "category4_conversation_handler"
    supported_categories = ["category_4"]
    version = "3.0.0"
    
    # 反思类型
    REFLECTION_TYPES = {
        "efficiency": "效率反思 - 沟通和执行效率",
        "quality": "质量反思 - 输出质量和准确性",
        "learning": "学习反思 - 能力提升和知识积累",
        "relationship": "关系反思 - 协作和信任建立"
    }
    
    # 问题模式识别
    ISSUE_PATTERNS = {
        "misunderstanding": {
            "patterns": [
                r"我不是?这个意思",
                r"你可能没理解",
                r"我说的是.*不是",
                r"我的意思是",
                r"可能.*误解"
            ],
            "description": "理解偏差",
            "severity": "medium"
        },
        "incomplete": {
            "patterns": [
                r"还没完成",
                r"还差.*没做",
                r"需要.*补充",
                r"遗漏了",
                r"漏掉了"
            ],
            "description": "完成度不足",
            "severity": "high"
        },
        "quality_issue": {
            "patterns": [
                r"质量.*不够",
                r"需要.*改进",
                r"这个不行",
                r"重新.*做",
                r"不够好"
            ],
            "description": "质量问题",
            "severity": "high"
        },
        "delay": {
            "patterns": [
                r"延迟",
                r"延期",
                r"需要.*时间",
                r"来不及",
                r"还没开始"
            ],
            "description": "进度延迟",
            "severity": "medium"
        },
        "repetition": {
            "patterns": [
                r"又说.*一遍",
                r"重复.*次",
                r"同样的.*问题",
                r"又.*犯了"
            ],
            "description": "重复问题",
            "severity": "medium"
        }
    }
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.reflection_dir = self.config.get("reflection_dir", "memory/reflections/")
        self.remediation_dir = self.config.get("remediation_dir", "memory/conversation_remediation/")
        self.reflection_history: Dict[str, Dict] = {}
        
        os.makedirs(self.reflection_dir, exist_ok=True)
        os.makedirs(self.remediation_dir, exist_ok=True)
        
        logger.info(f"Category4ConversationHandler initialized: dir={self.reflection_dir}")
    
    def validate(self, task: Task) -> bool:
        """验证对话整改任务数据"""
        if not super().validate(task):
            return False
        
        data = task.data
        
        # 检查是否有对话内容
        if "conversation_content" not in data and "reflection_topic" not in data:
            logger.error("Task validation failed: missing conversation_content or reflection_topic")
            return False
        
        return True
    
    def execute(self, task: Task, checkpoint_state: Optional[Dict] = None) -> TaskResult:
        """执行对话/反思整改"""
        start_time = datetime.now()
        task_id = task.task_id
        
        if checkpoint_state:
            self._restore_state(checkpoint_state)
        
        try:
            data = task.data
            conversation_content = data.get("conversation_content", "")
            reflection_topic = data.get("reflection_topic", "对话反思")
            reflection_type = data.get("reflection_type", "efficiency")
            context = data.get("context", {})
            
            # 1. 分析对话内容，识别问题
            identified_issues = self._analyze_conversation(conversation_content)
            
            # 2. 生成反思报告
            reflection_report = self._generate_reflection(
                task_id, reflection_topic, reflection_type,
                conversation_content, identified_issues, context
            )
            
            # 3. 提取行动项
            action_items = self._extract_action_items(identified_issues, reflection_report)
            
            # 4. 生成整改计划
            remediation_plan = self._generate_remediation_plan(
                task_id, reflection_topic, identified_issues, action_items
            )
            
            # 5. 保存反思记录
            self.reflection_history[task_id] = {
                "topic": reflection_topic,
                "reflection_type": reflection_type,
                "issues_identified": len(identified_issues),
                "action_items": len(action_items),
                "report_path": reflection_report.get("report_path"),
                "timestamp": datetime.now().isoformat()
            }
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            return TaskResult(
                task_id=task_id,
                status="completed",
                output={
                    "reflection_topic": reflection_topic,
                    "reflection_type": reflection_type,
                    "issues_identified": len(identified_issues),
                    "identified_issues": identified_issues,
                    "action_items_count": len(action_items),
                    "action_items": action_items,
                    "reflection_report_path": reflection_report.get("report_path"),
                    "remediation_plan_path": remediation_plan.get("plan_path"),
                    "key_insights": reflection_report.get("key_insights", []),
                    "improvement_areas": self._summarize_improvements(identified_issues)
                },
                token_consumed=2000,
                time_elapsed=elapsed,
                audit_required=True
            )
            
        except Exception as e:
            logger.error(f"Conversation reflection failed: {task_id}, error={e}")
            elapsed = (datetime.now() - start_time).total_seconds()
            return TaskResult(
                task_id=task_id,
                status="failed",
                output={},
                token_consumed=1000,
                time_elapsed=elapsed,
                error=str(e)
            )
    
    def _analyze_conversation(self, content: str) -> List[Dict]:
        """分析对话内容，识别问题"""
        issues = []
        
        for issue_type, config in self.ISSUE_PATTERNS.items():
            for pattern in config["patterns"]:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # 获取上下文
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 50)
                    context = content[start:end]
                    
                    issue = {
                        "type": issue_type,
                        "description": config["description"],
                        "severity": config["severity"],
                        "matched_text": match.group(),
                        "context": context,
                        "position": match.start()
                    }
                    
                    # 避免重复
                    if not any(i["matched_text"] == issue["matched_text"] for i in issues):
                        issues.append(issue)
        
        # 按位置排序
        issues.sort(key=lambda x: x["position"])
        
        return issues
    
    def _generate_reflection(self, task_id: str, topic: str, reflection_type: str,
                            content: str, issues: List[Dict], context: Dict) -> Dict:
        """生成反思报告"""
        
        # 分析问题类型分布
        issue_distribution = {}
        for issue in issues:
            t = issue["type"]
            issue_distribution[t] = issue_distribution.get(t, 0) + 1
        
        # 生成关键洞察
        key_insights = []
        
        if "misunderstanding" in issue_distribution:
            key_insights.append({
                "insight": "沟通中存在理解偏差",
                "recommendation": "加强确认机制，使用复述验证理解",
                "priority": "high"
            })
        
        if "incomplete" in issue_distribution or "quality_issue" in issue_distribution:
            key_insights.append({
                "insight": "输出质量或完成度需要提升",
                "recommendation": "建立自检清单，执行三次检查法",
                "priority": "high"
            })
        
        if "delay" in issue_distribution:
            key_insights.append({
                "insight": "存在进度延迟问题",
                "recommendation": "改进时间估算，设置里程碑检查点",
                "priority": "medium"
            })
        
        if "repetition" in issue_distribution:
            key_insights.append({
                "insight": "存在重复出现的问题",
                "recommendation": "建立防复发机制，固化经验教训",
                "priority": "medium"
            })
        
        if not issues:
            key_insights.append({
                "insight": "对话质量良好，无明显问题",
                "recommendation": "继续保持，关注持续改进",
                "priority": "low"
            })
        
        # 生成报告
        report = {
            "task_id": task_id,
            "topic": topic,
            "reflection_type": reflection_type,
            "reflection_time": datetime.now().isoformat(),
            "context": context,
            "issue_analysis": {
                "total_issues": len(issues),
                "distribution": issue_distribution,
                "by_severity": {
                    "high": sum(1 for i in issues if i["severity"] == "high"),
                    "medium": sum(1 for i in issues if i["severity"] == "medium"),
                    "low": sum(1 for i in issues if i["severity"] == "low")
                }
            },
            "issues_detail": issues,
            "key_insights": key_insights,
            "conversation_excerpt": content[:500] if len(content) > 500 else content
        }
        
        # 保存报告
        report_path = os.path.join(self.reflection_dir, f"{task_id}_reflection.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        report["report_path"] = report_path
        logger.info(f"Reflection report generated: {report_path}")
        return report
    
    def _extract_action_items(self, issues: List[Dict], reflection_report: Dict) -> List[Dict]:
        """提取行动项"""
        action_items = []
        
        # 从洞察生成行动项
        for insight in reflection_report.get("key_insights", []):
            action = {
                "description": insight["recommendation"],
                "priority": insight["priority"],
                "category": "improvement",
                "source": "insight",
                "due_date": None,
                "status": "pending"
            }
            action_items.append(action)
        
        # 从问题生成行动项
        for issue in issues:
            if issue["severity"] == "high":
                action = {
                    "description": f"解决{issue['description']}: {issue['matched_text']}",
                    "priority": "high",
                    "category": "fix",
                    "source": f"issue:{issue['type']}",
                    "due_date": "immediate",
                    "status": "pending"
                }
                action_items.append(action)
        
        # 去重
        seen = set()
        unique_actions = []
        for action in action_items:
            key = action["description"]
            if key not in seen:
                seen.add(key)
                unique_actions.append(action)
        
        # 按优先级排序
        priority_order = {"high": 0, "medium": 1, "low": 2}
        unique_actions.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        return unique_actions
    
    def _generate_remediation_plan(self, task_id: str, topic: str,
                                   issues: List[Dict], action_items: List[Dict]) -> Dict:
        """生成整改计划"""
        plan = {
            "task_id": task_id,
            "topic": topic,
            "created_at": datetime.now().isoformat(),
            "phases": []
        }
        
        # 立即执行（P0）
        immediate_actions = [a for a in action_items if a.get("due_date") == "immediate"]
        if immediate_actions:
            plan["phases"].append({
                "name": "立即整改",
                "priority": "P0",
                "actions": immediate_actions,
                "timeframe": "24小时内"
            })
        
        # 高优先级改进（P1）
        high_priority = [a for a in action_items 
                        if a.get("priority") == "high" and a.get("due_date") != "immediate"]
        if high_priority:
            plan["phases"].append({
                "name": "高优先级改进",
                "priority": "P1",
                "actions": high_priority,
                "timeframe": "本周内"
            })
        
        # 中优先级改进（P2）
        medium_priority = [a for a in action_items if a.get("priority") == "medium"]
        if medium_priority:
            plan["phases"].append({
                "name": "持续改进",
                "priority": "P2",
                "actions": medium_priority,
                "timeframe": "本月内"
            })
        
        # 低优先级改进（P3）
        low_priority = [a for a in action_items if a.get("priority") == "low"]
        if low_priority:
            plan["phases"].append({
                "name": "长期优化",
                "priority": "P3",
                "actions": low_priority,
                "timeframe": "长期"
            })
        
        # 保存计划
        plan_path = os.path.join(self.remediation_dir, f"{task_id}_remediation_plan.json")
        with open(plan_path, "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        
        plan["plan_path"] = plan_path
        logger.info(f"Remediation plan generated: {plan_path}")
        return plan
    
    def _summarize_improvements(self, issues: List[Dict]) -> List[str]:
        """汇总改进领域"""
        if not issues:
            return ["整体表现良好"]
        
        areas = []
        issue_types = set(i["type"] for i in issues)
        
        type_descriptions = {
            "misunderstanding": "沟通清晰度",
            "incomplete": "任务完成度",
            "quality_issue": "输出质量",
            "delay": "时间管理",
            "repetition": "防复发机制"
        }
        
        for t in issue_types:
            if t in type_descriptions:
                areas.append(type_descriptions[t])
        
        return areas
    
    def _restore_state(self, state: Dict) -> None:
        """从检查点恢复状态"""
        if "reflection_history" in state:
            self.reflection_history = state["reflection_history"]
    
    def estimate_cost(self, task: Task) -> Dict[str, int]:
        """估算Token和时间成本"""
        content_size = len(task.data.get("conversation_content", ""))
        # 根据内容大小调整估算
        base_tokens = 2000
        size_factor = content_size // 1000
        
        return {
            "tokens": base_tokens + size_factor * 200,
            "time_seconds": 20 + size_factor * 2
        }
    
    def get_checkpoint_state(self) -> Dict[str, Any]:
        """获取检查点状态"""
        state = super().get_checkpoint_state()
        state["reflection_history"] = self.reflection_history
        return state
    
    def restore_from_checkpoint(self, state: Dict[str, Any]) -> None:
        """从检查点恢复"""
        super().restore_from_checkpoint(state)
        if "reflection_history" in state:
            self.reflection_history = state["reflection_history"]
    
    def audit(self, task_id: Optional[str] = None) -> AuditRecord:
        """
        蓝军审计方法
        
        审计标准：
        1. 问题识别完整性
        2. 洞察生成质量
        3. 行动项可执行性
        4. 整改计划合理性
        """
        audit = AuditRecord(
            task_id=task_id,
            auditor="blue_army_category4",
            audit_type="blue_army",
            criteria=[
                "issue_identification",
                "insight_quality",
                "action_feasibility",
                "plan_rationality"
            ]
        )
        
        # 检查反思历史
        for tid, result in self.reflection_history.items():
            # 检查反思报告是否存在
            report_path = result.get("report_path", "")
            if report_path and not os.path.exists(report_path):
                audit.add_finding(
                    item=f"反思报告文件不存在: {result.get('topic')}",
                    expected="报告文件存在",
                    actual="文件不存在",
                    severity="high"
                )
            
            # 检查问题识别是否合理
            issues_count = result.get("issues_identified", 0)
            action_items_count = result.get("action_items", 0)
            
            if issues_count > 0 and action_items_count == 0:
                audit.add_finding(
                    item=f"有问题但无行动项: {result.get('topic')}",
                    expected="发现问题应有对应行动项",
                    actual="有{}个问题但0个行动项".format(issues_count),
                    severity="warning"
                )
            
            # 检查是否有高严重度问题但未生成高优先级行动
            # 这个检查需要读取实际报告文件
            if report_path and os.path.exists(report_path):
                try:
                    with open(report_path, "r", encoding="utf-8") as f:
                        report = json.load(f)
                    
                    issue_analysis = report.get("issue_analysis", {})
                    high_severity_count = issue_analysis.get("by_severity", {}).get("high", 0)
                    
                    # 如果有高严重度问题，应该至少有一个高优先级行动
                    key_insights = report.get("key_insights", [])
                    high_priority_insights = sum(1 for i in key_insights if i.get("priority") == "high")
                    
                    if high_severity_count > 0 and high_priority_insights == 0:
                        audit.add_finding(
                            item=f"高严重度问题缺少高优先级洞察: {result.get('topic')}",
                            expected="高严重度问题应有高优先级洞察",
                            actual=f"{high_severity_count}个高严重度问题但0个高优先级洞察",
                            severity="warning"
                        )
                except Exception as e:
                    audit.add_finding(
                        item=f"无法读取反思报告: {result.get('topic')}",
                        expected="报告可读取",
                        actual=str(e),
                        severity="medium"
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
            audit.recommendations.append("对话反思流程运行正常")
        
        logger.info(f"Category4 audit completed: {audit.passed}, findings={len(audit.findings)}")
        return audit


def register_handler(registry):
    """注册处理器到注册表"""
    registry.register_handler(Category4ConversationHandler)
    logger.info("Category4ConversationHandler registered")
