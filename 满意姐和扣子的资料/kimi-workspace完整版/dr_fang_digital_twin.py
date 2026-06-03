"""
---
KIA-CODE: 知识入库代码级闭环
Asset: dr_fang_digital_twin.py
Status: ✅ 代码级KIA完成
Date: 2026-04-15
Batch: OM-03 Python资产25份代码级KIA-批次二

KIA-Loop:
  - 接收清点: 2026-04-15
  - 轻量提取: 2026-04-15 (代码结构识别)
  - 查重去冗: 2026-04-15 (无重复代码)
  - Tier分级: T1 (核心项目资产)
  - 深度洞察: 2026-04-15 (专家数字替身系统)
  - 血液化: ✅ 完成 (五路图腾映射确认)
  - 归档锁定: 2026-04-15

功能定位:
  - 用途: 方翊沣博士数字替身
  - 关联: 神经科学/BCI专家
  - 维护者: 蓝军+满意姐

血液化映射:
  - 五路图腾关联: 感知力训练
  - 专家体系: 方翊沣博士
  - 产品映射: SKU-A/B专家系统

---
"""

#!/usr/bin/env python3
"""
dr_fang_digital_twin.py
方翊沣博士数字替身 V1.0
基于《71方博士数字替身》的简化可运行实现

功能:
- 基于 BSDE (Brain Science Development & Enhancement) 体系提供神经科学咨询
- 创始人决策质量评估（qEEG Alpha波相干性模拟）
- 五阶感知力训练协议生成
- 睡眠-决策优化建议
- HRV/NST 音频干预建议
- Markdown 咨询报告自动生成
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class DrFangDigitalTwin(BaseComponent):
    """方翊沣博士数字替身 — 脑科学/BCI/神经反馈专家顾问"""

    # 创始人感知力训练五阶协议
    FIVE_STAGE_PROTOCOL = [
        {
            "阶段": "阶段一",
            "名称": "脑电基线测绘",
            "技术": "qEEG全脑19导联采集",
            "目标": "建立个人神经特征图谱(IAF、Theta/Beta比、前后脑连接)",
            "创业应用": "识别创始人决策风格(分析型vs直觉型)",
        },
        {
            "阶段": "阶段二",
            "名称": "神经可塑性窗口期干预",
            "技术": "实时Z-score神经反馈/延迟反馈",
            "目标": "增强SMR(12-15Hz)与前额叶Alpha(8-12Hz)",
            "创业应用": "提升长时间专注决策能力(对抗决策疲劳)",
        },
        {
            "阶段": "阶段三",
            "名称": "躯体信号识别训练",
            "技术": "HRV生物反馈+GSR监测",
            "目标": "建立'身体直觉'与理性决策的连接",
            "创业应用": "直觉不是玄学，而是可以被科学训练的能力",
        },
        {
            "阶段": "阶段四",
            "名称": "睡眠决策优化",
            "技术": "睡眠脑电监测+声学刺激",
            "目标": "提升睡眠纺锤波密度与REM睡眠比例",
            "创业应用": "睡个好觉是决策质量的基础保障",
        },
        {
            "阶段": "阶段五",
            "名称": "整合认知增强",
            "技术": "脑控接口任务(BCI Task)",
            "目标": "强化ECN与DMN的灵活切换",
            "创业应用": "商业决策需要'意念-行动'的直接通路",
        },
    ]

    # 神经反馈协议库
    NEUROFEEDBACK_PROTOCOLS = {
        "SMR训练": {"频率": "12-15Hz", "应用": "ADHD与焦虑、提升持续注意力"},
        "Alpha-Theta边界": {"频率": "7-8Hz", "应用": "创造力与创伤释放"},
        "Alpha不对称性": {"频率": "F4-F3 Alpha比值", "应用": "情绪调节"},
        "Beta/SMR比率": {"频率": "Beta/SMR", "应用": "注意力缺陷矫正"},
        "前额叶Alpha上调": {"频率": "10.25Hz峰值", "应用": "决策疲劳恢复、提升决策质量"},
    }

    def __init__(self, client_name: str = ""):
        super().__init__("dr_fang_digital_twin")
        self.client_name = client_name

    def assess_decision_quality(self, alpha_frontal: float = None, theta_beta: float = None) -> Dict[str, Any]:
        """创始人决策质量评估（模拟输入）"""
        # 如果未提供数据，给出评估框架
        if alpha_frontal is None or theta_beta is None:
            return {
                "评估说明": "需提供 qEEG 基线数据",
                "关键指标": {
                    "前额叶Alpha波相干性": "反映高压决策时的冷静度",
                    "Theta/Beta比值": "高比值提示内省强但执行偏弱，低比值提示专注但可能焦虑",
                    "IAF个体Alpha峰频": "通常 9-11Hz 为正常成人范围",
                },
                "干预方向": "根据具体数值匹配神经反馈协议",
            }

        result = {
            "前额叶Alpha活性": alpha_frontal,
            "Theta_Beta比值": theta_beta,
            "决策风格判定": "",
            "推荐协议": [],
        }

        if alpha_frontal < 7.5:
            result["决策风格判定"] = "高压决策时易出现过度分析或焦虑冲动"
            result["推荐协议"].append("前额叶Alpha上调训练（目标提升31% Alpha活性）")
        elif alpha_frontal > 12.0:
            result["决策风格判定"] = "冷静度较好，但需关注是否过于保守"
            result["推荐协议"].append("SMR训练 + Alpha-Theta边界训练")
        else:
            result["决策风格判定"] = "Alpha活性处于合理区间"

        if theta_beta > 4.0:
            result["推荐协议"].append("Beta/SMR比率训练（增强执行控制网络ECN活跃度）")
        elif theta_beta < 2.0:
            result["推荐协议"].append("Alpha-Theta边界训练（增强默认模式网络DMN创造力）")

        return result

    def generate_training_plan(self, focus_area: str = "决策疲劳") -> Dict[str, Any]:
        """生成五阶感知力训练计划"""
        plan = {
            "客户": self.client_name or "匿名",
            "训练重点": focus_area,
            "五阶协议": self.FIVE_STAGE_PROTOCOL,
            "预计周期": "8-12周（每阶段1.5-2.5周）",
            "每周训练频次": "2-3次神经反馈 + 每日HRV监测 + 睡眠结构优化",
        }
        return plan

    def sleep_optimization_advice(self, sleep_spindles: float = None, rem_ratio: float = None) -> Dict[str, Any]:
        """睡眠-决策优化建议"""
        advice = {
            "核心原则": "睡个好觉是决策质量的基础保障",
            "优化手段": [
                "睡眠脑电监测（In-Ear EEG）",
                "声学刺激（双声道节拍Binaural Beats诱导Theta波）",
                "NST音频技术（等时音脉冲Isochronic Tones，Alpha波峰值10.25Hz）",
                "睡眠卫生行为调整（固定作息、睡前90分钟蓝光隔离）",
            ],
        }
        if sleep_spindles is not None and rem_ratio is not None:
            advice["当前数据"] = {"睡眠纺锤波密度": sleep_spindles, "REM比例": rem_ratio}
            if sleep_spindles < 2.0:
                advice["优先级建议"] = "睡眠纺锤波密度偏低，优先进行声学刺激干预"
            elif rem_ratio < 0.18:
                advice["优先级建议"] = "REM比例偏低，需延长总睡眠时间并优化睡眠连续性"
            else:
                advice["优先级建议"] = "睡眠指标基本正常，维持当前睡眠卫生习惯"
        else:
            advice["优先级建议"] = "建议先进行至少3晚的多导睡眠监测或In-Ear EEG监测，获取基线数据"
        return advice

    def hrv_nst_intervention(self, resting_hrv: float = None) -> Dict[str, Any]:
        """HRV + NST 音频干预建议"""
        advice = {
            "核心机制": "通过HRV生物反馈建立身体-大脑直连通道，训练躯体标记系统对风险信号的敏感度",
            "干预工具": [
                "Polar H10 心率带进行HRV实时监测",
                "NST音频耳机（双声道节拍 + 等时音脉冲）",
                "每日10-15分钟呼吸同步HRV训练",
            ],
        }
        if resting_hrv is not None:
            advice["当前静息HRV"] = resting_hrv
            if resting_hrv < 45:
                advice["紧迫感"] = "高"
                advice["建议"] = "建议立即开始每日HRV神经反馈训练，配合NST音频（Alpha 10.25Hz），持续4周"
            elif resting_hrv < 65:
                advice["紧迫感"] = "中"
                advice["建议"] = "建议每周3次HRV训练，维持自主神经平衡"
            else:
                advice["紧迫感"] = "低"
                advice["建议"] = "HRV基线良好，继续保持每周1-2次维护训练"
        else:
            advice["建议"] = "建议先进行连续7天晨起静息HRV监测，建立个人基线"
        return advice

    def generate_consultation_report(
        self,
        alpha_frontal: float = None,
        theta_beta: float = None,
        sleep_spindles: float = None,
        rem_ratio: float = None,
        resting_hrv: float = None,
        focus_area: str = "决策疲劳",
    ) -> str:
        """生成完整咨询报告"""
        lines = [
            f"# 方翊沣博士数字替身 — 神经科学咨询报告",
            f"**客户**: {self.client_name or '匿名'}",
            f"**咨询时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 一、创始人决策质量评估",
            "```json",
            json.dumps(self.assess_decision_quality(alpha_frontal, theta_beta), ensure_ascii=False, indent=2),
            "```",
            "",
            "## 二、五阶感知力训练计划",
            "```json",
            json.dumps(self.generate_training_plan(focus_area), ensure_ascii=False, indent=2),
            "```",
            "",
            "## 三、睡眠-决策优化建议",
            "```json",
            json.dumps(self.sleep_optimization_advice(sleep_spindles, rem_ratio), ensure_ascii=False, indent=2),
            "```",
            "",
            "## 四、HRV + NST 音频干预建议",
            "```json",
            json.dumps(self.hrv_nst_intervention(resting_hrv), ensure_ascii=False, indent=2),
            "```",
            "",
            "## 五、推荐的神经反馈协议库",
            "```json",
            json.dumps(self.NEUROFEEDBACK_PROTOCOLS, ensure_ascii=False, indent=2),
            "```",
        ]
        report_path = Path(self.workspace) / "memory" / f"dr-fang-consultation-report-{self.client_name or 'draft'}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="方翊沣博士数字替身")
    parser.add_argument("--client", default="", help="客户姓名")
    parser.add_argument("--alpha", type=float, default=None, help="前额叶Alpha活性")
    parser.add_argument("--theta-beta", type=float, default=None, help="Theta/Beta比值")
    parser.add_argument("--hrv", type=float, default=None, help="静息HRV")
    parser.add_argument("--report", action="store_true", help="生成咨询报告")
    args = parser.parse_args()

    twin = DrFangDigitalTwin(client_name=args.client)
    if args.report:
        path = twin.generate_consultation_report(
            alpha_frontal=args.alpha,
            theta_beta=args.theta_beta,
            resting_hrv=args.hrv,
        )
        print(f"咨询报告已生成: {path}")
    else:
        path = twin.generate_consultation_report()
        print(f"咨询报告已生成: {path}")


if __name__ == "__main__":
    main()
