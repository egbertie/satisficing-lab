"""
Token预算守卫 - Token Budget Guard
核心模块: 防止Token崩溃，三级熔断机制
版本: 1.0.0
日期: 2026-04-02

新限制声明 (蓝军整改要求):
- 无法获取实时Token计数（无平台API）
- 采用"基于响应长度估算"方案
- 估算误差可能达到10-20%
"""

import json
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, Optional, Callable
import re


class BudgetStatus(Enum):
    """预算状态枚举"""
    NORMAL = "normal"           # 正常
    WARNING = "warning"         # 警告
    RESTRICTED = "restricted"   # 限制模式
    MELTDOWN = "meltdown"       # 熔断


class ActionType(Enum):
    """动作类型枚举"""
    CONTINUE = "continue"       # 继续
    WARN = "warn"               # 警告
    RESTRICT = "restrict"       # 限制
    STOP = "stop"               # 停止


@dataclass
class BudgetCheckResult:
    """预算检查结果"""
    status: BudgetStatus
    action: ActionType
    current_usage: int          # 当前估算使用量
    total_budget: int           # 总预算
    usage_ratio: float          # 使用比例
    remaining: int              # 剩余预算
    message: str                # 状态消息
    allowed_operations: list    # 允许的操作


@dataclass
class UsageRecord:
    """使用记录"""
    timestamp: float
    operation: str
    content_length: int         # 内容长度
    estimated_tokens: int       # 估算Token数
    actual_response_length: int # 实际响应长度


class TokenBudgetGuard:
    """
    Token预算守卫
    
    核心机制:
    1. 三级阈值监控 (70%/85%/95%)
    2. 基于字符长度的Token估算
    3. 限制模式行为控制
    4. 使用历史记录
    
    新限制 (重要):
    - 无法获取实时Token计数（依赖平台API）
    - 采用字符长度÷4的粗略估算
    - 估算误差: 10-20%
    - 熔断阈值固定（无法动态调整）
    """
    
    # 估算系数: 平均1个Token ≈ 4个字符（中英文混合）
    CHARS_PER_TOKEN = 4
    
    # 默认预算配置
    DEFAULT_TOTAL_BUDGET = 200000  # 20万Token（约80万字符）
    
    # 三级阈值
    THRESHOLDS = {
        "warning": 0.70,      # 70% - 警告线
        "limit": 0.85,        # 85% - 限制线
        "meltdown": 0.95      # 95% - 熔断线
    }
    
    def __init__(
        self,
        total_budget: int = DEFAULT_TOTAL_BUDGET,
        history_file: str = "~/.openclaw/token_budget_history.json"
    ):
        self.total_budget = total_budget
        self.current_usage = 0
        self.history_file = Path(history_file).expanduser()
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.usage_history: list = []
        self.restricted_mode = False
        self.meltdown_triggered = False
        
        # 限制模式下的操作白名单
        self.allowed_in_restricted = [
            "text_response",      # 纯文本回复
            "compaction",         # 压缩命令
            "status_check",       # 状态检查
            "budget_query"        # 预算查询
        ]
        
        # 加载历史记录
        self._load_history()
    
    def estimate_tokens(self, text: str) -> int:
        """
        基于字符长度估算Token数
        
        新限制:
        - 这是估算，不是精确计数
        - 误差范围: 10-20%
        - 中文内容误差可能更大
        """
        if not text:
            return 0
        
        # 基础估算: 字符数 ÷ 4
        base_estimate = len(text) // self.CHARS_PER_TOKEN
        
        # 根据内容类型调整
        # 代码内容通常Token效率更低
        code_patterns = [
            r'```[\s\S]*?```',      # 代码块
            r'`[^`]+`',              # 行内代码
            r'\{[^}]+\}',            # JSON/对象
            r'\[[^\]]+\]'            # 数组
        ]
        
        code_chars = 0
        for pattern in code_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                code_chars += len(match)
        
        # 代码部分Token效率较低（约1:3）
        if code_chars > 0:
            code_estimate = code_chars // 3
            normal_chars = len(text) - code_chars
            normal_estimate = normal_chars // 4
            return code_estimate + normal_estimate
        
        return base_estimate
    
    def check_budget(
        self,
        operation: str = "general",
        estimated_input_length: int = 0
    ) -> BudgetCheckResult:
        """
        检查Token预算状态
        
        Args:
            operation: 操作类型
            estimated_input_length: 预估输入长度
        
        Returns:
            BudgetCheckResult: 检查结果和动作建议
        """
        # 估算本次操作所需Token
        estimated_tokens = estimated_input_length // self.CHARS_PER_TOKEN
        projected_usage = self.current_usage + estimated_tokens
        usage_ratio = projected_usage / self.total_budget
        remaining = self.total_budget - projected_usage
        
        # 判断状态
        if usage_ratio >= self.THRESHOLDS["meltdown"]:
            self.meltdown_triggered = True
            return BudgetCheckResult(
                status=BudgetStatus.MELTDOWN,
                action=ActionType.STOP,
                current_usage=projected_usage,
                total_budget=self.total_budget,
                usage_ratio=usage_ratio,
                remaining=remaining,
                message=f"Token即将耗尽（{usage_ratio*100:.1f}%），请新开会话继续",
                allowed_operations=[]
            )
        
        elif usage_ratio >= self.THRESHOLDS["limit"]:
            self.restricted_mode = True
            return BudgetCheckResult(
                status=BudgetStatus.RESTRICTED,
                action=ActionType.RESTRICT,
                current_usage=projected_usage,
                total_budget=self.total_budget,
                usage_ratio=usage_ratio,
                remaining=remaining,
                message=f"进入限制模式（{usage_ratio*100:.0f}%）：仅允许文本输出，禁止工具调用",
                allowed_operations=self.allowed_in_restricted
            )
        
        elif usage_ratio >= self.THRESHOLDS["warning"]:
            return BudgetCheckResult(
                status=BudgetStatus.WARNING,
                action=ActionType.WARN,
                current_usage=projected_usage,
                total_budget=self.total_budget,
                usage_ratio=usage_ratio,
                remaining=remaining,
                message=f"Token已使用{usage_ratio*100:.0f}%，建议/compaction",
                allowed_operations=["all"]
            )
        
        else:
            return BudgetCheckResult(
                status=BudgetStatus.NORMAL,
                action=ActionType.CONTINUE,
                current_usage=projected_usage,
                total_budget=self.total_budget,
                usage_ratio=usage_ratio,
                remaining=remaining,
                message="预算充足，正常执行",
                allowed_operations=["all"]
            )
    
    def record_usage(
        self,
        operation: str,
        content: str,
        response: str = ""
    ):
        """记录实际使用情况"""
        content_length = len(content)
        response_length = len(response)
        estimated_tokens = self.estimate_tokens(content + response)
        
        record = UsageRecord(
            timestamp=time.time(),
            operation=operation,
            content_length=content_length,
            estimated_tokens=estimated_tokens,
            actual_response_length=response_length
        )
        
        self.usage_history.append(asdict(record))
        self.current_usage += estimated_tokens
        
        # 保存历史（最多保留1000条）
        if len(self.usage_history) > 1000:
            self.usage_history = self.usage_history[-1000:]
        self._save_history()
    
    def is_operation_allowed(self, operation: str) -> bool:
        """检查操作是否在限制模式下允许"""
        if not self.restricted_mode and not self.meltdown_triggered:
            return True
        
        if self.meltdown_triggered:
            return False
        
        return operation in self.allowed_in_restricted
    
    def get_status(self) -> Dict:
        """获取当前状态"""
        return {
            "total_budget": self.total_budget,
            "current_usage": self.current_usage,
            "remaining": self.total_budget - self.current_usage,
            "usage_ratio": self.current_usage / self.total_budget,
            "restricted_mode": self.restricted_mode,
            "meltdown_triggered": self.meltdown_triggered,
            "thresholds": self.THRESHOLDS,
            "history_count": len(self.usage_history)
        }
    
    def _load_history(self):
        """加载历史记录"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.usage_history = data.get("history", [])
                    self.current_usage = data.get("current_usage", 0)
            except:
                self.usage_history = []
                self.current_usage = 0
    
    def _save_history(self):
        """保存历史记录"""
        data = {
            "current_usage": self.current_usage,
            "total_budget": self.total_budget,
            "last_updated": time.time(),
            "history": self.usage_history
        }
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def reset(self):
        """重置预算（新会话）"""
        self.current_usage = 0
        self.restricted_mode = False
        self.meltdown_triggered = False
        self.usage_history = []
        self._save_history()
    
    def estimate_remaining_operations(
        self,
        avg_operation_tokens: int = 1000
    ) -> int:
        """估算剩余可执行操作数"""
        remaining = self.total_budget - self.current_usage
        return remaining // avg_operation_tokens


# 便捷函数接口
def check_budget(
    total_budget: int = 200000,
    operation: str = "general",
    estimated_input_length: int = 0
) -> BudgetCheckResult:
    """便捷检查函数"""
    guard = TokenBudgetGuard(total_budget=total_budget)
    return guard.check_budget(operation, estimated_input_length)


def get_budget_status() -> Dict:
    """便捷状态查询"""
    guard = TokenBudgetGuard()
    return guard.get_status()


# 装饰器模式
class BudgetGuarded:
    """预算守卫装饰器"""
    
    def __init__(self, guard: TokenBudgetGuard = None):
        self.guard = guard or TokenBudgetGuard()
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            # 检查预算
            result = self.guard.check_budget(
                operation=func.__name__,
                estimated_input_length=len(str(args) + str(kwargs))
            )
            
            if result.action == ActionType.STOP:
                return {
                    "error": "Token预算耗尽",
                    "message": result.message,
                    "suggestion": "请新开会话继续"
                }
            
            if result.action == ActionType.RESTRICT:
                if not self.guard.is_operation_allowed(func.__name__):
                    return {
                        "error": "限制模式",
                        "message": result.message,
                        "allowed_operations": result.allowed_operations
                    }
            
            # 执行函数
            response = func(*args, **kwargs)
            
            # 记录使用
            self.guard.record_usage(
                operation=func.__name__,
                content=str(args) + str(kwargs),
                response=str(response)[:1000]  # 限制记录长度
            )
            
            return response
        
        return wrapper


if __name__ == "__main__":
    import sys
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Token预算守卫")
    parser.add_argument("--test", action="store_true", help="运行完整测试套件")
    parser.add_argument("--status", action="store_true", help="显示当前预算状态")
    args = parser.parse_args()
    
    if args.test:
        # 完整测试套件 (≥10项)
        print("=" * 70)
        print("Token预算守卫 - 完整测试套件 (v1.0.0)")
        print("=" * 70)
        
        guard = TokenBudgetGuard(total_budget=100000)
        test_results = []
        
        # 测试1: 正常状态检查
        print("\n[测试1/12] 正常状态检查...")
        try:
            result = guard.check_budget("test", 1000)
            passed = result.status == BudgetStatus.NORMAL and result.action == ActionType.CONTINUE
            test_results.append(("正常状态检查", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: {result.message}")
        except Exception as e:
            test_results.append(("正常状态检查", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试2: 警告状态(70%)
        print("\n[测试2/12] 警告状态(70%)...")
        try:
            guard.current_usage = 70000
            result = guard.check_budget("test", 1000)
            passed = result.status == BudgetStatus.WARNING and result.action == ActionType.WARN
            test_results.append(("警告状态(70%)", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: {result.message}")
        except Exception as e:
            test_results.append(("警告状态(70%)", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试3: 限制模式(85%)
        print("\n[测试3/12] 限制模式(85%)...")
        try:
            guard.current_usage = 85000
            result = guard.check_budget("test", 1000)
            passed = (result.status == BudgetStatus.RESTRICTED and 
                     result.action == ActionType.RESTRICT and
                     len(result.allowed_operations) > 0)
            test_results.append(("限制模式(85%)", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: 允许操作={result.allowed_operations}")
        except Exception as e:
            test_results.append(("限制模式(85%)", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试4: 熔断状态(95%)
        print("\n[测试4/12] 熔断状态(95%)...")
        try:
            guard.current_usage = 95000
            result = guard.check_budget("test", 1000)
            passed = (result.status == BudgetStatus.MELTDOWN and 
                     result.action == ActionType.STOP and
                     len(result.allowed_operations) == 0)
            test_results.append(("熔断状态(95%)", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: {result.message}")
        except Exception as e:
            test_results.append(("熔断状态(95%)", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试5: Token估算-纯文本
        print("\n[测试5/12] Token估算-纯文本...")
        try:
            guard = TokenBudgetGuard()  # 重置
            text = "A" * 400  # 400字符 ≈ 100 Token
            estimated = guard.estimate_tokens(text)
            passed = 80 <= estimated <= 120  # 允许20%误差
            test_results.append(("Token估算-纯文本", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: 400字符→{estimated} Token")
        except Exception as e:
            test_results.append(("Token估算-纯文本", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试6: Token估算-中文
        print("\n[测试6/12] Token估算-中文...")
        try:
            text = "中" * 400  # 400中文字符
            estimated = guard.estimate_tokens(text)
            passed = 80 <= estimated <= 120
            test_results.append(("Token估算-中文", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: 400中文字符→{estimated} Token")
        except Exception as e:
            test_results.append(("Token估算-中文", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试7: 使用记录功能
        print("\n[测试7/12] 使用记录功能...")
        try:
            guard.record_usage("test_op", "测试内容", "测试响应")
            passed = len(guard.usage_history) > 0
            test_results.append(("使用记录功能", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: 历史记录数={len(guard.usage_history)}")
        except Exception as e:
            test_results.append(("使用记录功能", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试8: 限制模式下的操作检查
        print("\n[测试8/12] 限制模式下的操作检查...")
        try:
            guard.restricted_mode = True
            allowed = guard.is_operation_allowed("text_response")
            blocked = not guard.is_operation_allowed("tool_call")
            passed = allowed and blocked
            test_results.append(("限制模式操作检查", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: text_response允许={allowed}, tool_call阻止={blocked}")
        except Exception as e:
            test_results.append(("限制模式操作检查", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试9: 状态查询
        print("\n[测试9/12] 状态查询...")
        try:
            status = guard.get_status()
            passed = ("total_budget" in status and 
                     "current_usage" in status and 
                     "usage_ratio" in status)
            test_results.append(("状态查询", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: 使用比例={status['usage_ratio']*100:.1f}%")
        except Exception as e:
            test_results.append(("状态查询", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试10: 重置功能
        print("\n[测试10/12] 重置功能...")
        try:
            guard.current_usage = 50000
            guard.reset()
            passed = (guard.current_usage == 0 and 
                     not guard.restricted_mode and 
                     not guard.meltdown_triggered)
            test_results.append(("重置功能", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: 当前使用={guard.current_usage}")
        except Exception as e:
            test_results.append(("重置功能", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试11: 剩余操作估算
        print("\n[测试11/12] 剩余操作估算...")
        try:
            guard.total_budget = 10000
            guard.current_usage = 5000
            remaining_ops = guard.estimate_remaining_operations(avg_operation_tokens=1000)
            passed = remaining_ops == 5
            test_results.append(("剩余操作估算", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: 剩余操作数={remaining_ops}")
        except Exception as e:
            test_results.append(("剩余操作估算", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试12: 估算系数准确性
        print("\n[测试12/12] 估算系数准确性...")
        try:
            # 测试英文混合文本
            text = "Hello World! This is a test. " * 10  # ~320字符
            estimated = guard.estimate_tokens(text)
            expected = len(text) // 4  # 期望≈80 Token
            passed = abs(estimated - expected) <= 10
            test_results.append(("估算系数准确性", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: {len(text)}字符→{estimated} Token (期望~{expected})")
        except Exception as e:
            test_results.append(("估算系数准确性", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试总结
        print("\n" + "=" * 70)
        print("测试总结")
        print("=" * 70)
        passed_count = sum(1 for _, p in test_results if p)
        total_count = len(test_results)
        print(f"通过: {passed_count}/{total_count}")
        print(f"失败: {total_count - passed_count}/{total_count}")
        print(f"通过率: {passed_count/total_count*100:.1f}%")
        
        if passed_count == total_count:
            print("\n✅ 所有测试通过!")
            sys.exit(0)
        else:
            print("\n❌ 存在失败的测试:")
            for name, passed in test_results:
                if not passed:
                    print(f"  - {name}")
            sys.exit(1)
    
    elif args.status:
        # 显示状态
        guard = TokenBudgetGuard()
        status = guard.get_status()
        print("=" * 60)
        print("Token预算守卫 - 状态")
        print("=" * 60)
        print(f"总预算: {status['total_budget']} Tokens")
        print(f"当前使用: {status['current_usage']} Tokens")
        print(f"剩余: {status['remaining']} Tokens")
        print(f"使用比例: {status['usage_ratio']*100:.1f}%")
        print(f"限制模式: {'是' if status['restricted_mode'] else '否'}")
        print(f"熔断状态: {'是' if status['meltdown_triggered'] else '否'}")
        print(f"历史记录: {status['history_count']} 条")
        print("=" * 60)
    
    else:
        # 默认运行快速测试
        print("=" * 60)
        print("Token预算守卫 - 快速测试")
        print("=" * 60)
        print("\n使用 --test 运行完整测试套件")
        print("使用 --status 显示当前预算状态")