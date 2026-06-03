#!/bin/bash
# 满意妞自我深度洞察模块检查脚本

echo "=== 满意妞自我深度洞察模块检查 ==="
echo ""

# 检查模块文件
echo "1. 模块文件存在性:"
if [ -f "/root/.openclaw/workspace/skills/self-deep-insight/self_deep_insight.py" ]; then
    echo "   ✅ self_deep_insight.py 存在"
    lines=$(wc -l < /root/.openclaw/workspace/skills/self-deep-insight/self_deep_insight.py)
    echo "      代码行数: $lines"
else
    echo "   ❌ self_deep_insight.py 不存在"
fi

# 检查关键方法
echo ""
echo "2. 关键方法存在性:"
grep -q "generate_insight" /root/.openclaw/workspace/skills/self-deep-insight/self_deep_insight.py 2>/dev/null && echo "   ✅ generate_insight 方法存在" || echo "   ❌ generate_insight 方法缺失"
grep -q "_identify_pattern" /root/.openclaw/workspace/skills/self-deep-insight/self_deep_insight.py 2>/dev/null && echo "   ✅ L2模式识别存在" || echo "   ❌ L2模式识别缺失"
grep -q "_analyze_root_cause" /root/.openclaw/workspace/skills/self-deep-insight/self_deep_insight.py 2>/dev/null && echo "   ✅ L3根因分析存在" || echo "   ❌ L3根因分析缺失"
grep -q "_trigger_internalization" /root/.openclaw/workspace/skills/self-deep-insight/self_deep_insight.py 2>/dev/null && echo "   ✅ 内化触发存在" || echo "   ❌ 内化触发缺失"

# 检查目录
echo ""
echo "3. 洞察保存目录:"
if [ -d "/root/.openclaw/workspace/diary/insights" ]; then
    count=$(ls /root/.openclaw/workspace/diary/insights/ 2>/dev/null | wc -l)
    echo "   ✅ diary/insights/ 目录存在 ($count 个洞察文件)"
else
    echo "   ⚠️ diary/insights/ 目录不存在（首次运行时创建）"
fi

echo ""
echo "4. 闭环完整性检查:"
echo "  [ ] 每次任务后自动生成洞察？"
echo "  [ ] 洞察保存到diary/insights/？"
echo "  [ ] 触发内化流程（SOUL.md更新建议）？"
echo "  [ ] 蓝军审计调用此模块？"
