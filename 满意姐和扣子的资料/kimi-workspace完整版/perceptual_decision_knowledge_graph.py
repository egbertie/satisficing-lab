"""
---
KIA-CODE: 知识入库代码级闭环
Asset: perceptual_decision_knowledge_graph.py
Status: ✅ 代码级KIA完成
Date: 2026-04-15
Batch: OM-03 Python资产25份代码级KIA

KIA-Loop:
  - 接收清点: 2026-04-15
  - 轻量提取: 2026-04-15 (代码结构识别)
  - 查重去冗: 2026-04-15 (无重复代码)
  - Tier分级: T1 (核心项目资产)
  - 深度洞察: 2026-04-15 (功能定位确认)
  - 血液化: ✅ 完成 (五路图腾映射确认)
  - 归档锁定: 2026-04-15

功能定位:
  - 用途: 感知决策知识图谱
  - 关联: 知识管理
  - 维护者: 蓝军+满意姐

血液化映射:
  - 五路图腾关联: 司马贺-理性
  - 产品映射: 决策支持
  - 运营映射: 知识库

---
"""

#!/usr/bin/env python3
"""
perceptual_decision_knowledge_graph.py
感知力决策知识图谱 V1.0
基于《24感知力决策_从理论源头到商业实战的完整知识图谱》

功能:
- 结构化查询感知力决策的理论基础（信号检测理论、神经经济学、具身认知等）
- 输出从学术源头到商业实战的层级地图
- 生成持续学习与知识更新建议
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class PerceptualDecisionKnowledgeGraph(BaseComponent):
    """感知力决策知识图谱"""

    KNOWLEDGE_GRAPH = {
        "理论基础层": {
            "信号检测理论(SDT)": {
                "核心概念": ["敏感性(d')", "反应偏向(β)", "信号 vs 噪声"],
                "学术来源": "Green & Swets (1966)",
                "商业映射": "在不确定环境中区分有效信息与噪音",
            },
            "神经经济学": {
                "核心概念": ["价值编码", "风险评估", "跨期选择"],
                "学术来源": "Neuroeconomics Society, Glimcher (2003)",
                "商业映射": "理解决策者在利益与风险间的大脑加工机制",
            },
            "具身认知与躯体标记假说": {
                "核心概念": ["躯体状态影响决策", "直觉=躯体信号+经验模式"],
                "学术来源": "Damasio, Somatic Marker Hypothesis (1994)",
                "商业映射": "高压决策中的躯体反应可作为预警信号",
            },
            "双系统理论": {
                "核心概念": ["系统1(快思考)", "系统2(慢思考)"],
                "学术来源": "Kahneman (2011)",
                "商业映射": "左脑风控(系统2)+右脑直觉(系统1)的协同",
            },
        },
        "方法论层": {
            "五路图腾决策框架": {
                "构成": ["土/德", "火/顿悟", "水/观自在", "金/满意解", "木/仁"],
                "应用场景": "合伙人评估、战略迷茫期、文化重塑",
            },
            "QPMS引擎": {
                "构成": ["REPA模块", "DDM模型", "躯体信号接口"],
                "应用场景": "硬科技合伙人匹配的可操作化评估",
            },
            "72小时压力测试": {
                "构成": ["模拟谈判", "极限情境", "团队协作观察"],
                "应用场景": "在高压下暴露真实的合伙人兼容性",
            },
        },
        "商业实战层": {
            "决策陪跑服务": {
                "核心交付": "合伙人选择→冲突调解→战略共识→组织传承",
                "服务周期": "6-12个月",
            },
            "感知力训练营": {
                "核心交付": "躯体标记觉察+情绪调节+顿悟触发",
                "服务周期": "4周",
            },
            "知识更新机制": {
                "学术追踪": "Nature Neuroscience, Neuron, SJDM",
                "实践网络": "创业案例库+行业标杆访谈+失败案例反事实分析",
            },
        },
    }

    def __init__(self):
        super().__init__("perceptual_decision_knowledge_graph")

    def query(self, layer: str = None, concept: str = None) -> Dict[str, Any]:
        if layer and concept:
            return self.KNOWLEDGE_GRAPH.get(layer, {}).get(concept, {})
        if layer:
            return self.KNOWLEDGE_GRAPH.get(layer, {})
        return self.KNOWLEDGE_GRAPH

    def generate_report(self, focus_layer: str = None) -> str:
        content = self.query(layer=focus_layer)
        lines = [
            "# 感知力决策知识图谱报告",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**聚焦层级**: {focus_layer or '全层级'}",
            "",
            "## 图谱内容",
            "```json",
            json.dumps(content, ensure_ascii=False, indent=2),
            "```",
        ]
        report_path = Path(self.workspace) / "memory" / f"pd-knowledge-graph-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="感知力决策知识图谱")
    parser.add_argument("--layer", default="", help="聚焦层级（理论基础层/方法论层/商业实战层）")
    parser.add_argument("--report", action="store_true", help="生成知识图谱报告")
    args = parser.parse_args()

    kg = PerceptualDecisionKnowledgeGraph()
    path = kg.generate_report(focus_layer=args.layer or None)
    print(f"知识图谱报告已生成: {path}")


if __name__ == "__main__":
    main()
