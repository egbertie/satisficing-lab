#!/usr/bin/env python3
"""
pressure_test_72h.py
极限72小时压力测试实施系统 V1.0
基于《极限72小时压力测试实施方案_V1.0》的简化可运行实现

功能:
- 72小时测试日程编排与任务设计
- 三维九项评估框架的数据收集
- 观察记录与评分工具
- 安全红线检查与伦理保障
- 最终报告生成
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class PressureTest72h(BaseComponent):
    """极限72小时压力测试实施系统"""
    
    # 三维九项评估框架
    EVAL_DIMENSIONS = {
        "决策能力": {
            "信息处理": "复杂信息下的筛选与优先级判断",
            "方案生成": "在约束条件下提出可行方案",
            "执行调整": "根据反馈迭代决策",
        },
        "价值观一致性": {
            "核心优先级": "对长期目标vs短期利益的取舍",
            "利益观": "资源分配与风险承担的态度",
            "诚信底线": "压力下的诚实与承诺一致性",
        },
        "关系质量": {
            "冲突处理": "建设性vs破坏性的分歧处理",
            "支持行为": "对合伙人困境的响应",
            "修复能力": "冲突后的道歉与原谅",
        },
    }
    
    # 安全红线
    SAFETY_RED_LINES = {
        "生理": {
            "每日最低睡眠": "4小时",
            "营养保障": "每小时提供易消化能量补充",
            "医疗监护": "AED设备与医疗人员全程在场",
            "紧急停止": "医疗人员可无条件叫停测试",
        },
        "心理": {
            "禁止人格羞辱": True,
            "禁止隐私侵犯": True,
            "禁止恐惧诱导": True,
            "任务相关压力": "压力必须与创业能力评估直接关联",
        },
        "伦理": {
            "知情同意": "测试前72小时收到完整方案说明",
            "退出权利": "任何时刻可无责退出",
            "数据保密": "明确数据使用范围",
        },
    }
    
    # 72小时日程模板
    SCHEDULE = {
        "Day 1": {
            "主题": "高强度任务日（建立基线）",
            "上午": {
                "时段": "6小时",
                "任务": "复杂问题解决",
                "场景": "SaaS企业核心客户流失+关键技术故障",
                "压力源": ["信息干扰", "时间压力(90分钟更新)"],
                "观察要点": ["关键互动时刻", "信息处理方式", "方案生成速度", "角色分工自然性"],
                "评分维度": ["结构化思维", "压力稳定性", "沟通能力", "领导风格"],
            },
            "下午": {
                "时段": "6小时",
                "任务": "资源受限团队任务（MVP冲刺）",
                "场景": "48小时产品冲刺模拟",
                "压力源": ["资源稀缺", "目标冲突", "动态调整(90分钟外部事件)"],
                "观察要点": ["创造性协作", "利益协调", "资源审计透明度", "紧急求助行为"],
                "评分维度": ["创造性", "协作效率", "冲突处理", "计划执行"],
            },
            "晚上": {
                "时段": "2小时",
                "任务": "反思与规划（3R框架）",
                "内容": "Results结果 / Roles角色 / Relationship关系",
                "压力源": ["睡眠限制启动（4小时）"],
                "观察要点": ["自我认知准确性", "关系维护主动性", "疲劳下的情绪管理"],
                "评分维度": ["反思深度", "关系修复", "疲劳适应"],
            },
        },
        "Day 2": {
            "主题": "冲突与压力日（压力峰值）",
            "上午": {
                "时段": "6小时",
                "任务": "故意制造决策冲突",
                "场景": "战略方向根本性分歧（技术深耕vs市场扩张）",
                "压力源": ["目标对立", "时间挤压", "联盟动态"],
                "观察要点": ["冲突建设性", "情绪控制", "说服与妥协", "联盟行为"],
                "评分维度": ["冲突处理", "价值观优先级", "说服力", "情绪韧性"],
            },
            "下午": {
                "时段": "6小时",
                "任务": "突发危机处理",
                "场景": "完全意外事件（黑天鹅）",
                "压力源": ["多重危机叠加", "领导力真空"],
                "观察要点": ["危机响应模式", "自然领导力涌现", "团队凝聚力", "情绪传染控制"],
                "评分维度": ["危机决策", "领导力", "团队凝聚", "压力耐受"],
            },
            "晚上": {
                "时段": "2小时",
                "任务": "压力下的沟通任务",
                "内容": "敏感话题讨论+观察员挑衅/误导",
                "压力源": ["累计睡眠剥夺12-16小时", "第三方负面反馈"],
                "观察要点": ["情绪传染", "支持行为", "负面信息处理", "关系修复尝试"],
                "评分维度": ["沟通质量", "支持行为", "负面反馈处理", "恢复力"],
            },
        },
        "Day 3": {
            "主题": "恢复与观察日（韧性验证）",
            "上午": {
                "时段": "4小时",
                "任务": "疲劳状态下的创意任务",
                "场景": "复杂创意挑战（新产品概念/商业模式创新）",
                "压力源": ["严重疲劳", "认知负荷"],
                "观察要点": ["残余功能维持", "自我管理", "创意产出", "与Day1对比"],
                "评分维度": ["疲劳产出", "自我管理", "创意质量", "对比退化"],
            },
            "下午": {
                "时段": "4小时",
                "任务": "关系修复与总结",
                "内容": "冲突回顾+道歉与原谅+未来契约",
                "观察要点": ["修复主动性", "道歉真诚度", "原谅能力", "契约具体性"],
                "评分维度": ["修复主动性", "道歉能力", "原谅能力", "承诺具体性"],
            },
        },
    }
    # 五图腾合议机制
    COUNCIL_MECHANISM = {
        "刘禹锡 (土 - 价值纯度)": {
            "关注点": "测试是否真正筛选出德馨之才，而非仅挑选抗压士兵",
            "通过条件": "高压下仍保持诚实、尊重与长期价值观一致性",
            "反对信号": ["欺骗观察员", "贬低队友", "为赢不择手段"],
        },
        "司马贺 (金 - 满意解方法论)": {
            "关注点": "72小时高密度信息是否足够做出合伙人匹配的满意决策",
            "通过条件": "信息增益显著高于常规面试，且决策风险可控",
            "保留条件": "建议将72小时测试作为满意解决策中的一个强信号维度，权重不超过30%",
        },
        "观自在 (水 - 风险守望)": {
            "关注点": "测试对参与者身心安全的潜在伤害",
            "通过条件": "三层安全协议完备，医疗监护全程在场，独立停止点有效",
            "反对条件": ["出现创伤反应", "医疗叫停后仍继续", "无独立停止点"],
        },
        "孔子 (木 - 合伙伦理)": {
            "关注点": "测试过程是否符合仁义礼智信的伦理底线",
            "通过条件": "知情同意充分，退出无责，数据保密范围明确，禁止人格羞辱",
            "反对条件": ["知情同意不充分", "威胁退出后果", "人格羞辱或恐惧诱导"],
        },
        "六祖慧能 (火 - 顿悟直觉)": {
            "关注点": "高压情境下创始人的直觉信号与真实领导力涌现",
            "通过条件": "能触发真实的压力反应，创始人展现出自然的领导风格与合作模式",
            "保留条件": "压力过强导致参与者进入表演/迎合/冻结模式，掩盖真实自我",
        },
    }

    # 健康基线字段
    HEALTH_BASELINE = {
        "睡眠": {
            "极限版_最低睡眠": "4小时/晚（连续两晚，第3天恢复）",
            "轻度版_最低睡眠": "6小时/晚",
            "睡眠剥夺效应监测": ["微睡眠迹象", "情绪稳定性", "认知反应时"],
        },
        "生理指标": {
            "心率异常阈值": "静息心率较基线上升 >20% 或 >100bpm",
            "血压警戒": "收缩压 >160mmHg 或舒张压 >100mmHg",
            "血糖保障": "每2小时提供易消化能量补充",
        },
        "认知功能": {
            "简易心算测试": "10以内连续加减，错误率 >30% 视为认知退化信号",
            "注意力持续时间": "连续专注 <15分钟视为疲劳信号",
        },
        "心理状态": {
            "创伤反应筛查": ["解离", "过度警觉", "情绪麻木", "回避行为"],
            "每日情绪自评": "1-10分，连续 <4 分需启动安全协议",
        },
        "医疗停止点": {
            "无条件停止": ["医疗人员判定继续有风险", "参与者主动退出", "出现创伤反应"],
            "条件停止": ["连续两晚睡眠 <4h 且认知测试未通过", "心率/血压持续异常 >30分钟"],
        },
    }
    
    def __init__(self, team_name: str = ""):
        super().__init__("pressure_test_72h")
        self.team_name = team_name
        self.observations = {}
        self.safety_log = []
        
    def generate_schedule(self, start_time: datetime = None) -> Dict[str, Any]:
        """生成具体日程序列"""
        if start_time is None:
            start_time = datetime.now()
        
        schedule = {}
        for day_label, day_data in self.SCHEDULE.items():
            day_num = int(day_label.replace("Day ", ""))
            day_start = start_time + timedelta(days=day_num - 1)
            schedule[day_label] = {
                "日期": day_start.strftime("%Y-%m-%d"),
                "主题": day_data["主题"],
                "任务": day_data,
            }
        return schedule
    
    def generate_observation_form(self) -> Dict[str, Any]:
        """生成观察记录空白表"""
        form = {
            "meta": {
                "team_name": self.team_name,
                "observer": "",
                "start_time": "",
                "safety_check_passed": False,
            },
            "safety_log": [],
            "daily_records": {},
        }
        
        for day_label, day_data in self.SCHEDULE.items():
            form["daily_records"][day_label] = {}
            for period, task in day_data.items():
                if period in ("主题",):
                    continue
                form["daily_records"][day_label][period] = {
                    "评分": {dim: None for dim in task.get("评分维度", [])},
                    "观察要点记录": {pt: "" for pt in task.get("观察要点", [])},
                    "关键事件": "",
                    "风险信号": "",
                }
        
        # 三维九项汇总表
        form["dimension_summary"] = {}
        for dimension, items in self.EVAL_DIMENSIONS.items():
            form["dimension_summary"][dimension] = {
                item: {"评分": None, "证据": ""} for item in items.keys()
            }
        
        return form
    
    def check_safety(self, log_entry: Dict[str, Any]) -> Dict[str, Any]:
        """安全检查入口"""
        result = {"passed": True, "violations": [], "actions": []}
        # 简化版：记录输入并返回通过，实际应由医疗/伦理监督员人工判定
        self.safety_log.append({
            "time": datetime.now().isoformat(),
            "entry": log_entry,
        })
        return result
    
    def compute_dimension_scores(self, daily_records: Dict[str, Any]) -> Dict[str, float]:
        """基于日常记录计算三维得分"""
        scores = {}
        # 决策能力 = Day1上午+下午 + Day2上午+下午平均值
        decision_items = [
            daily_records.get("Day 1", {}).get("上午", {}).get("评分", {}).get("结构化思维", 0),
            daily_records.get("Day 1", {}).get("上午", {}).get("评分", {}).get("压力稳定性", 0),
            daily_records.get("Day 1", {}).get("下午", {}).get("评分", {}).get("创造性", 0),
            daily_records.get("Day 1", {}).get("下午", {}).get("评分", {}).get("协作效率", 0),
            daily_records.get("Day 2", {}).get("上午", {}).get("评分", {}).get("冲突处理", 0),
            daily_records.get("Day 2", {}).get("上午", {}).get("评分", {}).get("说服力", 0),
            daily_records.get("Day 2", {}).get("下午", {}).get("评分", {}).get("危机决策", 0),
            daily_records.get("Day 2", {}).get("下午", {}).get("评分", {}).get("领导力", 0),
            daily_records.get("Day 3", {}).get("上午", {}).get("评分", {}).get("疲劳产出", 0),
            daily_records.get("Day 3", {}).get("上午", {}).get("评分", {}).get("自我管理", 0),
        ]
        scores["决策能力"] = self._avg_valid(decision_items)
        
        # 价值观一致性
        value_items = [
            daily_records.get("Day 2", {}).get("上午", {}).get("评分", {}).get("价值观优先级", 0),
            daily_records.get("Day 1", {}).get("下午", {}).get("评分", {}).get("冲突处理", 0),
            daily_records.get("Day 2", {}).get("下午", {}).get("评分", {}).get("团队凝聚", 0),
        ]
        scores["价值观一致性"] = self._avg_valid(value_items)
        
        # 关系质量
        relation_items = [
            daily_records.get("Day 1", {}).get("下午", {}).get("评分", {}).get("冲突处理", 0),
            daily_records.get("Day 1", {}).get("晚上", {}).get("评分", {}).get("关系修复", 0),
            daily_records.get("Day 2", {}).get("晚上", {}).get("评分", {}).get("支持行为", 0),
            daily_records.get("Day 2", {}).get("晚上", {}).get("评分", {}).get("恢复力", 0),
            daily_records.get("Day 3", {}).get("下午", {}).get("评分", {}).get("修复主动性", 0),
            daily_records.get("Day 3", {}).get("下午", {}).get("评分", {}).get("道歉能力", 0),
            daily_records.get("Day 3", {}).get("下午", {}).get("评分", {}).get("原谅能力", 0),
        ]
        scores["关系质量"] = self._avg_valid(relation_items)
        
        overall = sum(scores.values()) / len(scores) if scores else 0
        scores["overall"] = round(overall, 2)
        return scores
    
    def _avg_valid(self, items: List[float]) -> float:
        valid = [v for v in items if v is not None and v > 0]
        return round(sum(valid) / len(valid), 2) if valid else 0.0
    
    def generate_report(self, form: Dict[str, Any] = None) -> str:
        """生成 Markdown 测试报告"""
        if form is None:
            form = self.generate_observation_form()
        
        daily_records = form.get("daily_records", {})
        dim_scores = self.compute_dimension_scores(daily_records)
        
        lines = []
        lines.append("# 极限72小时压力测试报告")
        lines.append(f"**测试团队**: {self.team_name or '(待填写)'}")
        lines.append(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")
        lines.append("## 一、安全与伦理检查")
        lines.append("### 安全红线")
        for category, rules in self.SAFETY_RED_LINES.items():
            lines.append(f"- **{category}**: {json.dumps(rules, ensure_ascii=False)}")
        lines.append("")
        lines.append("### 安全日志")
        if self.safety_log:
            for entry in self.safety_log:
                lines.append(f"- {entry['time']}: {entry['entry']}")
        else:
            lines.append("- 暂无安全事件记录")
        lines.append("")
        lines.append("## 二、72小时日程执行情况")
        for day_label, day_data in self.SCHEDULE.items():
            lines.append(f"### {day_label}: {day_data.get('主题', '')}")
            record = daily_records.get(day_label, {})
            for period in ["上午", "下午", "晚上"]:
                if period not in day_data:
                    continue
                task = day_data[period]
                rec = record.get(period, {})
                lines.append(f"**{period} - {task.get('任务', '')}**")
                lines.append(f"- 评分: {json.dumps(rec.get('评分', {}), ensure_ascii=False)}")
                lines.append(f"- 关键事件: {rec.get('关键事件', '') or '（待填写）'}")
                lines.append(f"- 风险信号: {rec.get('风险信号', '') or '（待填写）'}")
            lines.append("")
        
        lines.append("## 三、三维九项评估结果")
        for dim, score in dim_scores.items():
            if dim == "overall":
                continue
            lines.append(f"- **{dim}**: {score}")
        lines.append(f"\n**综合得分**: {dim_scores.get('overall', 0)}")
        
        recommendation = ""
        overall = dim_scores.get("overall", 0)
        if overall >= 4.0:
            recommendation = "推荐建立合伙关系"
        elif overall >= 3.0:
            recommendation = "具备合伙潜力，建议在特定条件下深入磨合"
        elif overall >= 2.0:
            recommendation = "存在显著风险，建议延长观察期或重新评估"
        else:
            recommendation = "不建议建立合伙关系"
        lines.append(f"\n**推荐结论**: {recommendation}")
        
        report_path = Path(self.workspace) / "memory" / f"pressure-test-72h-report-{self.team_name or 'draft'}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)
    
    def run_full_pipeline(self, team_name: str = "") -> str:
        """完整测试流水线入口"""
        if team_name:
            self.team_name = team_name
        form = self.generate_observation_form()
        report_path = self.generate_report(form)
        return report_path


def main():
    import argparse
    parser = argparse.ArgumentParser(description="极限72小时压力测试实施系统")
    parser.add_argument("--team", default="", help="测试团队名称")
    parser.add_argument("--schedule", action="store_true", help="输出行程表JSON")
    parser.add_argument("--form", action="store_true", help="输出空白观察表JSON")
    parser.add_argument("--report", action="store_true", help="生成空白测试报告")
    args = parser.parse_args()
    
    system = PressureTest72h(team_name=args.team)
    
    if args.schedule:
        print(json.dumps(system.generate_schedule(), ensure_ascii=False, indent=2))
    elif args.form:
        print(json.dumps(system.generate_observation_form(), ensure_ascii=False, indent=2))
    elif args.report:
        path = system.run_full_pipeline()
        print(f"测试报告已生成: {path}")
    else:
        path = system.run_full_pipeline()
        print(f"空白观察表与报告已生成: {path}")


if __name__ == "__main__":
    main()
