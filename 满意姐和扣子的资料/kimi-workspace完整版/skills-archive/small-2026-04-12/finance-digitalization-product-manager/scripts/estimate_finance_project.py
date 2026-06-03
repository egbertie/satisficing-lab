#!/usr/bin/env python3
import argparse
import json

BASELINES = {
    "expense-control": {
        "label": "报销与费控",
        "cost": [15, 80],
        "weeks": [6, 10],
        "outcomes": ["报销周期缩短 40%-70%", "审核人效提升 30%-50%", "合规差错率下降"]
    },
    "invoice-tax": {
        "label": "发票与税务协同",
        "cost": [20, 90],
        "weeks": [6, 12],
        "outcomes": ["税务校验工作量下降 30%-60%", "票据流转时效提升"]
    },
    "ap-automation": {
        "label": "应付自动化",
        "cost": [30, 150],
        "weeks": [8, 16],
        "outcomes": ["AP 处理效率提升 30%-50%", "重复/逾期付款风险下降"]
    },
    "ar-collection": {
        "label": "应收与回款管理",
        "cost": [25, 120],
        "weeks": [8, 16],
        "outcomes": ["DSO 改善", "逾期应收占比下降", "回款透明度提升"]
    },
    "treasury": {
        "label": "资金与现金预测",
        "cost": [50, 250],
        "weeks": [12, 24],
        "outcomes": ["现金头寸可视化", "调拨效率提升", "闲置资金减少"]
    },
    "budgeting-bi": {
        "label": "预算与经营分析",
        "cost": [60, 300],
        "weeks": [12, 24],
        "outcomes": ["预算编制周期缩短 30%-60%", "分析一致性提升"]
    },
    "close-reconciliation": {
        "label": "月结、对账与关账",
        "cost": [30, 150],
        "weeks": [8, 16],
        "outcomes": ["月结周期缩短 20%-50%", "差异处理时长下降"]
    },
    "e-archive": {
        "label": "电子会计档案",
        "cost": [20, 100],
        "weeks": [6, 12],
        "outcomes": ["查档时长显著缩短", "审计准备成本下降"]
    }
}

COMPLEXITY = {
    "low": {"cost": 0.8, "weeks": 0.9, "label": "低复杂度"},
    "medium": {"cost": 1.0, "weeks": 1.0, "label": "中复杂度"},
    "high": {"cost": 1.35, "weeks": 1.4, "label": "高复杂度"}
}

TEAM_HINT = {
    "low": ["产品/BA", "实施顾问", "低代码或 RPA"],
    "medium": ["产品经理", "业务分析", "实施顾问", "开发", "测试"],
    "high": ["产品经理", "架构师", "集成开发", "数据工程", "测试", "变更管理"]
}


def to_range(values, factor):
    low, high = values
    return [round(low * factor), round(high * factor)]


def main():
    parser = argparse.ArgumentParser(description="Estimate finance digitalization project baseline.")
    parser.add_argument("--scenario", choices=sorted(BASELINES.keys()), required=True)
    parser.add_argument("--complexity", choices=sorted(COMPLEXITY.keys()), default="medium")
    parser.add_argument("--integrations", type=int, default=0, help="Number of non-standard integrations.")
    parser.add_argument("--ai", action="store_true", help="Whether AI capability is included.")
    args = parser.parse_args()

    base = BASELINES[args.scenario]
    factor = COMPLEXITY[args.complexity]

    cost_range = to_range(base["cost"], factor["cost"])
    week_range = to_range(base["weeks"], factor["weeks"])

    integration_uplift = max(args.integrations, 0) * 5
    ai_uplift = 15 if args.ai else 0

    result = {
        "scenario": base["label"],
        "complexity": factor["label"],
        "estimated_cost_range_wan_cny": [cost_range[0] + integration_uplift + ai_uplift, cost_range[1] + integration_uplift + ai_uplift],
        "estimated_week_range": [week_range[0], week_range[1] + max(args.integrations, 0)],
        "team_hint": TEAM_HINT[args.complexity],
        "baseline_outcomes": base["outcomes"],
        "assumptions": [
            "默认按中国企业项目交付口径估算",
            "未包含大规模历史数据治理与组织重构成本",
            "每个非标准接口按约 5 万元增量估算",
            "AI 能力默认增加模型、复核与安全控制相关投入"
        ]
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
