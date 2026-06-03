"""
---
KIA-CODE: 知识入库代码级闭环
Asset: competitive_effectiveness_evaluator.py
Status: ✅ 代码级KIA完成
Date: 2026-04-15
Batch: OM-03 Python资产25份代码级KIA-批次三

KIA-Loop:
  - 接收清点: 2026-04-15
  - 轻量提取: 2026-04-15 (代码结构识别)
  - 查重去冗: 2026-04-15 (无重复代码)
  - Tier分级: T1 (核心项目资产)
  - 深度洞察: 2026-04-15 (案例库与决策系统)
  - 血液化: ✅ 完成 (五路图腾映射确认)
  - 归档锁定: 2026-04-15

功能定位:
  - 用途: 竞争效能评估器
  - 关联: 竞品分析
  - 维护者: 蓝军+满意姐

血液化映射:
  - 五路图腾关联: 竞争定位
  - 产品映射: 司马贺-理性决策
  - 运营映射: 案例库与决策支持

---
"""

#!/usr/bin/env python3
"""
competitive_effectiveness_evaluator.py
硬科技创业决策支持服务竞争效能对比评估器 V1.0
基于《41硬科技创业决策支持服务的竞争效能对比研究》

功能:
- 从6个维度评估不同决策支持服务模式与创业需求的匹配度
- 支持满意解、AI教练、合伙人匹配平台、传统咨询、孵化器、心理测评的横向对比
- 根据客户情境特征推荐最适合的服务组合
- Markdown 竞争效能对比报告生成
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class CompetitiveEffectivenessEvaluator(BaseComponent):
    """竞争效能对比评估器"""

    SERVICE_PROFILES = {
        "满意解方法论": {
            "合伙人深度匹配": 5,
            "决策陪跑": 5,
            "危机干预": 4,
            "规模化能力": 2,
            "单价可及性": 3,
            "科学严谨性": 4,
        },
        "AI教练平台": {
            "合伙人深度匹配": 2,
            "决策陪跑": 3,
            "危机干预": 1,
            "规模化能力": 5,
            "单价可及性": 5,
            "科学严谨性": 3,
        },
        "合伙人匹配平台": {
            "合伙人深度匹配": 3,
            "决策陪跑": 1,
            "危机干预": 1,
            "规模化能力": 4,
            "单价可及性": 4,
            "科学严谨性": 2,
        },
        "传统管理咨询": {
            "合伙人深度匹配": 3,
            "决策陪跑": 2,
            "危机干预": 2,
            "规模化能力": 3,
            "单价可及性": 1,
            "科学严谨性": 4,
        },
        "孵化器投后服务": {
            "合伙人深度匹配": 2,
            "决策陪跑": 2,
            "危机干预": 2,
            "规模化能力": 4,
            "单价可及性": 3,
            "科学严谨性": 2,
        },
        "心理测评工具": {
            "合伙人深度匹配": 2,
            "决策陪跑": 1,
            "危机干预": 1,
            "规模化能力": 5,
            "单价可及性": 4,
            "科学严谨性": 4,
        },
    }

    def __init__(self, client_name: str = ""):
        super().__init__("competitive_effectiveness_evaluator")
        self.client_name = client_name

    def evaluate(self, needs: Dict[str, int]) -> Dict[str, Any]:
        """根据客户需求评估各服务模式的匹配度"""
        scores = {}
        for service, profile in self.SERVICE_PROFILES.items():
            match_score = 0
            max_possible = 0
            for dimension, need_level in needs.items():
                capability = profile.get(dimension, 3)
                match_score += need_level * capability
                max_possible += need_level * 5
            fit_ratio = match_score / max_possible if max_possible > 0 else 0
            scores[service] = round(fit_ratio, 3)

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return {
            "客户": self.client_name or "未命名",
            "需求": needs,
            "匹配度排名": ranked,
            "最佳匹配": ranked[0][0],
            "推荐理由": self._recommend_reason(ranked[0][0]),
        }

    def _recommend_reason(self, top_service: str) -> str:
        reasons = {
            "满意解方法论": "高冲突风险合伙人决策的首选，提供深度陪跑和伦理框架支持",
            "AI教练平台": "标准化创新训练和快速方案产出的高性价比选择",
            "合伙人匹配平台": "适合候选人池扩张和初期对接，深度评估需补充",
            "传统管理咨询": "复杂战略分析和行业经验的权威来源，周期长、单价高",
            "孵化器投后服务": "综合资源扶持的全链条选择，合伙人专项支持相对有限",
            "心理测评工具": "学术验证的人格快照，适合作为决策辅助数据输入",
        }
        return reasons.get(top_service, "")

    def generate_report(self, needs: Dict[str, int]) -> str:
        result = self.evaluate(needs)
        lines = [
            f"# 硬科技决策支持服务竞争效能对比报告 — {self.client_name or '未命名客户'}",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**最佳匹配**: {result['最佳匹配']}",
            "",
            "## 匹配度排名",
            "```json",
            json.dumps(result['匹配度排名'], ensure_ascii=False, indent=2),
            "```",
            "",
            f"## 推荐理由\n\n{result['推荐理由']}",
        ]
        report_path = Path(self.workspace) / "memory" / f"competitive-effectiveness-report-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="竞争效能对比评估器")
    parser.add_argument("--client", default="", help="客户名称")
    parser.add_argument("--report", action="store_true", help="生成对比报告")
    args = parser.parse_args()

    evaluator = CompetitiveEffectivenessEvaluator(client_name=args.client)
    sample_needs = {
        "合伙人深度匹配": 5,
        "决策陪跑": 4,
        "危机干预": 3,
        "规模化能力": 2,
        "单价可及性": 3,
        "科学严谨性": 4,
    }
    path = evaluator.generate_report(sample_needs)
    print(f"竞争效能对比报告已生成: {path}")


if __name__ == "__main__":
    main()
