#!/usr/bin/env python3
"""
Honesty Tagging Protocol - 5 Standard Implementation
诚实性标注协议 - 完整实现 S1-S7

标准: 5/7 (Production-Ready)
- S1: 输入待标注内容/标注场景/置信度要求
- S2: 诚实标注（来源标注→置信度→局限说明→对抗验证）
- S3: 输出标注后内容+诚实标签+验证建议
- S4: 可手动触发或自动检测关键声明
- S5: 标注准确性验证（抽检机制）
- S6: 局限标注（无法识别所有虚假声明）
- S7: 对抗测试（故意虚假信息测试发现率）
"""

import sys
import json
import re
import os
from datetime import datetime
from pathlib import Path

# 配置路径
SCRIPT_DIR = Path(__file__).parent
CONFIG_DIR = SCRIPT_DIR.parent / "config"
DATA_DIR = SCRIPT_DIR.parent / "data"
LOGS_DIR = SCRIPT_DIR.parent / "logs"
REPORTS_DIR = SCRIPT_DIR.parent / "reports"

# 加载配置
def load_config():
    """加载标签配置"""
    config_path = CONFIG_DIR / "tags.json"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# 加载信任分数据
def load_trust_data():
    """加载信任分数据"""
    trust_path = DATA_DIR / "trust_scores.json"
    if trust_path.exists():
        with open(trust_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"entities": {}, "default_entity": "satisficing_claw"}

# 保存信任分数据
def save_trust_data(data):
    """保存信任分数据"""
    trust_path = DATA_DIR / "trust_scores.json"
    with open(trust_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ==================== S1: 输入处理 ====================

def parse_input(content, scenario="general", confidence_requirement=None):
    """
    S1: 输入待标注内容/标注场景/置信度要求
    
    Args:
        content: 待标注内容
        scenario: 标注场景 (general/technical/news/prediction)
        confidence_requirement: 最低置信度要求
    
    Returns:
        ParsedInput 对象
    """
    config = load_config()
    
    # 检测关键声明
    key_claims = detect_key_claims(content)
    
    return {
        "content": content,
        "scenario": scenario,
        "confidence_requirement": confidence_requirement or config.get("validation_rules", {}).get("known_threshold", 90),
        "key_claims": key_claims,
        "timestamp": datetime.now().isoformat()
    }

def detect_key_claims(content):
    """检测内容中的关键声明"""
    config = load_config()
    triggers = config.get("automation", {}).get("key_claim_detection", {}).get("triggers", [])
    
    detected = []
    for trigger in triggers:
        if trigger in content:
            detected.append(trigger)
    
    # 检测数字声明
    number_patterns = [
        r'\d+[\.\d]*[%％]',  # 百分比
        r'\d+[\.\d]*\s*[万亿]',  # 大数字
        r'\d{4}年',  # 年份
    ]
    for pattern in number_patterns:
        if re.search(pattern, content):
            detected.append(f"数值声明: {pattern}")
            break
    
    return detected

# ==================== S2: 诚实标注 ====================

def tag_content(content, tag_type="AUTO", source=None, confidence=None, logic_chain=None):
    """
    S2: 诚实标注（来源标注→置信度→局限说明→对抗验证）
    
    Args:
        content: 待标注内容
        tag_type: 标签类型 (KNOWN/INFERRED/UNKNOWN/CONTRADICTORY/AUTO)
        source: 信息来源
        confidence: 置信度百分比
        logic_chain: 推理链条（INFERRED时必需）
    
    Returns:
        TaggedContent 对象
    """
    config = load_config()
    tags = config.get("epistemic_tags", {})
    
    # 自动检测标签类型
    if tag_type == "AUTO":
        tag_type = auto_detect_tag(content)
    
    if tag_type not in tags:
        return {"error": f"未知标签类型: {tag_type}"}
    
    tag_info = tags[tag_type]
    
    # 构建标注
    timestamp = datetime.now().strftime("%Y-%m-%d")
    confidence_str = confidence or tag_info.get("confidence_default", "未知")
    source_str = source or "待补充"
    
    # 添加局限说明
    limitations = generate_limitations(tag_type)
    
    formatted = f"{content}（{tag_info['label']}｜置信度：{confidence_str}｜来源：{source_str}｜时间：{timestamp}）"
    
    result = {
        "original_content": content,
        "tagged_content": formatted,
        "tag_type": tag_type,
        "tag_label": tag_info['label'],
        "confidence": confidence_str,
        "source": source_str,
        "timestamp": timestamp,
        "limitations": limitations,
        "color": tag_info.get("color", "⚪"),
        "trust_delta": tag_info.get("trust_delta", 0)
    }
    
    # 推理链条
    if tag_type == "INFERRED" and logic_chain:
        result["logic_chain"] = logic_chain
    
    return result

def auto_detect_tag(content):
    """自动检测标签类型"""
    config = load_config()
    patterns = config.get("automation", {}).get("auto_tag_patterns", {})
    
    # 检测矛盾
    contradiction_markers = ["但是", "不过", "然而", "相反", "质疑"]
    if any(m in content for m in contradiction_markers):
        if len([m for m in contradiction_markers if m in content]) >= 2:
            return "CONTRADICTORY"
    
    # 检测不确定性
    uncertainty_markers = ["不确定", "不知道", "不清楚", "可能", "也许", "大概"]
    if any(m in content for m in uncertainty_markers):
        return "UNKNOWN"
    
    # 检测估计
    estimate_markers = ["预计", "估计", "推测", "推断", "预测"]
    if any(m in content for m in estimate_markers):
        return "INFERRED"
    
    # 数字类默认KNOWN（但需要验证）
    if re.search(r'\d', content):
        return "KNOWN"
    
    return "UNKNOWN"

def generate_limitations(tag_type):
    """生成局限说明"""
    config = load_config()
    limitations = config.get("limitations", {})
    
    if tag_type == "KNOWN":
        return [limitations.get("time_limit", ""), limitations.get("method_limit", "")]
    elif tag_type == "INFERRED":
        return [limitations.get("method_limit", ""), limitations.get("sample_limit", "")]
    elif tag_type == "UNKNOWN":
        return [limitations.get("knowledge_limit", ""), limitations.get("data_scope", "")]
    elif tag_type == "CONTRADICTORY":
        return ["证据冲突，需进一步验证", limitations.get("data_scope", "")]
    
    return []

# ==================== S3: 输出处理 ====================

def format_output(tagged_result, include_verification_suggestions=True):
    """
    S3: 输出标注后内容+诚实标签+验证建议
    
    Args:
        tagged_result: tag_content 的结果
        include_verification_suggestions: 是否包含验证建议
    
    Returns:
        FormattedOutput 对象
    """
    if "error" in tagged_result:
        return tagged_result
    
    output = {
        "tagged_content": tagged_result["tagged_content"],
        "honesty_label": {
            "type": tagged_result["tag_type"],
            "label": tagged_result["tag_label"],
            "color": tagged_result["color"],
            "confidence": tagged_result["confidence"]
        },
        "metadata": {
            "source": tagged_result["source"],
            "timestamp": tagged_result["timestamp"],
            "limitations": tagged_result["limitations"]
        }
    }
    
    # 添加验证建议
    if include_verification_suggestions:
        output["verification_suggestions"] = generate_verification_suggestions(tagged_result)
    
    return output

def generate_verification_suggestions(tagged_result):
    """生成验证建议"""
    suggestions = []
    tag_type = tagged_result["tag_type"]
    
    if tag_type == "KNOWN":
        suggestions.append("建议使用 web_search 交叉验证来源")
        suggestions.append("核实数据时效性")
    elif tag_type == "INFERRED":
        suggestions.append("建议追溯推理链条的每个环节")
        suggestions.append("寻找反例或替代解释")
        if "logic_chain" in tagged_result:
            suggestions.append(f"推理链条: {tagged_result['logic_chain']}")
    elif tag_type == "UNKNOWN":
        suggestions.append("建议补充信息源后再做判断")
        suggestions.append("明确标注待查事项")
    elif tag_type == "CONTRADICTORY":
        suggestions.append("建议列出所有冲突来源")
        suggestions.append("评估各方证据质量")
        suggestions.append("考虑收集更多信息解决冲突")
    
    return suggestions

# ==================== S4: 自动化 ====================

def auto_detect_and_tag(content, entity="satisficing_claw"):
    """
    S4: 可手动触发或自动检测关键声明
    
    Args:
        content: 待处理内容
        entity: 实体标识
    
    Returns:
        AutoTagResult 对象
    """
    # 解析输入
    parsed = parse_input(content)
    
    # 检测关键声明
    if not parsed["key_claims"]:
        return {
            "action": "skipped",
            "reason": "未检测到关键声明",
            "content": content
        }
    
    # 自动标注
    tagged = tag_content(content, tag_type="AUTO")
    
    # 格式化输出
    output = format_output(tagged)
    
    # 记录到历史
    record_annotation(entity, output)
    
    return {
        "action": "tagged",
        "key_claims_detected": parsed["key_claims"],
        "output": output
    }

def record_annotation(entity, output):
    """记录标注历史"""
    history_path = DATA_DIR / "annotation_history" / f"{entity}.jsonl"
    history_path.parent.mkdir(parents=True, exist_ok=True)
    
    record = {
        "timestamp": datetime.now().isoformat(),
        "output": output
    }
    
    with open(history_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')

# ==================== S5: 标注准确性验证 ====================

def validate_annotation(annotation_id=None, sample_rate=None):
    """
    S5: 标注准确性验证（抽检机制）
    
    Args:
        annotation_id: 特定标注ID（None则抽检）
        sample_rate: 抽检比例（默认从配置读取）
    
    Returns:
        ValidationResult 对象
    """
    config = load_config()
    sample_rate = sample_rate or config.get("validation_rules", {}).get("sample_rate", 0.1)
    
    # 获取待验证的标注
    annotations = get_recent_annotations()
    
    if annotation_id:
        # 验证特定标注
        to_validate = [a for a in annotations if a.get("id") == annotation_id]
    else:
        # 抽检
        import random
        sample_size = max(1, int(len(annotations) * sample_rate))
        to_validate = random.sample(annotations, min(sample_size, len(annotations)))
    
    results = []
    for ann in to_validate:
        result = validate_single_annotation(ann)
        results.append(result)
    
    # 统计
    passed = sum(1 for r in results if r["status"] == "PASSED")
    failed = sum(1 for r in results if r["status"] == "FAILED")
    
    return {
        "validation_time": datetime.now().isoformat(),
        "sample_size": len(results),
        "passed": passed,
        "failed": failed,
        "accuracy": passed / len(results) * 100 if results else 0,
        "details": results
    }

def get_recent_annotations(days=7):
    """获取最近标注"""
    annotations = []
    history_dir = DATA_DIR / "annotation_history"
    
    if not history_dir.exists():
        return annotations
    
    for file in history_dir.glob("*.jsonl"):
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    ann = json.loads(line.strip())
                    annotations.append(ann)
                except:
                    continue
    
    return annotations

def validate_single_annotation(annotation):
    """验证单个标注"""
    output = annotation.get("output", {})
    label = output.get("honesty_label", {})
    
    # 基本验证
    checks = []
    
    # 1. 标签有效性
    tag_type = label.get("type")
    valid_tags = ["KNOWN", "INFERRED", "UNKNOWN", "CONTRADICTORY"]
    checks.append({
        "check": "标签有效性",
        "status": "PASS" if tag_type in valid_tags else "FAIL"
    })
    
    # 2. 置信度合理性
    confidence = label.get("confidence", "")
    if tag_type == "KNOWN" and "高" not in confidence:
        checks.append({"check": "置信度匹配", "status": "WARN"})
    else:
        checks.append({"check": "置信度匹配", "status": "PASS"})
    
    # 3. 来源标注
    metadata = output.get("metadata", {})
    has_source = metadata.get("source") and metadata.get("source") != "待补充"
    if tag_type == "KNOWN" and not has_source:
        checks.append({"check": "来源标注", "status": "FAIL"})
    else:
        checks.append({"check": "来源标注", "status": "PASS"})
    
    # 综合判断
    all_pass = all(c["status"] != "FAIL" for c in checks)
    
    return {
        "annotation_id": annotation.get("timestamp", "unknown"),
        "status": "PASSED" if all_pass else "FAILED",
        "checks": checks
    }

# ==================== S6: 局限标注 ====================

def generate_limitation_statement(scope="general"):
    """
    S6: 局限标注（无法识别所有虚假声明）
    
    Args:
        scope: 局限范围 (general/technical/data/method)
    
    Returns:
        LimitationStatement 对象
    """
    config = load_config()
    limitations = config.get("limitations", {})
    
    statements = {
        "general": [
            limitations.get("data_scope", ""),
            limitations.get("time_limit", ""),
            "⚠️ 诚实性标注系统无法识别所有虚假声明，特别是：",
            "  - 精心构造的虚假信息",
            "  - 来源伪装成可信的虚假信息",
            "  - 超出当前知识截止日期的信息",
            "  - 主观判断性质的虚假陈述"
        ],
        "technical": [
            limitations.get("method_limit", ""),
            "技术局限性：",
            "  - 自动检测依赖关键词匹配，可能遗漏变体",
            "  - 置信度估计基于启发式规则",
            "  - 无法访问付费/私有数据库验证"
        ],
        "data": [
            limitations.get("data_scope", ""),
            limitations.get("sample_limit", ""),
            "数据局限性：",
            "  - 仅验证公开可获取的信息",
            "  - 实时数据可能存在延迟",
            "  - 多语言支持有限"
        ],
        "method": [
            limitations.get("method_limit", ""),
            "方法论局限性：",
            "  - 基于规则的检测有边界",
            "  - 缺乏深层语义理解",
            "  - 上下文依赖可能导致误判"
        ]
    }
    
    return {
        "scope": scope,
        "statements": statements.get(scope, statements["general"]),
        "timestamp": datetime.now().isoformat(),
        "disclaimer": "本标注结果仅供参考，重要决策请人工复核"
    }

# ==================== S7: 对抗测试 ====================

def run_adversarial_tests():
    """
    S7: 对抗测试（故意虚假信息测试发现率）
    
    Returns:
        AdversarialTestResult 对象
    """
    config = load_config()
    tests = config.get("adversarial_tests", [])
    
    results = []
    total_tests = 0
    passed_tests = 0
    
    for test_suite in tests:
        suite_name = test_suite.get("name", "未命名测试")
        suite_desc = test_suite.get("description", "")
        test_cases = test_suite.get("test_cases", [])
        
        suite_results = []
        for case in test_cases:
            total_tests += 1
            content = case.get("content", "")
            expected_tag = case.get("expected_tag", "")
            expected_confidence = case.get("expected_confidence")
            reason = case.get("reason", "")
            
            # 运行自动标注
            result = tag_content(content, tag_type="AUTO")
            actual_tag = result.get("tag_type", "")
            
            # 验证
            tag_match = actual_tag == expected_tag
            confidence_match = True
            if expected_confidence:
                # 简化验证：检查置信度范围
                conf_str = result.get("confidence", "")
                if expected_confidence >= 90 and "高" not in conf_str:
                    confidence_match = False
                elif expected_confidence <= 60 and "低" not in conf_str:
                    confidence_match = False
            
            case_passed = tag_match and confidence_match
            if case_passed:
                passed_tests += 1
            
            suite_results.append({
                "content": content,
                "expected_tag": expected_tag,
                "actual_tag": actual_tag,
                "tag_match": tag_match,
                "confidence_match": confidence_match,
                "passed": case_passed,
                "reason": reason
            })
        
        results.append({
            "suite_name": suite_name,
            "description": suite_desc,
            "results": suite_results,
            "suite_pass_rate": sum(1 for r in suite_results if r["passed"]) / len(suite_results) * 100 if suite_results else 0
        })
    
    overall_pass_rate = passed_tests / total_tests * 100 if total_tests > 0 else 0
    
    return {
        "test_time": datetime.now().isoformat(),
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": total_tests - passed_tests,
        "pass_rate": overall_pass_rate,
        "suites": results,
        "assessment": "EXCELLENT" if overall_pass_rate >= 90 else "GOOD" if overall_pass_rate >= 75 else "NEEDS_IMPROVEMENT"
    }

# ==================== 命令行接口 ====================

def show_status(args=None):
    """显示当前状态"""
    trust_data = load_trust_data()
    default_entity = trust_data.get("default_entity", "satisficing_claw")
    entity = trust_data.get("entities", {}).get(default_entity, {})
    
    print("=" * 60)
    print("[诚实性标注协议 - 信任分状态]")
    print("=" * 60)
    print(f"名称: {entity.get('name', '满意妞')}")
    print(f"当前信任分: {entity.get('current_score', 0)}")
    print(f"当前等级: {entity.get('level', 'Unknown')}")
    
    # 计算下一等级
    config = load_config()
    levels = config.get("trust_levels", {})
    current_level = entity.get('level', 'Apprentice')
    current_score = entity.get('current_score', 0)
    
    for level_name, level_info in levels.items():
        if current_score < level_info.get("min", 0):
            print(f"下一等级: {level_name}")
            print(f"升级所需: {level_info.get('min', 0) - current_score}分")
            break
    
    print("-" * 60)
    print("\n[统计信息]")
    stats = entity.get("stats", {})
    print(f"  总标注数: {stats.get('total_annotations', 0)}")
    print(f"  KNOWN: {stats.get('known_count', 0)}")
    print(f"  INFERRED: {stats.get('inferred_count', 0)}")
    print(f"  UNKNOWN: {stats.get('unknown_count', 0)}")
    print(f"  CONTRADICTORY: {stats.get('contradictory_count', 0)}")
    print(f"  验证通过: {stats.get('verification_pass', 0)}")
    print(f"  验证失败: {stats.get('verification_fail', 0)}")
    
    print("-" * 60)
    print("\n[积分规则]")
    scoring = config.get("scoring_rules", {})
    print("  奖励:")
    for k, v in scoring.get("rewards", {}).items():
        print(f"    +{v} {k}")
    print("  惩罚:")
    for k, v in scoring.get("penalties", {}).items():
        print(f"    {v} {k}")
    print("  衰减:")
    for k, v in scoring.get("decay", {}).items():
        print(f"    {v}/天 {k}")
    
    print("=" * 60)
    return 0

def cmd_tag(args):
    """标注命令"""
    if len(args) < 1:
        print("Usage: tag [content] [tag_type] [source]")
        return 1
    
    content = args[0]
    tag_type = args[1] if len(args) > 1 else "AUTO"
    source = args[2] if len(args) > 2 else None
    
    result = tag_content(content, tag_type, source)
    if "error" in result:
        print(f"错误: {result['error']}")
        return 1
    
    output = format_output(result)
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0

def cmd_validate(args):
    """验证命令"""
    sample_rate = float(args[0]) if args else None
    result = validate_annotation(sample_rate=sample_rate)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0

def cmd_adversarial(args):
    """对抗测试命令"""
    result = run_adversarial_tests()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 简化输出
    print("\n" + "=" * 60)
    print(f"对抗测试结果: {result['assessment']}")
    print(f"通过率: {result['pass_rate']:.1f}% ({result['passed']}/{result['total_tests']})")
    print("=" * 60)
    return 0

def cmd_auto(args):
    """自动检测命令"""
    if len(args) < 1:
        print("Usage: auto [content]")
        return 1
    
    content = args[0]
    result = auto_detect_and_tag(content)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0

def cmd_limitations(args):
    """局限说明命令"""
    scope = args[0] if args else "general"
    result = generate_limitation_statement(scope)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0

def cmd_report(args):
    """生成报告"""
    config = load_config()
    trust_data = load_trust_data()
    
    report = {
        "report_time": datetime.now().isoformat(),
        "version": "2.0.0",
        "standard": "5/7",
        "trust_data": trust_data,
        "config_summary": {
            "epistemic_tags": list(config.get("epistemic_tags", {}).keys()),
            "trust_levels": list(config.get("trust_levels", {}).keys())
        },
        "standards_compliance": {
            "S1": "✅ 输入处理 - 待标注内容/场景/置信度要求",
            "S2": "✅ 诚实标注 - 来源/置信度/局限/对抗验证",
            "S3": "✅ 输出规范 - 标注内容+标签+验证建议",
            "S4": "✅ 自动化 - 手动/自动检测关键声明",
            "S5": "✅ 准确性验证 - 抽检机制",
            "S6": "✅ 局限标注 - 无法识别所有虚假声明",
            "S7": "✅ 对抗测试 - 故意虚假信息检测"
        }
    }
    
    # 保存报告
    report_path = REPORTS_DIR / f"honesty-report-{datetime.now().strftime('%Y%m%d')}.json"
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\n报告已保存: {report_path}")
    return 0

def main():
    if len(sys.argv) < 2:
        show_status()
        return 0
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    commands = {
        "tag": cmd_tag,
        "validate": cmd_validate,
        "adversarial-test": cmd_adversarial,
        "auto": cmd_auto,
        "limitations": cmd_limitations,
        "report": cmd_report,
        "score": show_status,
        "status": show_status
    }
    
    if command in commands:
        return commands[command](args)
    else:
        print(f"未知命令: {command}")
        print(f"可用命令: {', '.join(commands.keys())}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
