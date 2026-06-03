#!/bin/bash
# 蓝军深度洞察审计模块检查脚本

echo "=== 蓝军深度洞察审计模块检查 ==="
echo ""

# 检查模块文件
echo "1. 模块文件存在性:"
if [ -f "/root/.openclaw/workspace/skills/blue-army-deep-insight-auditor/deep_insight_auditor.py" ]; then
    echo "   ✅ deep_insight_auditor.py 存在"
    lines=$(wc -l < /root/.openclaw/workspace/skills/blue-army-deep-insight-auditor/deep_insight_auditor.py)
    echo "      代码行数: $lines"
else
    echo "   ❌ deep_insight_auditor.py 不存在"
fi

# 检查关键方法
echo ""
echo "2. 关键方法存在性:"
grep -q "audit_file" /root/.openclaw/workspace/skills/blue-army-deep-insight-auditor/deep_insight_auditor.py 2>/dev/null && echo "   ✅ audit_file 方法存在" || echo "   ❌ audit_file 方法缺失"
grep -q "audit_directory" /root/.openclaw/workspace/skills/blue-army-deep-insight-auditor/deep_insight_auditor.py 2>/dev/null && echo "   ✅ audit_directory 方法存在" || echo "   ❌ audit_directory 方法缺失"
grep -q "_has_root_cause_depth" /root/.openclaw/workspace/skills/blue-army-deep-insight-auditor/deep_insight_auditor.py 2>/dev/null && echo "   ✅ L3深度检查存在" || echo "   ❌ L3深度检查缺失"
grep -q "_has_executable_guidance" /root/.openclaw/workspace/skills/blue-army-deep-insight-auditor/deep_insight_auditor.py 2>/dev/null && echo "   ✅ L5可执行性检查存在" || echo "   ❌ L5可执行性检查缺失"

# 运行审计测试
echo ""
echo "3. 审计功能测试:"
cd /root/.openclaw/workspace
if python3 skills/blue-army-deep-insight-auditor/deep_insight_auditor.py skills/super-knowledge-ingest/ 2>/dev/null | grep -q "深度洞察完整"; then
    echo "   ✅ 审计功能正常（super-knowledge-ingest通过）"
else
    echo "   ⚠️ 审计功能待验证"
fi

echo ""
echo "4. 闭环完整性检查:"
echo "  [ ] 蓝军审计流程调用此模块？"
echo "  [ ] 未通过审计自动exit 1阻断？"
echo "  [ ] 审计报告生成并保存？"
echo "  [ ] 定期全量Skill审计（每周）？"
