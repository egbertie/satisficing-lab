#!/usr/bin/env python3
"""
Zero-Vacancy Executor - Self Check
S5: 自我验证 - 槽位状态自检

WIP状态：当前为概念实现
已知局限：自检覆盖有限，不保证发现所有问题
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 导入slot_manager
sys.path.insert(0, str(Path(__file__).parent))
from slot_manager import SlotManager, SlotStatus


class SlotSelfValidator:
    """
    槽位状态自检器 - S5: 自我验证
    """
    
    CHECK_DEFINITIONS = [
        {
            "name": "reserved_slot_available",
            "description": "确认用户预留槽位始终可用",
            "category": "S1-全局考虑"
        },
        {
            "name": "slot_count_consistency",
            "description": "槽位总数与配置一致",
            "category": "数据一致性"
        },
        {
            "name": "no_orphaned_slots",
            "description": "无孤立槽位（持有者不存在但状态为占用）",
            "category": "数据一致性"
        },
        {
            "name": "priority_valid",
            "description": "所有槽位优先级在有效范围内(0-100)",
            "category": "数据完整性"
        },
        {
            "name": "metrics_flowing",
            "description": "指标数据正常流动",
            "category": "S3-可观测输出"
        },
        {
            "name": "config_valid",
            "description": "配置项完整且有效",
            "category": "配置验证"
        }
    ]
    
    def __init__(self, manager: SlotManager = None):
        self.manager = manager or SlotManager()
        self.results = []
    
    def run_all_checks(self) -> Dict:
        """运行所有自检项目"""
        self.results = []
        
        # 执行各项检查
        self._check_reserved_slot()
        self._check_slot_count()
        self._check_orphaned_slots()
        self._check_priority_valid()
        self._check_metrics_flowing()
        self._check_config_valid()
        
        # 汇总结果
        passed = sum(1 for r in self.results if r["status"] == "passed")
        failed = sum(1 for r in self.results if r["status"] == "failed")
        warnings = sum(1 for r in self.results if r["status"] == "warning")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_checks": len(self.results),
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "health_score": passed / len(self.results) if self.results else 0
            },
            "checks": self.results,
            "recommendations": self._generate_recommendations()
        }
    
    def _check_reserved_slot(self):
        """检查1: 预留槽位可用"""
        user_reserved = any(
            s.holder == "user_dialogue" and s.status in [SlotStatus.RESERVED, SlotStatus.AVAILABLE]
            for s in self.manager.slots.values()
        )
        
        self.results.append({
            "name": "reserved_slot_available",
            "category": "S1-全局考虑",
            "description": "确认用户预留槽位始终可用",
            "status": "passed" if user_reserved else "failed",
            "importance": "critical",
            "message": "用户预留槽位正常，可确保用户对话响应" if user_reserved else "警告：用户预留槽位异常，可能影响用户响应"
        })
    
    def _check_slot_count(self):
        """检查2: 槽位数量一致性"""
        expected = self.manager.config["slot_management"]["total_slots"]
        actual = len(self.manager.slots)
        
        self.results.append({
            "name": "slot_count_consistency",
            "category": "数据一致性",
            "description": "槽位总数与配置一致",
            "status": "passed" if expected == actual else "failed",
            "importance": "high",
            "message": f"槽位总数 {actual} 与配置 {expected} 一致" if expected == actual else f"不一致：配置{expected}个，实际{actual}个"
        })
    
    def _check_orphaned_slots(self):
        """检查3: 无孤立槽位"""
        orphaned = []
        for slot in self.manager.slots.values():
            if slot.status == SlotStatus.OCCUPIED and slot.holder:
                # 检查持有者是否有效（简化检查）
                if not (slot.holder.startswith("user:") or 
                        slot.holder.startswith("task:") or
                        slot.holder == "user_dialogue"):
                    orphaned.append(slot.id)
        
        self.results.append({
            "name": "no_orphaned_slots",
            "category": "数据一致性",
            "description": "无孤立槽位",
            "status": "passed" if not orphaned else "warning",
            "importance": "medium",
            "message": "未发现孤立槽位" if not orphaned else f"发现 {len(orphaned)} 个孤立槽位: {orphaned}"
        })
    
    def _check_priority_valid(self):
        """检查4: 优先级有效"""
        invalid = [
            s.id for s in self.manager.slots.values()
            if s.priority < 0 or s.priority > 100
        ]
        
        self.results.append({
            "name": "priority_valid",
            "category": "数据完整性",
            "description": "所有槽位优先级在有效范围内(0-100)",
            "status": "passed" if not invalid else "failed",
            "importance": "medium",
            "message": "所有槽位优先级有效" if not invalid else f"槽位 {invalid} 优先级超出范围"
        })
    
    def _check_metrics_flowing(self):
        """检查5: 指标流动"""
        metrics = self.manager.metrics
        has_data = (
            len(metrics.get("user_response_latency_ms", [])) > 0 or
            metrics.get("check_count", 0) > 0
        )
        
        self.results.append({
            "name": "metrics_flowing",
            "category": "S3-可观测输出",
            "description": "指标数据正常流动",
            "status": "passed" if has_data else "warning",
            "importance": "medium",
            "message": "指标数据正常收集" if has_data else "暂无指标数据（可能是刚启动）"
        })
    
    def _check_config_valid(self):
        """检查6: 配置有效"""
        config = self.manager.config
        required_keys = ["slot_management", "detection", "release"]
        missing = [k for k in required_keys if k not in config]
        
        # 检查关键配置项
        total_slots = config.get("slot_management", {}).get("total_slots", 0)
        reserved = config.get("slot_management", {}).get("reserved_slots", {}).get("user_dialogue", 0)
        
        issues = []
        if missing:
            issues.append(f"缺少配置项: {missing}")
        if total_slots <= 0:
            issues.append("total_slots必须大于0")
        if reserved <= 0:
            issues.append("user_dialogue预留槽位必须大于0")
        if reserved >= total_slots:
            issues.append("预留槽位不能超过总槽位")
        
        self.results.append({
            "name": "config_valid",
            "category": "配置验证",
            "description": "配置项完整且有效",
            "status": "passed" if not issues else "failed",
            "importance": "critical",
            "message": "配置有效" if not issues else f"; ".join(issues)
        })
    
    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        failed_critical = [
            r for r in self.results 
            if r["status"] == "failed" and r.get("importance") == "critical"
        ]
        
        if failed_critical:
            recommendations.append(f"关键问题：{len(failed_critical)}个检查失败，需要立即处理")
        
        # 基于结果的建议
        for result in self.results:
            if result["status"] != "passed":
                if result["name"] == "reserved_slot_available":
                    recommendations.append("建议：检查槽位初始化逻辑，确保用户槽位被正确预留")
                elif result["name"] == "slot_count_consistency":
                    recommendations.append("建议：重新初始化槽位或检查配置文件")
                elif result["name"] == "no_orphaned_slots":
                    recommendations.append("建议：运行清理脚本释放孤立槽位")
                elif result["name"] == "priority_valid":
                    recommendations.append("建议：检查槽位优先级分配逻辑")
        
        return recommendations
    
    def print_report(self, report: Dict = None):
        """打印报告"""
        if report is None:
            report = self.run_all_checks()
        
        print("=" * 60)
        print("Zero-Vacancy Executor - 槽位状态自检报告 (S5)")
        print("=" * 60)
        print(f"时间: {report['timestamp']}")
        print(f"健康评分: {report['summary']['health_score']:.0%}")
        print(f"检查项: {report['summary']['total_checks']}")
        print(f"  ✅ 通过: {report['summary']['passed']}")
        print(f"  ❌ 失败: {report['summary']['failed']}")
        print(f"  ⚠️  警告: {report['summary']['warnings']}")
        print("-" * 60)
        
        print("\n详细结果:")
        for check in report["checks"]:
            icon = "✅" if check["status"] == "passed" else "❌" if check["status"] == "failed" else "⚠️"
            print(f"\n{icon} [{check['category']}] {check['name']}")
            print(f"   描述: {check['description']}")
            print(f"   状态: {check['status']}")
            print(f"   消息: {check['message']}")
        
        if report["recommendations"]:
            print("\n" + "-" * 60)
            print("改进建议:")
            for rec in report["recommendations"]:
                print(f"  • {rec}")
        
        print("\n" + "=" * 60)


def main():
    """主入口"""
    validator = SlotSelfValidator()
    report = validator.run_all_checks()
    validator.print_report(report)
    
    # 输出JSON格式供自动化处理
    output_path = Path("/tmp/zero-vacancy/self_check_report.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n报告已保存: {output_path}")
    
    # 返回退出码
    if report["summary"]["failed"] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
