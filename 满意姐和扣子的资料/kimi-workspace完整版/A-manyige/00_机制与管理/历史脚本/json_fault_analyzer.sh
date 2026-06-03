#!/bin/bash
# JSON故障深入排查脚本
# 分析JSON错误根因

echo "=== JSON故障深入排查 ==="
echo "时间: $(date)"
echo ""

# 分析1: 统计错误发生频率
echo "【分析1】错误发生频率"
ERROR_COUNT=$(grep -c "Expected double-quoted property name" /var/log/syslog 2>/dev/null || echo "0")
echo "  今日JSON错误次数: $ERROR_COUNT"

# 分析2: 提取错误详情
echo ""
echo "【分析2】错误详情分析"
grep "Expected double-quoted property name" /var/log/syslog 2>/dev/null | tail -3 | while read line; do
    echo "  错误: $line"
    # 提取时间
    error_time=$(echo "$line" | grep -oP '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')
    echo "    时间: $error_time"
    # 提取位置
    position=$(echo "$line" | grep -oP 'position \d+' | grep -oP '\d+')
    echo "    位置: $position"
done

# 分析3: 检查相关消息
echo ""
echo "【分析3】关联消息检查"
# 查找错误前后的消息
grep -B2 -A2 "Expected double-quoted property name" /var/log/syslog 2>/dev/null | tail -10

# 分析4: 可能原因推断
echo ""
echo "【分析4】可能原因推断"
echo "  1. 消息中的JSON格式不正确"
echo "  2. 属性名没有用双引号包裹"
echo "  3. 可能包含未转义的字符"
echo "  4. 可能是AI回复中的代码块格式问题"

# 分析5: 预防机制建议
echo ""
echo "【分析5】预防机制建议"
echo "  1. 所有JSON输出前进行格式验证"
echo "  2. 使用jq工具验证JSON格式"
echo "  3. 在发送前检查属性名是否加引号"
echo "  4. 建立JSON格式检查钩子"

# 生成报告
echo ""
echo "=== 排查报告生成 ==="
REPORT_FILE="/root/.openclaw/workspace/reports/json_fault_analysis_$(date +%Y%m%d_%H%M).md"

cat > "$REPORT_FILE" <> EOF
# JSON故障排查报告
## 时间: $(date)

## 错误统计
- 今日错误次数: $ERROR_COUNT
- 最后错误时间: $(grep "Expected double-quoted property name" /var/log/syslog 2>/dev/null | tail -1 | grep -oP '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')

## 可能原因
1. 消息中的JSON格式不正确
2. 属性名没有用双引号包裹
3. 可能包含未转义的字符

## 建议措施
1. 所有JSON输出前进行格式验证
2. 使用jq工具验证JSON格式
3. 建立JSON格式检查钩子

## 后续行动
- [ ] 部署JSON预检查机制
- [ ] 监控错误是否再次发生
EOF

echo "报告已生成: $REPORT_FILE"
