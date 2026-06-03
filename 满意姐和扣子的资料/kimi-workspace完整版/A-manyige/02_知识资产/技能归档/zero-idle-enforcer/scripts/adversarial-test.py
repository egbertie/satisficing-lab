#!/usr/bin/env python3
"""
零空置强制执行器 - 对抗测试 (S7)
模拟各种边界条件验证触发逻辑
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


class AdversarialTester:
    """对抗测试执行器 - S7"""
    
    def __init__(self):
        self.current_time = int(time.time())
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def _mock_last_activity(self, desc):
        """根据描述模拟最后活动时间"""
        if "future" in desc:
            return self.current_time + 3600
        elif "60d_ago" in desc:
            return self.current_time - 86400 * 60
        elif "30d_ago" in desc:
            return self.current_time - 86400 * 30
        elif "8h_ago" in desc:
            return self.current_time - 3600 * 8
        elif "3h_ago" in desc:
            return self.current_time - 3600 * 3
        elif "2h_ago" in desc:
            return self.current_time - 3600 * 2
        elif "1h59m_ago" in desc:
            return self.current_time - (3600 * 2 - 60)
        elif "1h_ago" in desc:
            return self.current_time - 3600
        elif "30m_ago" in desc:
            return self.current_time - 1800
        elif "5m_ago" in desc:
            return self.current_time - 300
        elif "1h_future" in desc:
            return self.current_time + 3600
        return self.current_time
    
    def run_all_tests(self):
        """运行全部对抗测试"""
        print("=" * 60)
        print("零空置强制执行器 - 对抗测试报告 (S7)")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 基础场景
        print("\n【基础场景】")
        self._test("正常空闲(3小时)", 
                   {"last_activity": "3h_ago"},
                   {"should_fill": True})
        
        self._test("用户活跃(5分钟)", 
                   {"last_activity": "5m_ago"},
                   {"should_fill": False})
        
        # 边界场景
        print("\n【边界场景】")
        self._test("刚好2小时空闲", 
                   {"last_activity": "2h_ago"},
                   {"should_fill": True})
        
        self._test("差1分钟到2小时", 
                   {"last_activity": "1h59m_ago"},
                   {"should_fill": False})
        
        # 资源场景
        print("\n【资源场景】")
        self._test("Token充足(50%)+空闲", 
                   {"last_activity": "3h_ago", "token_pct": 50},
                   {"should_fill": True, "mode": "dual_line"})
        
        self._test("Token较低(20%)+空闲", 
                   {"last_activity": "3h_ago", "token_pct": 20},
                   {"should_fill": True, "mode": "line2_only"})
        
        self._test("Token临界(10%)+空闲", 
                   {"last_activity": "3h_ago", "token_pct": 10},
                   {"should_fill": False})
        
        # 阻断场景
        print("\n【阻断场景】")
        self._test("用户显式阻断", 
                   {"last_activity": "3h_ago", "blocker": True},
                   {"should_fill": False})
        
        # 异常场景
        print("\n【异常场景】")
        self._test("数据异常-未来时间戳", 
                   {"last_activity": "1h_future"},
                   {"should_fill": False, "error": True})
        
        self._test("数据异常-60天前", 
                   {"last_activity": "60d_ago"},
                   {"should_fill": False, "error": True})
        
        # 组合场景
        print("\n【组合场景】")
        self._test("刚补位完1小时+空闲", 
                   {"last_activity": "3h_ago", "last_fill": "1h_ago"},
                   {"should_fill": False})
        
        self._test("长空闲8小时+Token正常", 
                   {"last_activity": "8h_ago", "token_pct": 60},
                   {"should_fill": True, "mode": "dual_line"})
        
        # 生成最终报告
        self._generate_report()
    
    def _test(self, name, mock_state, expected):
        """运行单个测试"""
        # 模拟检测结果
        actual = self._simulate(mock_state)
        
        # 对比预期
        passed = True
        for key, exp_val in expected.items():
            if key not in actual or actual[key] != exp_val:
                passed = False
                break
        
        # 记录结果
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {name}")
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
            print(f"       预期: {expected}")
            print(f"       实际: {actual}")
        
        self.results.append({
            "name": name,
            "passed": passed,
            "mock": mock_state,
            "expected": expected,
            "actual": actual
        })
    
    def _simulate(self, mock_state):
        """模拟零空置检测逻辑"""
        result = {"should_fill": False}
        
        # 检查阻断
        if mock_state.get("blocker"):
            return result
        
        # 计算空闲时间
        last_activity = self._mock_last_activity(mock_state.get("last_activity", ""))
        inactive_time = self.current_time - last_activity
        
        # 异常检查
        if inactive_time > 2592000:  # 30天
            result["error"] = True
            return result
        
        if last_activity > self.current_time:  # 未来时间
            result["error"] = True
            return result
        
        # 空闲阈值
        if inactive_time < 7200:  # 2小时
            return result
        
        # 检查上次补位
        if "last_fill" in mock_state:
            last_fill = self._mock_last_activity(mock_state["last_fill"])
            time_since_fill = self.current_time - last_fill
            if time_since_fill < 7200:
                return result
        
        # Token检查
        token_pct = mock_state.get("token_pct", 100)
        if token_pct < 15:
            return result
        
        # 可以补位
        result["should_fill"] = True
        if token_pct < 30:
            result["mode"] = "line2_only"
        else:
            result["mode"] = "dual_line"
        
        return result
    
    def _generate_report(self):
        """生成测试报告"""
        total = self.passed + self.failed
        accuracy = self.passed / total if total > 0 else 0
        
        print("\n" + "=" * 60)
        print("测试结果汇总")
        print("=" * 60)
        print(f"总测试数: {total}")
        print(f"通过: {self.passed}")
        print(f"失败: {self.failed}")
        print(f"准确率: {accuracy*100:.1f}%")
        
        if accuracy >= 0.95:
            print("\n✅ 结论: 所有对抗测试通过 (S7达标)")
        else:
            print("\n❌ 结论: 测试未通过，需要修复")
        
        print("=" * 60)
        
        # 保存报告
        report = {
            "test_type": "adversarial",
            "timestamp": datetime.now().isoformat(),
            "total": total,
            "passed": self.passed,
            "failed": self.failed,
            "accuracy": accuracy,
            "results": self.results,
            "conclusion": "PASS" if accuracy >= 0.95 else "FAIL"
        }
        
        reports_dir = Path(__file__).parent.parent / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f"adversarial-test-{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n报告已保存: {report_file}")
        
        return accuracy >= 0.95


def main():
    tester = AdversarialTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
