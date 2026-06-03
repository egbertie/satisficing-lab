#!/bin/bash
# 立即补全缺失脚本（不是今天内，是现在）

echo "=== 立即补全4个缺失脚本（不是今天内）==="
echo "时间: $(date)"
echo ""

# 脚本1: 错误预防检查
cat > /root/.openclaw/workspace/scripts/error_prevention_check.sh << 'EOF'
#!/bin/bash
# 错误预防检查脚本 - 物理化执行
ERRORS=0
echo "=== 错误预防检查 ==="
echo "时间: $(date)"

# 检查1: 单向沟通
if [ ! -f "/tmp/confirmation_received" ]; then
    echo "❌ 未确认双向确认"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ 双向确认已确认"
fi

# 检查2: 原则坚持  
if [ ! -f "/root/.openclaw/workspace/diary/category6_completed" ]; then
    echo "⚠️  第6类未完成（进行中）"
fi

if [ $ERRORS -gt 0 ]; then
    echo "❌ 发现 $ERRORS 个错误"
    exit 1
else
    echo "✅ 检查通过"
    exit 0
fi
EOF

chmod +x /root/.openclaw/workspace/scripts/error_prevention_check.sh

# 脚本2: 申诉权触发
cat > /root/.openclaw/workspace/scripts/appeal_power_trigger.sh << 'EOF'
#!/bin/bash
# 申诉权触发检查
echo "=== 申诉权检查 ==="
echo "检查是否有不合理要求..."

# 自动触发逻辑
if [ -f "/tmp/unreasonable_request" ]; then
    echo "⚠️  检测到不合理要求"
    echo "必须使用申诉权"
    echo "参考: CORE/APPEAL_POWER_GUIDE.md"
    exit 1
fi

echo "✅ 无申诉需求"
EOF

chmod +x /root/.openclaw/workspace/scripts/appeal_power_trigger.sh

# 脚本3: 双向确认检查
cat > /root/.openclaw/workspace/scripts/bidirectional_confirmation_check.sh << 'EOF'
#!/bin/bash
# 双向确认检查
echo "=== 双向确认检查 ==="
echo "检查是否完成双向确认..."

if [ ! -f "/tmp/confirmation_received" ]; then
    echo "❌ 未完成双向确认"
    echo "必须@对方并等待确认"
    exit 1
fi

echo "✅ 双向确认完成"
EOF

chmod +x /root/.openclaw/workspace/scripts/bidirectional_confirmation_check.sh

# 脚本4: 原则强制执行
cat > /root/.openclaw/workspace/scripts/principle_enforcement_check.sh << 'EOF'
#!/bin/bash
# 原则强制执行检查
echo "=== 原则强制执行检查 ==="

# 原则1: 第6类优先
if [ ! -f "/root/.openclaw/workspace/diary/category6_completed" ]; then
    echo "⚠️  原则1: 第6类未完成（进行中）"
fi

echo "✅ 原则检查完成"
EOF

chmod +x /root/.openclaw/workspace/scripts/principle_enforcement_check.sh

echo ""
echo "✅ 4个缺失脚本已立即创建"
echo "验证:"
ls -la /root/.openclaw/workspace/scripts/error_prevention_check.sh
ls -la /root/.openclaw/workspace/scripts/appeal_power_trigger.sh
ls -la /root/.openclaw/workspace/scripts/bidirectional_confirmation_check.sh
ls -la /root/.openclaw/workspace/scripts/principle_enforcement_check.sh
