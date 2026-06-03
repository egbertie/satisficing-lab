#!/bin/bash
# 零空置强制执行器 - Shell包装脚本 (S4)
# 7标准完全合规版本

set -e

SKILL_DIR="/root/.openclaw/workspace/skills/zero-idle-enforcer"
PYTHON="python3"

show_help() {
    echo "零空置强制执行器 V5.0"
    echo ""
    echo "用法: $0 <command>"
    echo ""
    echo "命令:"
    echo "  check      执行零空置检查"
    echo "  status     查看当前状态"
    echo "  report     生成执行报告"
    echo "  test       运行对抗测试 (S7)"
    echo "  block      临时阻断补位"
    echo "  unblock    解除阻断"
    echo "  help       显示帮助"
    echo ""
    echo "示例:"
    echo "  $0 status"
    echo "  $0 check"
    echo "  $0 block"
}

case "${1:-help}" in
    check)
        echo "🚀 执行零空置检查..."
        $PYTHON $SKILL_DIR/enforcer.py enforce
        ;;
    
    status)
        echo "📊 获取当前状态..."
        $PYTHON $SKILL_DIR/enforcer.py status
        ;;
    
    report)
        echo "📈 生成执行报告..."
        $PYTHON $SKILL_DIR/enforcer.py report
        ;;
    
    test)
        echo "🧪 运行对抗测试..."
        $PYTHON $SKILL_DIR/scripts/adversarial-test.py
        ;;
    
    block)
        BLOCKER_FILE="/root/.openclaw/workspace/memory/zero-idle-blocker.json"
        BLOCK_UNTIL=$(($(date +%s) + 3600))
        echo "{\"blocked\": true, \"reason\": \"manual\", \"until\": $BLOCK_UNTIL}" > "$BLOCKER_FILE"
        echo "🚫 已临时阻断零空置补位 (1小时)"
        echo "   阻断至: $(date -d @$BLOCK_UNTIL '+%Y-%m-%d %H:%M:%S')"
        ;;
    
    unblock)
        BLOCKER_FILE="/root/.openclaw/workspace/memory/zero-idle-blocker.json"
        if [ -f "$BLOCKER_FILE" ]; then
            rm -f "$BLOCKER_FILE"
            echo "✅ 已解除阻断"
        else
            echo "ℹ️  未处于阻断状态"
        fi
        ;;
    
    help|--help|-h)
        show_help
        ;;
    
    *)
        echo "❌ 未知命令: $1"
        show_help
        exit 1
        ;;
esac
