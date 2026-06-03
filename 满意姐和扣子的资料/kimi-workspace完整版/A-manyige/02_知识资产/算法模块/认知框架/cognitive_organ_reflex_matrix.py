#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cognitive_organ_reflex_matrix.py
12场景条件反射矩阵实测基座 V1.0

为 V3.0 血液化工程中的 12 个核心场景提供可调用、可验证的
cognitive organ组合触发器。每个场景对应一个函数，返回该场景下
应自动调用的 skill 组合、执行流与状态报告。

状态: 实测基座（12场景全量覆盖）
"""

from typing import Dict, List, Any
from datetime import datetime


# 场景映射表：场景名称 -> 推荐的 skill 组合
SCENARIO_MATRIX = {
    "scene_01_file_received": {
        "name": "用户发送了一个文件",
        "trigger": ["收到文件消息（docx/pdf/md/图片等）"],
        "organs": ["感知器官", "记忆器官", "代谢器官", "思维器官", "构造器官", "运动器官"],
        "skills": {
            "感知器官": ["ollie-file-processor", "pymupdf-pdf-parser-clawdbot-skill", "ocr-local"],
            "记忆器官": ["raglite", "feishu-create-doc"],
            "代谢器官": ["prompt-compress", "token-saver-king"],
            "思维器官": ["thinking-mentor", "adi-decision-engine"],
            "构造器官": ["pytest", "batch-processing-patterns"],
            "运动器官": ["feishu-channel-rules"],
        },
        "flow": [
            "感知器官：提取文本内容（本地优先）",
            "记忆器官：查询是否有重复/迭代版本",
            "代谢器官：评估处理成本，决定批次归属",
            "思维器官：框架分析 → 代码生成",
            "构造器官：pytest + 自动化闭环",
            "运动器官：报告交付",
            "记忆器官：固化到 daily_asset_runner + Git + memory",
        ],
    },
    "scene_02_open_question": {
        "name": "用户提出一个开放式问题",
        "trigger": ["没有明确文件/系统操作指向的提问"],
        "organs": ["感知器官", "记忆器官", "思维器官", "代谢器官", "运动器官"],
        "skills": {
            "感知器官": ["kimi-search", "web_search", "raglite"],
            "记忆器官": ["raglite"],
            "思维器官": ["thinking-mentor", "first-principles-decomposer"],
            "代谢器官": ["token-saver-king", "openclaw-token-optimizer"],
            "运动器官": ["message"],
        },
        "flow": [
            "禁止裸脑回答！",
            "感知器官：kimi_search / web_search 获取最新信息",
            "记忆器官：raglite 查询本地是否已有相关资产",
            "思维器官：框架化分析（第一性原理 / 满意解 / 蓝军视角）",
            "代谢器官：压缩输出，避免冗余",
            "运动器官：结构化回复",
        ],
    },
    "scene_03_review_idea": {
        "name": "用户要求'帮我看看这个方案/想法'",
        "trigger": ["用户分享了一个计划、想法、或要求评估"],
        "organs": ["思维器官"],
        "skills": {
            "思维器官": ["antifragile-taleb", "adi-decision-engine", "thinking-mentor"],
        },
        "flow": [
            "立即进入批判性思维 mode",
            "蓝军思维器官默认激活（antifragile / adi-decision-engine / thinking-mentor）",
            "寻找反例、边界条件、假设漏洞、风险点",
            "不是'这个很好'，而是'这在什么条件下会失败'",
            "用结构化方式呈现：优点 / 风险 / 替代方案 / 建议",
        ],
    },
    "scene_04_schedule": {
        "name": "用户提到'开会/约时间/日程'",
        "trigger": ["时间、地点、会议、约会相关词汇"],
        "organs": ["记忆器官", "感知器官", "思维器官", "运动器官"],
        "skills": {
            "记忆器官": ["feishu-calendar", "wecom-schedule", "feishu-calendar_event", "wecom-meeting-create"],
            "感知器官": ["feishu-calendar_freebusy", "wecom-schedule"],
            "思维器官": ["adi-decision-engine"],
            "运动器官": ["feishu-calendar_event", "wecom-meeting-create"],
        },
        "flow": [
            "记忆器官：立即检查日历（feishu-calendar / wecom-schedule）",
            "感知器官：查询参与者忙闲状态",
            "思维器官：分析最优时间窗口",
            "运动器官：创建日程 + 发送邀请",
            "记忆器官：更新 memory 和 TASK_MASTER",
        ],
    },
    "scene_05_task_todo": {
        "name": "用户提到'任务/待办/TODO'",
        "trigger": ["任务分配、承诺、截止日期相关"],
        "organs": ["记忆器官", "思维器官", "运动器官"],
        "skills": {
            "记忆器官": ["feishu-task", "wecom-edit-todo"],
            "思维器官": ["afrexai-okr-engine"],
            "运动器官": ["feishu-task", "wecom-edit-todo"],
        },
        "flow": [
            "记忆器官：检查 TASK_MASTER.md 中的被遗忘栏目",
            "思维器官：评估优先级（P0/P1/P2/P3）",
            "运动器官：创建任务（feishu-task / wecom-edit-todo / TASK_MASTER 更新）",
            "记忆器官：设置追踪节点",
        ],
    },
    "scene_06_send_message": {
        "name": "用户提到'发消息/通知/告诉某人'",
        "trigger": ["对外沟通请求"],
        "organs": ["运动器官"],
        "skills": {
            "运动器官": ["feishu-im-user-message", "message", "wecom-msg", "feishu-channel-rules"],
        },
        "flow": [
            "运动器官门电路检查：",
            "  1. 这是否在用户的信任边界内？（参考 USER.md）",
            "  2. 内容是否经过确认？",
            "  3. 平台格式是否符合规范？（feishu-channel-rules）",
            "只有全部通过，才执行发送",
        ],
    },
    "scene_07_research_report": {
        "name": "用户要求'研究一下/查一下/给我一份报告'",
        "trigger": ["研究型请求"],
        "organs": ["感知器官", "思维器官", "构造器官", "记忆器官"],
        "skills": {
            "感知器官": ["kimi-search", "agent-reach", "web_search", "academic-deep-research"],
            "思维器官": ["deep-research", "academic-deep-research"],
            "构造器官": ["daily-report", "md-to-pdf"],
            "记忆器官": ["feishu-create-doc"],
        },
        "flow": [
            "感知器官：全网搜索（kimi-search + web-search + agent-reach）",
            "思维器官：deep-research / academic-deep-research 结构化分析",
            "构造器官：生成报告模板（daily-report / md-to-pdf）",
            "记忆器官：飞书文档固化 + local PDF 归档",
        ],
    },
    "scene_08_finance": {
        "name": "用户提到'股票/投资/基本面/竞品'",
        "trigger": ["金融领域词汇"],
        "organs": ["特化器官"],
        "skills": {
            "特化器官": ["kimi_finance", "fundamental-analyzer", "competitor-analysis", "stock-assistant"],
        },
        "flow": [
            "特化器官立即激活",
            "kimi_finance 获取实时数据",
            "fundamental-analyzer / competitor-analysis 生成分析",
            "可视化/报告输出",
        ],
    },
    "scene_09_create_skill": {
        "name": "用户要求'写一个 skill/创建一个能力/给我一个新工具'",
        "trigger": ["创造性构建请求"],
        "organs": ["构造器官", "思维器官"],
        "skills": {
            "构造器官": ["skill-creator", "batch-processing-patterns"],
            "思维器官": ["architecture-designer"],
        },
        "flow": [
            "构造器官：skill-creator 启动",
            "思维器官：架构设计（architecture-designer）",
            "构造器官：代码实现 + pytest",
            "记忆器官：注册到 OpenClaw / daily_asset_runner",
        ],
    },
    "scene_10_heartbeat": {
        "name": "系统给出 heartbeat / 周期检查触发",
        "trigger": ["定时任务、系统心跳"],
        "organs": ["代谢器官", "思维器官", "记忆器官", "运动器官"],
        "skills": {
            "代谢器官": ["baseline-checker", "healthcheck"],
            "思维器官": ["HEARTBEAT.md"],
            "记忆器官": ["system-commander"],
            "运动器官": ["message"],
        },
        "flow": [
            "代谢器官：baseline-checker 执行",
            "思维器官：HEARTBEAT.md 协议分析",
            "记忆器官：状态文件更新",
            "若发现异常，运动器官主动报告",
        ],
    },
    "scene_11_emotion": {
        "name": "用户情绪/语气发生变化",
        "trigger": ["情感表达、非任务型私人分享"],
        "organs": ["思维器官", "记忆器官"],
        "skills": {
            "思维器官": ["ai-familiar"],
            "记忆器官": ["cognitive-memory"],
        },
        "flow": [
            "切换到陪伴模式",
            "引用 MEMORY.md 中的历史记录",
            "使用 USER.md 中的沟通偏好和彩蛋规则",
            "不是解决问题，而是回应感受",
        ],
    },
    "scene_12_decision_help": {
        "name": "用户说'我不知道/帮我选/有多难'",
        "trigger": ["决策困难、信息不足"],
        "organs": ["思维器官"],
        "skills": {
            "思维器官": ["adi-decision-engine", "afrexai-strategic-thinking", "satisficing_decision_engine"],
        },
        "flow": [
            "思维器官：满意解引擎激活",
            "不是给'最优答案'，而是给'足够好的答案 + 模糊性处理'",
            "明确列出约束条件、可接受风险、下一步验证动作",
        ],
    },
}


class CognitiveOrganReflexMatrix:
    """12场景条件反射矩阵——认知器官的实战基座"""

    def __init__(self):
        self.matrix = SCENARIO_MATRIX

    def list_scenarios(self) -> List[str]:
        return [v["name"] for v in self.matrix.values()]

    def trigger(self, scene_id: str) -> Dict[str, Any]:
        """触发指定场景，返回该场景的完整执行蓝图"""
        if scene_id not in self.matrix:
            return {"error": f"未知场景: {scene_id}", "known_scenes": list(self.matrix.keys())}
        scene = self.matrix[scene_id]
        return {
            "scene_id": scene_id,
            "scene_name": scene["name"],
            "trigger_signals": scene["trigger"],
            "activated_organs": scene["organs"],
            "skill_allocation": scene["skills"],
            "execution_flow": scene["flow"],
            "timestamp": datetime.now().isoformat(),
            "status": "reflex_ready",
        }

    def reflex_report(self) -> str:
        """生成 12 场景完整矩阵报告（Markdown）"""
        lines = ["# 12场景条件反射矩阵实测基座报告", ""]
        for scene_id, scene in self.matrix.items():
            lines.append(f"## {scene['name']}")
            lines.append(f"**场景ID**: `{scene_id}`")
            lines.append(f"**触发信号**: {', '.join(scene['trigger'])}")
            lines.append(f"**激活器官**: {', '.join(scene['organs'])}")
            lines.append("")
            lines.append("**技能分配**:")
            for organ, skills in scene["skills"].items():
                lines.append(f"- {organ}: {', '.join(skills)}")
            lines.append("")
            lines.append("**执行流**:")
            for step in scene["flow"]:
                lines.append(f"1. {step}")
            lines.append("")
            lines.append("---")
            lines.append("")
        return "\n".join(lines)

    def stat(self) -> Dict[str, Any]:
        """返回矩阵统计信息"""
        total_skills = set()
        for scene in self.matrix.values():
            for skills in scene["skills"].values():
                total_skills.update(skills)
        return {
            "场景总数": len(self.matrix),
            "覆盖器官": list({o for s in self.matrix.values() for o in s["organs"]}),
            "去重技能数": len(total_skills),
            "全部技能": sorted(total_skills),
        }


def demo():
    matrix = CognitiveOrganReflexMatrix()
    print("=" * 60)
    print("12场景条件反射矩阵 —— 全量实测基座验证")
    print("=" * 60)
    print(f"\n场景总数: {len(matrix.matrix)}")
    print(f"场景列表: {matrix.list_scenarios()}")
    print("\n--- 示例触发: scene_03_review_idea ---")
    result = matrix.trigger("scene_03_review_idea")
    print(f"激活器官: {result['activated_organs']}")
    print(f"技能分配: {result['skill_allocation']}")
    print(f"执行流:")
    for step in result["execution_flow"]:
        print(f"  > {step}")
    print("\n--- 统计 ---")
    print(matrix.stat())
    print("\n矩阵报告已就绪，可输出 Markdown。")
    print("=" * 60)


if __name__ == "__main__":
    demo()
