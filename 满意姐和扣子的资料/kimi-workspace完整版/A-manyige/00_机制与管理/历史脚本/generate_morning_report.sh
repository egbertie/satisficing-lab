#!/bin/bash
# 每日晨报生成自动化脚本
# 用法: ./generate_morning_report.sh [日期，默认为今天]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="/root/.openclaw/workspace"
DATE=${1:-$(date +%Y-%m-%d)}

echo "🌅 满意解晨报生成脚本"
echo "======================"
echo "日期: $DATE"
echo ""

cd "$SCRIPT_DIR" || exit 1

# 运行生成器
python3 daily_morning_report_generator.py --date "$DATE" --print

echo ""
echo "======================"
echo "✅ 晨报生成完成"
echo "📁 输出位置: A满意哥专属文件夹/01_🔥今日重点/晨报_${DATE}.md"
