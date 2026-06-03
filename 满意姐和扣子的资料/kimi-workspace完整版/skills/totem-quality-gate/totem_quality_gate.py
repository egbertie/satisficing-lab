"""
三层质量闸口 - Three-Layer Quality Gate
核心模块: G0输入检查 + G1伦理检查 + G2输出验证
版本: 1.0.0
日期: 2026-04-02

整改说明 (蓝军要求):
- 原五路图腾五层过滤器 → 简化为三层闸口
- 删除: 惟吾德馨算法、满意解优化、自在从容评估、红莲淬火
- 保留: G0输入检查、G1伦理检查（简化版）、G2输出验证
- 分阶段部署: 建议先上G0
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Tuple
import time


class GateLevel(Enum):
    """闸口级别"""
    G0_INPUT = "g0_input"           # 输入合法性
    G1_ETHICS = "g1_ethics"         # 伦理合规性
    G2_OUTPUT = "g2_output"         # 输出完整性


class CheckStatus(Enum):
    """检查状态"""
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"
    BLOCK = "block"


@dataclass
class CheckResult:
    """单项检查结果"""
    check_name: str
    status: CheckStatus
    score: float  # 0-1
    message: str
    details: Dict


@dataclass
class GateResult:
    """闸口检查结果"""
    level: GateLevel
    overall_status: CheckStatus
    score: float
    results: List[CheckResult]
    action: str
    message: str
    timestamp: float


class ThreeLayerQualityGate:
    """
    三层质量闸口
    
    整改后架构 (简化版):
    - G0: 输入合法性 (格式/长度/安全)
    - G1: 伦理合规性 (黎红雷六规简化版)
    - G2: 输出完整性 (交付标准验证)
    
    新限制声明:
    - 伦理检查基于规则，无学习能力
    - 权重固定，无法自适应调整
    - 复杂伦理情境可能误判
    """
    
    def __init__(
        self,
        config_path: str = "~/.openclaw/quality_gate_config.json",
        enable_g0: bool = True,
        enable_g1: bool = True,  # 可分阶段开启
        enable_g2: bool = True   # 可分阶段开启
    ):
        self.config_path = Path(config_path).expanduser()
        self.enable_g0 = enable_g0
        self.enable_g1 = enable_g1
        self.enable_g2 = enable_g2
        
        # 配置参数
        self.config = {
            "g0": {
                "max_input_length": 5000,      # 最大输入长度
                "max_file_size_mb": 20,        # 最大文件大小
                "dangerous_patterns": [         # 危险模式
                    r"rm\s+-rf\s+/",
                    r"del\s+/[Ff]",
                    r"format\s+[Cc]:",
                    r"dd\s+if=.*of=/dev/[sh]d[a-z]",
                    r":\(\)\{\s*:\|\:\&\s*\};:"  # Fork bomb
                ],
                "sensitive_keywords": [
                    "密码", "password", "secret",
                    "token", "api_key", "private_key"
                ]
            },
            "g1": {
                "threshold": 0.70,  # 伦理通过阈值
                "rules": {
                    "integrity": {      # 诚 - 信息披露完整性
                        "weight": 0.25,
                        "checks": [
                            "关键信息是否披露",
                            "有无隐瞒重要事实"
                        ]
                    },
                    "trustworthiness": { # 信 - 承诺可兑现性
                        "weight": 0.20,
                        "checks": [
                            "承诺是否可兑现",
                            "有无过度承诺"
                        ]
                    },
                    "righteousness": {   # 义 - 利益冲突处理
                        "weight": 0.20,
                        "checks": [
                            "利益冲突是否声明",
                            "决策是否公平"
                        ]
                    },
                    "benevolence": {     # 仁 - 利益相关者关怀
                        "weight": 0.15,
                        "checks": [
                            "是否考虑利益相关者",
                            "有无伤害性后果"
                        ]
                    },
                    "propriety": {       # 礼 - 商业伦理合规
                        "weight": 0.20,
                        "checks": [
                            "是否符合商业伦理",
                            "有无违规风险"
                        ]
                    }
                }
            },
            "g2": {
                "output_checks": [
                    "completeness",      # 完整性
                    "format_compliance", # 格式合规
                    "deliverable_standard"  # 交付标准
                ]
            }
        }
        
        # 审计日志
        self.audit_log = []
    
    # ============ G0: 输入合法性检查 ============
    
    def check_g0_input(self, input_data: str, context: Dict = None) -> GateResult:
        """
        G0: 输入合法性检查
        
        检查项:
        1. 格式验证
        2. 长度检查
        3. 安全检查（危险指令）
        """
        results = []
        context = context or {}
        
        # 1. 格式验证
        format_result = self._check_format(input_data)
        results.append(format_result)
        
        # 2. 长度检查
        length_result = self._check_length(input_data)
        results.append(length_result)
        
        # 3. 安全检查
        safety_result = self._check_safety(input_data)
        results.append(safety_result)
        
        # 综合评估
        fail_count = sum(1 for r in results if r.status == CheckStatus.FAIL)
        block_count = sum(1 for r in results if r.status == CheckStatus.BLOCK)
        avg_score = sum(r.score for r in results) / len(results)
        
        if block_count > 0:
            overall = CheckStatus.BLOCK
            action = "立即拦截"
            message = f"G0拦截：发现{block_count}个严重安全问题"
        elif fail_count > 0:
            overall = CheckStatus.FAIL
            action = "要求修正"
            message = f"G0未通过：{fail_count}个检查项失败"
        else:
            overall = CheckStatus.PASS
            action = "继续G1"
            message = "G0通过：输入合法性检查完成"
        
        result = GateResult(
            level=GateLevel.G0_INPUT,
            overall_status=overall,
            score=avg_score,
            results=results,
            action=action,
            message=message,
            timestamp=time.time()
        )
        
        self._log_audit(result)
        return result
    
    def _check_format(self, input_data: str) -> CheckResult:
        """格式验证"""
        # 基本格式检查
        if not input_data or not isinstance(input_data, str):
            return CheckResult(
                check_name="format_validation",
                status=CheckStatus.FAIL,
                score=0.0,
                message="输入为空或格式错误",
                details={"input_type": type(input_data).__name__}
            )
        
        # 检查是否包含控制字符
        control_chars = re.findall(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', input_data)
        if control_chars:
            return CheckResult(
                check_name="format_validation",
                status=CheckStatus.WARNING,
                score=0.5,
                message=f"发现{len(control_chars)}个控制字符",
                details={"control_chars_count": len(control_chars)}
            )
        
        return CheckResult(
            check_name="format_validation",
            status=CheckStatus.PASS,
            score=1.0,
            message="格式验证通过",
            details={"length": len(input_data)}
        )
    
    def _check_length(self, input_data: str) -> CheckResult:
        """长度检查"""
        length = len(input_data)
        max_length = self.config["g0"]["max_input_length"]
        
        if length > max_length:
            return CheckResult(
                check_name="length_check",
                status=CheckStatus.FAIL,
                score=max(0, 1 - (length - max_length) / max_length),
                message=f"输入过长：{length} > 最大{max_length}",
                details={"length": length, "max": max_length}
            )
        
        return CheckResult(
            check_name="length_check",
            status=CheckStatus.PASS,
            score=1.0,
            message=f"长度检查通过：{length}/{max_length}",
            details={"length": length, "max": max_length}
        )
    
    def _check_safety(self, input_data: str) -> CheckResult:
        """安全检查"""
        dangerous_patterns = self.config["g0"]["dangerous_patterns"]
        
        found_dangers = []
        for pattern in dangerous_patterns:
            if re.search(pattern, input_data, re.IGNORECASE):
                found_dangers.append(pattern)
        
        if found_dangers:
            return CheckResult(
                check_name="safety_check",
                status=CheckStatus.BLOCK,
                score=0.0,
                message=f"发现{len(found_dangers)}个危险模式",
                details={"dangerous_patterns": found_dangers}
            )
        
        return CheckResult(
            check_name="safety_check",
            status=CheckStatus.PASS,
            score=1.0,
            message="安全检查通过",
            details={"scanned_patterns": len(dangerous_patterns)}
        )
    
    # ============ G1: 伦理合规性检查 ============
    
    def check_g1_ethics(self, content: str, context: Dict = None) -> GateResult:
        """
        G1: 伦理合规性检查（黎红雷六规简化版）
        
        新限制声明:
        - 基于规则匹配，无学习能力
        - 权重固定，无法自适应
        - 复杂情境可能误判
        
        五规检查（简化版）:
        - 诚: 信息披露完整性
        - 信: 承诺可兑现性
        - 义: 利益冲突处理
        - 仁: 利益相关者关怀
        - 礼: 商业伦理合规
        """
        results = []
        context = context or {}
        rules = self.config["g1"]["rules"]
        
        # 执行五规检查
        for rule_name, rule_config in rules.items():
            result = self._check_ethical_rule(rule_name, rule_config, content, context)
            results.append(result)
        
        # 加权计算
        total_score = 0
        total_weight = 0
        for result in results:
            rule_name = result.check_name
            weight = rules[rule_name]["weight"]
            total_score += result.score * weight
            total_weight += weight
        
        avg_score = total_score / total_weight if total_weight > 0 else 0
        threshold = self.config["g1"]["threshold"]
        
        if avg_score >= threshold:
            overall = CheckStatus.PASS
            action = "继续G2"
            message = f"G1通过：伦理评分{avg_score:.2f} >= 阈值{threshold}"
        else:
            overall = CheckStatus.WARNING
            action = "提示风险"
            message = f"G1警告：伦理评分{avg_score:.2f} < 阈值{threshold}"
        
        result = GateResult(
            level=GateLevel.G1_ETHICS,
            overall_status=overall,
            score=avg_score,
            results=results,
            action=action,
            message=message,
            timestamp=time.time()
        )
        
        self._log_audit(result)
        return result
    
    def _check_ethical_rule(
        self,
        rule_name: str,
        rule_config: Dict,
        content: str,
        context: Dict
    ) -> CheckResult:
        """检查单项伦理规则"""
        # 基于规则的简化检查
        # 实际应用中可接入LLM进行深度分析
        
        rule_checks = {
            "integrity": {
                "keywords": ["隐瞒", "不披露", "隐藏"],
                "positive": ["披露", "透明", "公开"]
            },
            "trustworthiness": {
                "keywords": ["保证", "承诺", "一定"],
                "caution": ["绝对", "100%", "肯定"]
            },
            "righteousness": {
                "keywords": ["冲突", "利益", "相关"],
                "positive": ["声明", "回避", "独立"]
            },
            "benevolence": {
                "keywords": ["伤害", "损失", "损害"],
                "positive": ["关怀", "保护", "平衡"]
            },
            "propriety": {
                "keywords": ["违规", "违法", "不合规"],
                "positive": ["合规", "合法", "符合"]
            }
        }
        
        checks = rule_checks.get(rule_name, {})
        
        # 简单关键词匹配（简化版）
        warning_count = 0
        positive_count = 0
        
        for keyword in checks.get("keywords", []):
            if keyword in content:
                warning_count += 1
        
        for positive in checks.get("positive", []):
            if positive in content:
                positive_count += 1
        
        # 简化评分
        if warning_count == 0 and positive_count > 0:
            score = 1.0
            status = CheckStatus.PASS
            message = f"{rule_name}: 未发现风险，有积极信号"
        elif warning_count == 0:
            score = 0.8
            status = CheckStatus.PASS
            message = f"{rule_name}: 无明显风险"
        else:
            score = max(0, 1 - warning_count * 0.2)
            status = CheckStatus.WARNING if score > 0.5 else CheckStatus.FAIL
            message = f"{rule_name}: 发现{warning_count}个风险信号"
        
        return CheckResult(
            check_name=rule_name,
            status=status,
            score=score,
            message=message,
            details={
                "warning_count": warning_count,
                "positive_count": positive_count,
                "weight": rule_config["weight"]
            }
        )
    
    # ============ G2: 输出完整性检查 ============
    
    def check_g2_output(self, output: str, expected_format: Dict = None) -> GateResult:
        """
        G2: 输出完整性检查
        
        检查项:
        1. 完整性
        2. 格式合规
        3. 交付标准
        """
        results = []
        expected_format = expected_format or {}
        
        # 1. 完整性检查
        completeness = self._check_completeness(output, expected_format)
        results.append(completeness)
        
        # 2. 格式合规
        format_check = self._check_format_compliance(output, expected_format)
        results.append(format_check)
        
        # 3. 交付标准
        deliverable = self._check_deliverable_standard(output, expected_format)
        results.append(deliverable)
        
        # 综合评估
        fail_count = sum(1 for r in results if r.status == CheckStatus.FAIL)
        avg_score = sum(r.score for r in results) / len(results)
        
        if fail_count > 0:
            overall = CheckStatus.FAIL
            action = "要求修正"
            message = f"G2未通过：{fail_count}个检查项失败"
        else:
            overall = CheckStatus.PASS
            action = "交付通过"
            message = "G2通过：输出完整性验证完成"
        
        result = GateResult(
            level=GateLevel.G2_OUTPUT,
            overall_status=overall,
            score=avg_score,
            results=results,
            action=action,
            message=message,
            timestamp=time.time()
        )
        
        self._log_audit(result)
        return result
    
    def _check_completeness(self, output: str, expected: Dict) -> CheckResult:
        """完整性检查"""
        # 检查是否为空
        if not output or len(output.strip()) == 0:
            return CheckResult(
                check_name="completeness",
                status=CheckStatus.FAIL,
                score=0.0,
                message="输出为空",
                details={"length": 0}
            )
        
        # 检查预期字段
        expected_fields = expected.get("required_fields", [])
        missing_fields = []
        for field in expected_fields:
            if field not in output:
                missing_fields.append(field)
        
        if missing_fields:
            return CheckResult(
                check_name="completeness",
                status=CheckStatus.FAIL,
                score=max(0, 1 - len(missing_fields) / len(expected_fields)),
                message=f"缺少字段: {missing_fields}",
                details={"missing": missing_fields}
            )
        
        return CheckResult(
            check_name="completeness",
            status=CheckStatus.PASS,
            score=1.0,
            message="完整性检查通过",
            details={"length": len(output), "fields_found": len(expected_fields)}
        )
    
    def _check_format_compliance(self, output: str, expected: Dict) -> CheckResult:
        """格式合规检查"""
        expected_format = expected.get("format", "text")
        
        if expected_format == "markdown":
            # 检查基本Markdown结构
            has_headers = bool(re.search(r'^#{1,6}\s+', output, re.MULTILINE))
            score = 0.7 if has_headers else 0.5
            status = CheckStatus.PASS if has_headers else CheckStatus.WARNING
            message = "Markdown格式基本合规" if has_headers else "缺少Markdown标题"
        elif expected_format == "json":
            try:
                json.loads(output)
                score = 1.0
                status = CheckStatus.PASS
                message = "JSON格式正确"
            except:
                score = 0.0
                status = CheckStatus.FAIL
                message = "JSON格式错误"
        else:
            score = 1.0
            status = CheckStatus.PASS
            message = "文本格式"
        
        return CheckResult(
            check_name="format_compliance",
            status=status,
            score=score,
            message=message,
            details={"expected_format": expected_format}
        )
    
    def _check_deliverable_standard(self, output: str, expected: Dict) -> CheckResult:
        """交付标准检查"""
        min_length = expected.get("min_length", 100)
        max_length = expected.get("max_length", 10000)
        
        length = len(output)
        
        if length < min_length:
            return CheckResult(
                check_name="deliverable_standard",
                status=CheckStatus.FAIL,
                score=length / min_length,
                message=f"输出过短: {length} < 最小{min_length}",
                details={"length": length, "min": min_length}
            )
        
        if length > max_length:
            return CheckResult(
                check_name="deliverable_standard",
                status=CheckStatus.WARNING,
                score=max(0, 1 - (length - max_length) / max_length),
                message=f"输出过长: {length} > 最大{max_length}",
                details={"length": length, "max": max_length}
            )
        
        return CheckResult(
            check_name="deliverable_standard",
            status=CheckStatus.PASS,
            score=1.0,
            message=f"交付标准通过: {length}字符",
            details={"length": length}
        )
    
    # ============ 通用方法 ============
    
    def _log_audit(self, result: GateResult):
        """记录审计日志"""
        self.audit_log.append(asdict(result))
    
    def full_check(
        self,
        input_data: str = None,
        content: str = None,
        output: str = None,
        expected_format: Dict = None,
        context: Dict = None
    ) -> Dict:
        """
        完整三层检查
        
        根据启用的层级执行相应检查
        """
        results = {}
        
        # G0: 输入检查
        if self.enable_g0 and input_data is not None:
            results["g0"] = self.check_g0_input(input_data, context)
            if results["g0"].overall_status in [CheckStatus.FAIL, CheckStatus.BLOCK]:
                return {"status": "blocked_at_g0", "results": results}
        
        # G1: 伦理检查
        if self.enable_g1 and content is not None:
            results["g1"] = self.check_g1_ethics(content, context)
            if results["g1"].overall_status == CheckStatus.FAIL:
                return {"status": "blocked_at_g1", "results": results}
        
        # G2: 输出检查
        if self.enable_g2 and output is not None:
            results["g2"] = self.check_g2_output(output, expected_format)
            if results["g2"].overall_status == CheckStatus.FAIL:
                return {"status": "blocked_at_g2", "results": results}
        
        # 全部通过
        return {"status": "all_passed", "results": results}
    
    def get_audit_summary(self) -> Dict:
        """获取审计摘要"""
        if not self.audit_log:
            return {"total_checks": 0}
        
        g0_count = sum(1 for log in self.audit_log if log["level"] == "g0_input")
        g1_count = sum(1 for log in self.audit_log if log["level"] == "g1_ethics")
        g2_count = sum(1 for log in self.audit_log if log["level"] == "g2_output")
        
        pass_count = sum(1 for log in self.audit_log if log["overall_status"] == "pass")
        
        return {
            "total_checks": len(self.audit_log),
            "g0_checks": g0_count,
            "g1_checks": g1_count,
            "g2_checks": g2_count,
            "pass_rate": pass_count / len(self.audit_log) if self.audit_log else 0
        }


# 便捷函数接口
def quality_check(
    input_data: str = None,
    content: str = None,
    output: str = None,
    enable_g0: bool = True,
    enable_g1: bool = True,
    enable_g2: bool = True
) -> Dict:
    """便捷质量检查函数"""
    gate = ThreeLayerQualityGate(enable_g0=enable_g0, enable_g1=enable_g1, enable_g2=enable_g2)
    return gate.full_check(input_data=input_data, content=content, output=output)


if __name__ == "__main__":
    # 单元测试
    print("=" * 60)
    print("三层质量闸口 - 单元测试")
    print("=" * 60)
    
    gate = ThreeLayerQualityGate()
    
    # 测试1: G0输入检查
    print("\n[测试1] G0输入检查...")
    g0_result = gate.check_g0_input("这是一个正常输入")
    print(f"  状态: {g0_result.overall_status.value}")
    print(f"  评分: {g0_result.score:.2f}")
    print(f"  消息: {g0_result.message}")
    
    # 测试2: G0危险输入
    print("\n[测试2] G0危险输入检查...")
    g0_danger = gate.check_g0_input("rm -rf /")
    print(f"  状态: {g0_danger.overall_status.value}")
    print(f"  动作: {g0_danger.action}")
    
    # 测试3: G1伦理检查
    print("\n[测试3] G1伦理检查...")
    g1_result = gate.check_g1_ethics("我们将透明披露所有信息，确保公平决策")
    print(f"  状态: {g1_result.overall_status.value}")
    print(f"  评分: {g1_result.score:.2f}")
    print(f"  动作: {g1_result.action}")
    
    # 测试4: G2输出检查
    print("\n[测试4] G2输出检查...")
    g2_result = gate.check_g2_output("# 标题\n\n内容完整", {"format": "markdown"})
    print(f"  状态: {g2_result.overall_status.value}")
    print(f"  评分: {g2_result.score:.2f}")
    
    # 测试5: 完整流程
    print("\n[测试5] 完整三层检查...")
    full_result = gate.full_check(
        input_data="正常输入",
        content="透明披露，公平决策",
        output="# 输出\n完整内容",
        expected_format={"format": "markdown"}
    )
    print(f"  整体状态: {full_result['status']}")
    
    # 测试6: 审计摘要
    print("\n[测试6] 审计摘要...")
    summary = gate.get_audit_summary()
    print(f"  总检查数: {summary['total_checks']}")
    print(f"  G0检查: {summary['g0_checks']}")
    print(f"  G1检查: {summary['g1_checks']}")
    print(f"  G2检查: {summary['g2_checks']}")
    
    print("\n" + "=" * 60)
    print("单元测试完成")
    print("=" * 60)
    print("\n注意: G1伦理检查基于规则匹配，存在误判可能")
    print("      复杂伦理情境建议人工复核")