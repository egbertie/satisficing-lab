#!/bin/bash
# Skill A/B Testing Framework - Skill进化A/B测试框架
# 每月对比2个Skill版本效果

SKILL_DIR="/root/.openclaw/workspace/skills"
TEST_DIR="/root/.openclaw/workspace/skills/.ab-testing"
LOG_FILE="/var/log/skill-ab-test.log"
DATE=$(date +%Y-%m-%d)

mkdir -p "$TEST_DIR"

# A/B测试配置
init_ab_test() {
    local skill_name=$1
    local variant_a=$2
    local variant_b=$3
    
    echo "=== Skill A/B Test Init: $skill_name ===" | tee -a "$LOG_FILE"
    echo "Date: $DATE" | tee -a "$LOG_FILE"
    echo "Variant A: $variant_a" | tee -a "$LOG_FILE"
    echo "Variant B: $variant_b" | tee -a "$LOG_FILE"
    
    # 创建测试目录结构
    mkdir -p "$TEST_DIR/$skill_name/{A,B,results}"
    
    # 记录测试开始
    cat > "$TEST_DIR/$skill_name/test-config.json" << EOF
{
    "skill": "$skill_name",
    "start_date": "$DATE",
    "variant_a": "$variant_a",
    "variant_b": "$variant_b",
    "status": "RUNNING",
    "metrics": {
        "accuracy": {"A": 0, "B": 0},
        "token_usage": {"A": 0, "B": 0},
        "user_satisfaction": {"A": 0, "B": 0},
        "execution_time": {"A": 0, "B": 0}
    }
}
EOF
    
    echo "✅ A/B test initialized for $skill_name" | tee -a "$LOG_FILE"
}

# 记录测试数据
record_metric() {
    local skill_name=$1
    local variant=$2
    local metric=$3
    local value=$4
    
    local config_file="$TEST_DIR/$skill_name/test-config.json"
    
    if [ -f "$config_file" ]; then
        # 使用Python更新JSON
        python3 << PYEOF
import json
with open("$config_file", "r") as f:
    data = json.load(f)
data["metrics"]["$metric"]["$variant"] = $value
with open("$config_file", "w") as f:
    json.dump(data, f, indent=2)
PYEOF
        echo "📊 Recorded: $skill_name[$variant].$metric = $value" | tee -a "$LOG_FILE"
    fi
}

# 结束测试并生成报告
finalize_test() {
    local skill_name=$1
    
    local config_file="$TEST_DIR/$skill_name/test-config.json"
    
    if [ ! -f "$config_file" ]; then
        echo "❌ No test found for $skill_name" | tee -a "$LOG_FILE"
        return 1
    fi
    
    echo "=== Finalizing A/B Test: $skill_name ===" | tee -a "$LOG_FILE"
    
    # 生成报告
    python3 << PYEOF
import json

with open("$config_file", "r") as f:
    data = json.load(f)

metrics = data["metrics"]
variant_a = data["variant_a"]
variant_b = data["variant_b"]

# 计算胜出者
wins = {"A": 0, "B": 0}

for metric, values in metrics.items():
    if values["A"] > values["B"]:
        wins["A"] += 1
    elif values["B"] > values["A"]:
        wins["B"] += 1

winner = "A" if wins["A"] > wins["B"] else "B" if wins["B"] > wins["A"] else "TIE"

# 生成报告
report = f"""
# Skill A/B Test Report: {skill_name}

## 测试配置
- 开始日期: {data['start_date']}
- 结束日期: $DATE
- Variant A: {variant_a}
- Variant B: {variant_b}

## 测试结果
| 指标 | Variant A | Variant B | 胜出 |
|------|-----------|-----------|------|
| 准确性 | {metrics['accuracy']['A']} | {metrics['accuracy']['B']} | {'A' if metrics['accuracy']['A'] > metrics['accuracy']['B'] else 'B'} |
| Token消耗 | {metrics['token_usage']['A']} | {metrics['token_usage']['B']} | {'A' if metrics['token_usage']['A'] < metrics['token_usage']['B'] else 'B'} |
| 用户满意度 | {metrics['user_satisfaction']['A']} | {metrics['user_satisfaction']['B']} | {'A' if metrics['user_satisfaction']['A'] > metrics['user_satisfaction']['B'] else 'B'} |
| 执行时间 | {metrics['execution_time']['A']} | {metrics['execution_time']['B']} | {'A' if metrics['execution_time']['A'] < metrics['execution_time']['B'] else 'B'} |

## 结论
- **胜出者**: Variant {winner}
- **建议**: {'推广Variant A' if winner == 'A' else '推广Variant B' if winner == 'B' else '继续观察'}

---
生成时间: $DATE
"""

with open("$TEST_DIR/$skill_name/REPORT.md", "w") as f:
    f.write(report)

print(f"✅ Report generated: $TEST_DIR/$skill_name/REPORT.md")
PYEOF

    # 更新状态
    sed -i 's/"status": "RUNNING"/"status": "COMPLETED"/' "$config_file"
    
    echo "✅ Test finalized for $skill_name" | tee -a "$LOG_FILE"
}

# 主命令处理
case "$1" in
    init)
        init_ab_test "$2" "$3" "$4"
        ;;
    record)
        record_metric "$2" "$3" "$4" "$5"
        ;;
    finalize)
        finalize_test "$2"
        ;;
    list)
        echo "=== Active A/B Tests ==="
        find "$TEST_DIR" -name "test-config.json" -exec dirname {} \; 2>/dev/null
        ;;
    *)
        echo "Usage: $0 {init|record|finalize|list} [args...]"
        echo "  init <skill_name> <variant_a> <variant_b>"
        echo "  record <skill_name> <A|B> <metric> <value>"
        echo "  finalize <skill_name>"
        echo "  list"
        ;;
esac
