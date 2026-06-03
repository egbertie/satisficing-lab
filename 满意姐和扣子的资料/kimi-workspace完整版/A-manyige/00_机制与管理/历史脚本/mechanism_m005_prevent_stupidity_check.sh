#!/bin/bash
# 防愚蠢→能动性机制检查脚本
# 虚假完成机制整改 - M005

echo "=== 防愚蠢→能动性机制检查 ==="
echo ""

# 检查错误记录
echo "1. 错误记录系统:"
ls /root/.openclaw/workspace/diary/errors/ 2>/dev/null | wc -l
echo "   个错误记录文件"

# 检查复发预防
echo ""
echo "2. 复发预防机制:"
grep -r "复发\|prevent\|recurrence" /root/.openclaw/workspace/CORE/*.md 2>/dev/null | wc -l
echo "   个预防机制引用"

# 检查能力提升记录
echo ""
echo "3. 能力提升记录:"
grep -c "能力\|成长\|进化" /root/.openclaw/workspace/SOUL.md 2>/dev/null || echo "   0"

echo ""
echo "能动性度量标准:"
echo "  [ ] 主动发现问题？"
echo "  [ ] 主动修复问题？"
echo "  [ ] 主动进化系统？"
echo "  [ ] 错误复发率 < 10%？"
echo "  [ ] 信任积分持续增长？"
