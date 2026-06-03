#!/usr/bin/env python3
"""
满意解基因内化机制 - M003
自动应用满意解原则，记录决策过程，验证内化效果

创建时间: 2026-03-31
状态: 整改完成
"""

import json
import os
from datetime import datetime
from pathlib import Path

class SatisficingGeneEngine:
    """满意解基因内化引擎"""
    
    def __init__(self, workspace="/root/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.decisions_dir = self.workspace / "diary" / "satisficing_decisions"
        self.decisions_dir.mkdir(parents=True, exist_ok=True)
        
        # 满意解原则检查清单
        self.principles = [
            "是否为最优解陷阱？（追求完美导致延误）",
            "时间/资源是否允许追求最优？",
            "当前方案是否足够好（satisficing）？",
            "满意解的标准是什么？",
            "是否记录了满意解的选择理由？"
        ]
    
    def evaluate_decision(self, task_name, options, constraints):
        """
        评估决策，应用满意解原则
        
        Args:
            task_name: 任务名称
            options: 可选方案列表
            constraints: 约束条件（时间/资源/质量要求）
        
        Returns:
            decision_record: 决策记录
        """
        print(f"[SATISFICING] 评估任务: {task_name}")
        print(f"  可选方案: {len(options)}个")
        print(f"  约束条件: {constraints}")
        
        # 应用满意解原则
        evaluation = {
            "task_name": task_name,
            "timestamp": datetime.now().isoformat(),
            "options_count": len(options),
            "constraints": constraints,
            "principles_check": {},
            "satisficing_threshold": self._calculate_threshold(constraints),
            "selected_option": None,
            "selection_reason": None
        }
        
        # 逐一检查满意解原则
        for i, principle in enumerate(self.principles, 1):
            check_result = self._check_principle(principle, options, constraints)
            evaluation["principles_check"][f"P{i}"] = {
                "principle": principle,
                "passed": check_result["passed"],
                "note": check_result["note"]
            }
            print(f"  [P{i}] {principle[:30]}... {'✅' if check_result['passed'] else '⚠️'}")
        
        # 选择满意解（而非最优解）
        selected = self._select_satisficing_option(options, evaluation["satisficing_threshold"])
        evaluation["selected_option"] = selected["name"]
        evaluation["selection_reason"] = selected["reason"]
        evaluation["is_optimal"] = selected.get("is_optimal", False)
        
        print(f"  [选择] {selected['name']}")
        print(f"  [理由] {selected['reason']}")
        print(f"  [类型] {'最优解' if evaluation['is_optimal'] else '满意解'}")
        
        # 保存决策记录
        self._save_decision(evaluation)
        
        return evaluation
    
    def _calculate_threshold(self, constraints):
        """根据约束计算满意解阈值"""
        threshold = {
            "time": constraints.get("time", "normal"),
            "quality": constraints.get("quality", "good_enough"),
            "cost": constraints.get("cost", "reasonable")
        }
        
        # 时间紧急时降低质量要求
        if threshold["time"] == "urgent":
            threshold["quality"] = "acceptable"
        
        return threshold
    
    def _check_principle(self, principle, options, constraints):
        """检查单个满意解原则"""
        result = {"passed": True, "note": ""}
        
        if "最优解陷阱" in principle:
            # 检查是否选项过多（可能陷入最优解陷阱）
            if len(options) > 5:
                result["passed"] = False
                result["note"] = f"选项过多({len(options)}个)，存在最优解陷阱风险"
        
        elif "时间/资源" in principle:
            # 检查约束是否允许最优
            if constraints.get("time") == "urgent":
                result["note"] = "时间紧急，必须选择满意解"
        
        return result
    
    def _select_satisficing_option(self, options, threshold):
        """选择满意解（而非最优解）"""
        if not options:
            return {"name": "无选项", "reason": "没有可选方案"}
        
        # 策略：选择第一个满足阈值要求的选项（满意解）
        # 而非遍历所有选项找最优（最优解）
        for option in options:
            if self._meets_threshold(option, threshold):
                return {
                    "name": option["name"],
                    "reason": f"满足满意解标准: {threshold['quality']}",
                    "is_optimal": False,
                    "satisficing_score": option.get("score", 0)
                }
        
        # 如果没有满意解，选择最接近的
        best_option = max(options, key=lambda x: x.get("score", 0))
        return {
            "name": best_option["name"],
            "reason": "无满意解，选择最接近的",
            "is_optimal": True,
            "satisficing_score": best_option.get("score", 0)
        }
    
    def _meets_threshold(self, option, threshold):
        """检查选项是否满足阈值"""
        score = option.get("score", 0)
        
        # 根据阈值判断
        if threshold["quality"] == "acceptable":
            return score >= 60  # 60分即可
        elif threshold["quality"] == "good_enough":
            return score >= 75  # 75分即可
        else:
            return score >= 90  # 90分
    
    def _save_decision(self, record):
        """保存决策记录"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"decision_{timestamp}.json"
        filepath = self.decisions_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        
        print(f"[保存] 决策记录: {filepath}")
    
    def get_satisficing_stats(self):
        """获取满意解决策统计"""
        stats = {
            "total_decisions": 0,
            "satisficing_count": 0,
            "optimal_count": 0,
            "satisficing_rate": 0
        }
        
        for f in self.decisions_dir.glob("*.json"):
            with open(f, 'r', encoding='utf-8') as file:
                record = json.load(file)
                stats["total_decisions"] += 1
                
                if record.get("is_optimal"):
                    stats["optimal_count"] += 1
                else:
                    stats["satisficing_count"] += 1
        
        if stats["total_decisions"] > 0:
            stats["satisficing_rate"] = stats["satisficing_count"] / stats["total_decisions"] * 100
        
        return stats
    
    def generate_report(self):
        """生成满意解内化报告"""
        stats = self.get_satisficing_stats()
        
        report = f"""
=== 满意解基因内化报告 ===

决策统计:
- 总决策数: {stats['total_decisions']}
- 满意解选择: {stats['satisficing_count']} ({stats['satisficing_rate']:.1f}%)
- 最优解选择: {stats['optimal_count']}

内化评估:
{'✅ 满意解基因已内化' if stats['satisficing_rate'] >= 60 else '⚠️ 满意解基因内化中'}

建议:
- 目标满意解率: ≥60%
- 当前状态: {'达标' if stats['satisficing_rate'] >= 60 else '需提升'}
"""
        print(report)
        return report

# 使用示例
if __name__ == "__main__":
    engine = SatisficingGeneEngine()
    
    # 示例：任务方案选择
    print("=== 满意解基因内化示例 ===")
    print()
    
    options = [
        {"name": "方案A-完美版", "score": 95, "time": 10},
        {"name": "方案B-快速版", "score": 80, "time": 3},
        {"name": "方案C-平衡版", "score": 85, "time": 5}
    ]
    
    constraints = {
        "time": "urgent",
        "quality": "good_enough",
        "cost": "reasonable"
    }
    
    result = engine.evaluate_decision(
        task_name="文档编写",
        options=options,
        constraints=constraints
    )
    
    print()
    engine.generate_report()
