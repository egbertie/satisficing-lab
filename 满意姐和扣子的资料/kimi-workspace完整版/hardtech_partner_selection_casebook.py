"""
---
KIA-CODE: 知识入库代码级闭环
Asset: hardtech_partner_selection_casebook.py
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
  - 用途: 硬科技合伙人选择案例库
  - 关联: 案例库管理
  - 维护者: 蓝军+满意姐

血液化映射:
  - 五路图腾关联: 刘禹锡-根基
  - 产品映射: SKU-A
  - 运营映射: 知识沉淀

---
"""

#!/usr/bin/env python3
"""
hardtech_partner_selection_casebook.py
硬科技合伙人选择案例库分析器 V1.0
基于《28硬科技初创企业合伙人选择深度研究报告_成功案例与失败案例分析_2015-2025》

功能:
- 硬科技创业合伙人选择的阶段性评估（创业前/种子期/成长期/成熟期）
- 成功模式 vs 失败模式风险扫描
- 合伙人选择检查清单生成
- 输出案例库风格的评估报告
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class HardtechPartnerSelectionCasebook(BaseComponent):
    """硬科技合伙人选择案例库分析器"""

    STAGE_ADVICE = {
        "创业前": {
            "核心建议": "审慎选择合伙人",
            "关键行动": ["能力评估", "价值观测试", "压力测试", "股权预设计"],
            "常见陷阱": ["急于组队", "关系导向", "忽视书面化", "股权均分"],
        },
        "种子期": {
            "核心建议": "建立信任基础",
            "关键行动": ["共同经历", "透明沟通", "承诺兑现", "角色边界清晰化"],
            "常见陷阱": ["口头承诺", "股权均分", "角色模糊", "使命不一致"],
        },
        "成长期": {
            "核心建议": "动态调整机制",
            "关键行动": ["Vesting启动", "里程碑评估", "贡献反馈", "引入独立董事"],
            "常见陷阱": ["静态股权", "回避冲突", "信息封锁", "创始人独裁"],
        },
        "成熟期": {
            "核心建议": "治理结构优化",
            "关键行动": ["董事会建设", "梯队培养", "代际规划", "制度化决策"],
            "常见陷阱": ["创始人依赖", "组织僵化", "传承失败", "文化稀释"],
        },
    }

    SUCCESS_PATTERNS = {
        "技术-商业互补": "技术创始人和商业化合伙人能力高度互补",
        "价值观深度一致": "对成功的定义、风险偏好、伦理底线高度一致",
        "共同经历考验": "经历过高压项目或失败，关系经受过验证",
        "动态股权设计": "股权随贡献调整，避免静态分配的僵化",
        "透明沟通机制": "建立定期沟通、冲突解决和信息披露机制",
    }

    FAILURE_PATTERNS = {
        "股权结构失衡": "控制权争议频繁，利益分配不公",
        "能力重叠严重": "两位技术型创始人缺乏商业化视角",
        "价值观冲突": "对战略方向、风险偏好、成功标准存在根本分歧",
        "沟通机制缺失": "信息不对称、冲突积压、信任逐步侵蚀",
        "创始人依赖": "关键决策过度集中，合伙人沦为执行者",
    }

    def __init__(self, startup_name: str = ""):
        super().__init__("hardtech_partner_selection_casebook")
        self.startup_name = startup_name

    def check_stage(self, stage: str, actions_done: List[str]) -> Dict[str, Any]:
        advice = self.STAGE_ADVICE.get(stage, {})
        if not advice:
            return {"错误": "未知阶段，请选择：创业前/种子期/成长期/成熟期"}

        missing = [a for a in advice.get("关键行动", []) if a not in actions_done]
        traps_avoided = [t for t in advice.get("常见陷阱", []) if t not in actions_done]

        return {
            "阶段": stage,
            "核心建议": advice["核心建议"],
            "已完成关键行动": actions_done,
            "待补充关键行动": missing,
            "潜在陷阱": advice.get("常见陷阱", []),
        }

    def pattern_scan(self, has_tech_biz_complement: bool, value_aligned: bool,
                     shared_stress_test: bool, dynamic_equity: bool,
                     transparent_comm: bool, equity_imbalanced: bool,
                     capability_overlap: bool, founder_dependent: bool) -> Dict[str, Any]:
        successes = []
        failures = []
        if has_tech_biz_complement:
            successes.append("技术-商业互补")
        else:
            failures.append("能力重叠严重")
        if value_aligned:
            successes.append("价值观深度一致")
        else:
            failures.append("价值观冲突")
        if shared_stress_test:
            successes.append("共同经历考验")
        if dynamic_equity:
            successes.append("动态股权设计")
        else:
            failures.append("股权结构失衡")
        if transparent_comm:
            successes.append("透明沟通机制")
        else:
            failures.append("沟通机制缺失")
        if founder_dependent:
            failures.append("创始人依赖")

        score = len(successes) * 20 - len(failures) * 10
        return {
            "匹配成功模式": successes,
            "命中失败模式": failures,
            "综合评分": max(0, score),
            "建议": "继续保持现有合伙人治理机制" if score >= 60 else "建议在重大决策前引入第三方合伙人评估",
        }

    def generate_report(self, stage: str, actions_done: List[str],
                        **pattern_kwargs) -> str:
        stage_check = self.check_stage(stage, actions_done)
        pattern_result = self.pattern_scan(**pattern_kwargs)
        lines = [
            f"# 硬科技合伙人选择案例库评估报告 — {self.startup_name or '未命名企业'}",
            f"**评估时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 阶段评估",
            "```json",
            json.dumps(stage_check, ensure_ascii=False, indent=2),
            "```",
            "",
            "## 成功/失败模式扫描",
            "```json",
            json.dumps(pattern_result, ensure_ascii=False, indent=2),
            "```",
        ]
        report_path = Path(self.workspace) / "memory" / f"partner-casebook-{self.startup_name or 'draft'}-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="硬科技合伙人选择案例库分析器")
    parser.add_argument("--startup", default="", help="企业名称")
    parser.add_argument("--stage", default="种子期", help="阶段（创业前/种子期/成长期/成熟期）")
    parser.add_argument("--report", action="store_true", help="生成评估报告")
    args = parser.parse_args()

    casebook = HardtechPartnerSelectionCasebook(startup_name=args.startup)
    path = casebook.generate_report(
        stage=args.stage,
        actions_done=["能力评估", "价值观测试"],
        has_tech_biz_complement=True,
        value_aligned=True,
        shared_stress_test=False,
        dynamic_equity=True,
        transparent_comm=True,
        equity_imbalanced=False,
        capability_overlap=False,
        founder_dependent=False,
    )
    print(f"案例库评估报告已生成: {path}")


if __name__ == "__main__":
    main()
