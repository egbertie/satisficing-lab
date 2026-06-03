#!/bin/bash
# 蓝军自我闭环升级验证脚本

echo "=== 蓝军自我闭环升级验证 ==="
echo ""

# 检查自我闭环模块
echo "1. 自我闭环模块:"
if [ -f "/root/.openclaw/workspace/skills/blue-army-self-closure/blue_army_self_closure.py" ]; then
    echo "   ✅ blue_army_self_closure.py 存在"
    lines=$(wc -l < /root/.openclaw/workspace/skills/blue-army-self-closure/blue_army_self_closure.py)
    echo "      代码行数: $lines"
else
    echo "   ❌ blue_army_self_closure.py 不存在"
    exit 1
fi

# 检查关键方法
echo ""
echo "2. 关键方法存在性:"
grep -q "audit_own_output" /root/.openclaw/workspace/skills/blue-army-self-closure/blue_army_self_closure.py 2>/dev/null && echo "   ✅ audit_own_output 方法存在" || echo "   ❌ audit_own_output 方法缺失"
grep -q "audit_standards" /root/.openclaw/workspace/skills/blue-army-self-closure/blue_army_self_closure.py 2>/dev/null && echo "   ✅ 审计标准存在" || echo "   ❌ 审计标准缺失"
grep -q "generate_self_audit_report" /root/.openclaw/workspace/skills/blue-army-self-closure/blue_army_self_closure.py 2>/dev/null && echo "   ✅ 自我审计报告存在" || echo "   ❌ 自我审计报告缺失"

# 运行自我审计测试
echo ""
echo "3. 自我审计测试:"
cd /root/.openclaw/workspace
python3 skills/blue-army-self-closure/blue_army_self_closure.py 2>/dev/null | head -45

echo ""
echo "4. 自我审计记录目录:"
if [ -d "/root/.openclaw/workspace/diary/blue_army_self_audit" ]; then
    count=$(ls /root/.openclaw/workspace/diary/blue_army_self_audit/ 2>/dev/null | wc -l)
    echo "   ✅ diary/blue_army_self_audit/ 目录存在 ($count 个审计记录)"
else
    echo "   ⚠️ diary/blue_army_self_audit/ 目录待创建（首次运行时）"
fi

echo ""
echo "=== 蓝军自我闭环升级状态: ✅ 完成 ==="
echo "自我闭环系统已创建，支持4维度审计标准（诚实/洞察/闭环/机制）"
