#!/bin/bash
# 满意解基因内化检查脚本
# 虚假完成机制整改 - M003

echo "=== 满意解基因内化检查 ==="
echo ""
echo "检查SOUL.md中是否包含满意解基因定义:"
echo ""

if grep -q "满意解基因\|满意妞\|防愚蠢" /root/.openclaw/workspace/SOUL.md 2>/dev/null; then
    echo "✅ SOUL.md包含满意解基因定义"
else
    echo "❌ SOUL.md缺少满意解基因定义"
fi

echo ""
echo "检查是否触发内化SOP:"
echo "  [ ] 识别到内化需求？"
echo "  [ ] 固写到SOUL.md/USER.md？"
echo "  [ ] 物理化创建文件？"
echo "  [ ] 建立标准和检查清单？"
echo "  [ ] 创建自动化验证脚本？"
echo "  [ ] 创建执行日志？"
echo "  [ ] 创建Checkpoint机制？"
echo "  [ ] 创建极端事件恢复机制？"
echo "  [ ] 验证恢复是否成功？"
echo "  [ ] 每日/周/月/季回顾更新？"

echo ""
echo "检查完成度:"
grep -c "内化\|固化\|物理化" /root/.openclaw/workspace/SOUL.md 2>/dev/null || echo "0"
