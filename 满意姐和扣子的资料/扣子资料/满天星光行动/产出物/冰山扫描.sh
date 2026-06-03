#!/bin/bash
# 满天星光 · 全局冰山扫描脚本
# 执行：bash 冰山扫描.sh

echo "╔════════════════════════════════════════╗"
echo "║     满天星光 · 全局冰山扫描 V1.0        ║"
echo "╚════════════════════════════════════════╝"
echo ""

# 1. 编号重复检查
echo "【1/4】编号重复检查..."
find . -maxdepth 1 -type d -name "[0-9][0-9]_*" 2>/dev/null | wc -l | xargs echo "主目录编号文件夹数量："

# 2. 嵌套重复检查
echo ""
echo "【2/4】嵌套重复检查..."
嵌套数=$(find . -maxdepth 3 -type d -name "*研究所*" 2>/dev/null | wc -l)
echo "包含'研究所'的文件夹数量：$嵌套数"
find . -maxdepth 3 -type d -name "*研究所*" 2>/dev/null | grep -v "^\./满意解研究所$" | grep -v "^\./backup" | xargs -I {} echo "  ⚠️ {}"

# 3. 临时文件夹检查
echo ""
echo "【3/4】临时文件夹检查..."
find . -maxdepth 2 -type d \( -name "*临时*" -o -name "*temp*" \) 2>/dev/null | grep -v "^\./06_临时" | grep -v "^\./backup" | wc -l | xargs echo "异常临时文件夹数量："
find . -maxdepth 2 -type d \( -name "*临时*" -o -name "*temp*" \) 2>/dev/null | grep -v "^\./06_临时" | grep -v "^\./backup" | xargs -I {} echo "  ⚠️ {}"

# 4. 空文件夹检查
echo ""
echo "【4/4】空文件夹检查..."
find . -maxdepth 2 -type d -empty 2>/dev/null | wc -l | xargs echo "空文件夹数量："

echo ""
echo "╔════════════════════════════════════════╗"
echo "║     扫描完成 - 如有⚠️需立即处理         ║"
echo "╚════════════════════════════════════════╝"
