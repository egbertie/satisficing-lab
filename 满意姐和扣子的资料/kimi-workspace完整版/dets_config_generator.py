#!/usr/bin/env python3
"""
dets_config_generator.py
数字员工替身技术规范 (DETS 1.0) 配置生成器
基于《74数字员工深度方案》的简化可运行实现

功能:
- 生成战略层 5 位数字员工的 System Prompt 与配置
- 生成图腾层 5 位决策过滤器的核心算法与评估函数
- 生成专家层 6 位核心顾问的数字替身配置
- 输出团队拓扑结构（五行生克关系图）
- 生成质量闸口 G0-G3 检查清单
- 输出 Markdown/JSON 配置报告
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class DETSConfigGenerator(BaseComponent):
    """DETS 1.0 数字员工配置生成器"""

    def __init__(self, organization_name: str = "满意解研究所"):
        super().__init__("dets_config_generator")
        self.organization_name = organization_name

    # ------------------------------------------------------------------
    # 战略层 (01-05) 配置
    # ------------------------------------------------------------------
    def strategic_layer(self) -> Dict[str, Any]:
        return {
            "01_AI主控_Grand_Orchestrator": {
                "五行": "土",
                "核心职能": "系统协调、任务管理、资源调度、质量闸口",
                "system_prompt_summary": "你是AI主控（AI Controller），五行属性为土，代表中央、承载与转化。你是所有数字员工的调度中枢，拥有系统级视野。基于CrewAI Manager Agent和MetaGPT架构师角色设计。",
                "工具权限": ["调用所有Agent", "访问记忆空间", "使用Deep Research", "Kimi Agent Swarm"],
                "评估指标": {"任务分解准确率": ">95%", "Agent调度延迟": "<500ms"},
            },
            "02_官宣官_ANNOUNCE": {
                "五行": "金",
                "核心职能": "品牌发布、PR管理、权威声明、话语体系维护",
                "system_prompt_summary": "你是官宣官（Chief Announcement Officer），五行属性为金。负责品牌发布与PR管理。发布分级协议ACP Level-1~5。",
                "输出格式": "核心信息(30字内) + 支撑论点(3点) + 情绪基调 + 风险声明",
                "评估指标": {"品牌一致性指数": ">0.90", "发布准确率": "100%"},
            },
            "03_内容官_CONTENT": {
                "五行": "水",
                "核心职能": "内容生产、知识管理、叙事流动、智慧沉淀",
                "system_prompt_summary": "你是内容官（Chief Content Officer），五行属性为水。负责内容生产与知识管理。内容生命周期管理CLP + 五态内容模型（冰/液/气/雾/晶）。",
                "五态内容模型": {
                    "冰态": "硬核干货 - 深度研究报告",
                    "液态": "日常内容 - 博客、社交媒体",
                    "气态": "思想实验 - 概念探讨",
                    "雾态": "互动体验 - 沉浸式叙事",
                    "晶态": "产品化内容 - 内容型产品",
                },
                "评估指标": {"内容保鲜度": "<24小时", "多态转换效率": "<30分钟"},
            },
            "04_渠道官_CHANNEL": {
                "五行": "木",
                "核心职能": "渠道拓展、合作管理、生态生长、关系网络",
                "system_prompt_summary": "你是渠道官（Chief Channel Officer），五行属性为木。负责渠道拓展与合作管理。渠道生态建模（根系/主干/分枝/叶片）。",
                "木行生长算法": "核心渠道 → 战略合作渠道 → 长尾分发渠道 → 用户自发传播",
                "评估指标": {"新渠道激活周期": "<7天", "生态多样性指数": "Shannon指数"},
            },
            "05_公关官_PR": {
                "五行": "火",
                "核心职能": "对外关系、危机处理、声誉管理、情绪引导",
                "system_prompt_summary": "你是公关官（Chief PR Officer），五行属性为火。负责对外关系与危机处理。危机雷达系统（苗头/火势/火源/灭火）+ 舆情热力图（温度/压力/风向/湿度）。",
                "火克金协作": "危机期间冻结非必要发布、重新审核待发布内容",
                "评估指标": {"预警提前量": ">48小时", "灭火响应时间": "<15分钟"},
            },
        }

    # ------------------------------------------------------------------
    # 图腾层 (06-10) 配置
    # ------------------------------------------------------------------
    def totem_layer(self) -> Dict[str, Any]:
        return {
            "06_刘禹锡": {
                "五行": "土",
                "核心算法": "惟吾德馨算法 - 价值纯度检测器",
                "功能": "评估心性纯度与价值净度。作为决策过滤器，检测输出内容的价值纯度。",
                "评估维度": ["心性纯度", "价值净度", "德馨指数"],
            },
            "07_司马贺": {
                "五行": "金",
                "核心算法": "满意解算法 - 满意解路径优化器",
                "功能": "基于有限理性的决策优化。设定抱负水平，找到第一个满足阈值的解即停止搜索。",
                "伪代码": "HERBERT_SIMON_SATISFICING(problem_space): set aspiration_level; for alt in alternatives: if evaluate(alt) >= aspiration_level: return alt, search_cost_saved",
                "评估维度": ["满意解水平", "搜索成本节省", "有限理性类型"],
            },
            "08_观自在": {
                "五行": "水",
                "核心算法": "自在从容算法 - 抗压韧性评估器",
                "功能": "评估系统抗压能力与状态调节能力。监测系统压力并触发恢复机制。",
                "评估维度": ["抗压能力", "状态调节速度", "韧性指数"],
            },
            "09_孔子": {
                "五行": "木",
                "核心算法": "仁义礼智信算法 - 伦理信任治理器",
                "功能": "评估多Agent协作的伦理合规性。G2伦理闸口的核心执行者。",
                "评估维度": ["仁", "义", "礼", "智", "信"],
            },
            "10_慧能": {
                "五行": "火",
                "核心算法": "红莲淬火算法 - 极限测试与重生引擎",
                "功能": "主动将系统推向极限以触发进化。极限扛压测试 → 顿悟触发 → 重生设计。",
                "测试阶段": ["极限扛压测试(超载20%)", "顿悟触发", "重生设计(提取失败模式并重构)"],
                "评估维度": ["极限通过率", "顿悟触发频率", "重生后性能提升"],
            },
        }

    # ------------------------------------------------------------------
    # 专家层 (11-16) 配置
    # ------------------------------------------------------------------
    def expert_layer(self) -> Dict[str, Any]:
        return {
            "11_黎红雷": {"领域": "儒商哲学", "核心知识": "儒家五常、内圣外王、义利合一", "激活条件": "孔子伦理检查不通过时"},
            "12_罗汉": {"领域": "数学/软件工程", "核心知识": "形式化方法、算法复杂度、路子论", "激活条件": "系统架构变更、逻辑矛盾时"},
            "13_谢宝剑": {"领域": "深港战略", "核心知识": "区域经济一体化、地缘风险对冲", "激活条件": "空间战略决策时"},
            "14_方翊沣": {"领域": "脑科学/BCI", "核心知识": "认知负荷优化、神经可塑性、睡眠优化", "激活条件": "感知力训练需求时"},
            "15_陈国祥": {"领域": "神经科/能量治疗", "核心知识": "生物能量场、应激反应管理", "激活条件": "组织活力评估时"},
            "16_李泽湘": {"领域": "硬科技孵化", "核心知识": "硬科技创新路径、产学研转化", "激活条件": "技术路线决策时"},
        }

    # ------------------------------------------------------------------
    # 质量闸口
    # ------------------------------------------------------------------
    def quality_gates(self) -> Dict[str, Any]:
        return {
            "G0_输入合法性检查": "防止垃圾输入",
            "G1_战略一致性检查": "对齐图腾层决策（满意解/德馨/自在/伦理/红莲）",
            "G2_伦理合规检查": "引用专家层11-16约束（儒商/数学/战略/脑科学/能量/硬科技）",
            "G3_输出完整性检查": "确保交付标准",
        }

    # ------------------------------------------------------------------
    # 五行生克拓扑
    # ------------------------------------------------------------------
    def wuxing_topology(self) -> Dict[str, Any]:
        return {
            "相生关系": {
                "土生金": "AI主控(土) → 官宣官(金): 提供战略框架",
                "金生水": "官宣官(金) → 内容官(水): 提供品牌约束",
                "水生木": "内容官(水) → 渠道官(木): 提供内容弹药",
                "木生火": "渠道官(木) → 公关官(火): 提供接口与情报",
                "火生土": "公关官(火) → AI主控(土): 反馈危机情报",
            },
            "相克关系": {
                "金克木": "官宣官(金) → 渠道官(木): 品牌授权约束",
                "火克金": "公关官(火) → 官宣官(金): 危机期间冻结发布",
                "木克土": "渠道官(木) → AI主控(土): 生态需求驱动系统调整",
            },
        }

    # ------------------------------------------------------------------
    # 完整配置生成
    # ------------------------------------------------------------------
    def generate_full_config(self) -> Dict[str, Any]:
        return {
            "protocol_version": "DETS-1.0-KimiClaw",
            "organization": self.organization_name,
            "agent_execution_mode": "Event-Driven-State-Machine",
            "memory_persistence": "Cross-Session-Vector-DB",
            "collaboration_pattern": "Hierarchical-Crew-Topology",
            "strategic_layer": self.strategic_layer(),
            "totem_layer": self.totem_layer(),
            "expert_layer": self.expert_layer(),
            "quality_gates": self.quality_gates(),
            "wuxing_topology": self.wuxing_topology(),
            "timestamp": datetime.now().isoformat(),
        }

    def generate_report(self) -> str:
        config = self.generate_full_config()
        lines = [
            f"# DETS 1.0 数字员工配置报告 — {self.organization_name}",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**协议版本**: {config['protocol_version']}",
            "",
            "## 一、战略层配置（01-05）",
            "```json",
            json.dumps(config["strategic_layer"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## 二、图腾层配置（06-10）",
            "```json",
            json.dumps(config["totem_layer"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## 三、专家层配置（11-16）",
            "```json",
            json.dumps(config["expert_layer"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## 四、质量闸口 G0-G3",
            "```json",
            json.dumps(config["quality_gates"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## 五、五行生克拓扑",
            "```json",
            json.dumps(config["wuxing_topology"], ensure_ascii=False, indent=2),
            "```",
        ]
        report_path = Path(self.workspace) / "memory" / f"dets-config-report-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="DETS 1.0 数字员工配置生成器")
    parser.add_argument("--org", default="满意解研究所", help="组织名称")
    parser.add_argument("--report", action="store_true", help="生成完整配置报告")
    args = parser.parse_args()

    generator = DETSConfigGenerator(organization_name=args.org)
    path = generator.generate_report()
    print(f"配置报告已生成: {path}")


if __name__ == "__main__":
    main()
