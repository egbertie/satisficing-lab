#!/bin/bash
# 6 Worker蜂群机制检查脚本
# 虚假完成机制整改 - M006

echo "=== 6 Worker蜂群机制检查 ==="
echo ""

# 检查Worker定义
echo "1. Worker定义文件:"
grep -l "Meta-Strategist\|Supervisor-Biz\|Supervisor-Tech\|Worker-Analysis\|Worker-Execution\|Worker-Creative" /root/.openclaw/workspace/SOUL.md 2>/dev/null | wc -l
echo "   个Worker定义"

# 检查激活记录
echo ""
echo "2. Worker激活记录:"
grep -c "Worker.*激活\|激活.*Worker" /root/.openclaw/workspace/memory/2026-03-31.md 2>/dev/null || echo "   0次激活"

# 检查协调机制
echo ""
echo "3. 子代理协调:"
ls /root/.openclaw/workspace/diary/cat6_execution/ 2>/dev/null | wc -l
echo "   个执行记录"

echo ""
echo "6 Worker蜂群要求:"
echo "  [ ] Meta-Strategist全局编排？"
echo "  [ ] Supervisor监督验证？"
echo "  [ ] Worker具体执行？"
echo "  [ ] 层级协调机制？"
echo "  [ ] 每任务前Worker选择？"
