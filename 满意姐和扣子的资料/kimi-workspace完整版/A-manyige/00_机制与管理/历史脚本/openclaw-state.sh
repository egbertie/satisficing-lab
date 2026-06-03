#!/bin/bash
# Claw状态管理工具
# 用法: openclaw-state {list|restore|clean|summary}

COMMAND=$1
CHECKPOINT_DIR="$HOME/.openclaw/immortal-state/checkpoints"

mkdir -p "$CHECKPOINT_DIR"

case $COMMAND in
    list|ls)
        echo "📂 可用检查点 (最多20个):"
        echo ""
        ls -t "$CHECKPOINT_DIR"/*.meta 2>/dev/null | head -20 | while read metafile; do
            basename=$(basename "$metafile" .meta)
            if [ -f "$CHECKPOINT_DIR/${basename}.tar.gz" ]; then
                # 解析元数据
                python3 -c "
import json
import sys
try:
    with open('$metafile') as f:
        m = json.load(f)
    size_mb = m.get('size', 0) / 1024 / 1024
    print(f\"  {m['id']}\")
    print(f\"    时间: {m['timestamp'][:19]} | 大小: {size_mb:.1f}MB | 文件: {m.get('files', 0)}\")
except:
    print(f\"  {basename} (元数据解析失败)\")
"
            fi
        done
        echo ""
        echo "💡 使用: openclaw-state restore [检查点ID] 恢复状态"
        ;;
        
    restore|rs)
        CHECKPOINT_ID=$2
        
        if [ -z "$CHECKPOINT_ID" ]; then
            # 使用最新的
            LATEST_META=$(ls -t "$CHECKPOINT_DIR"/cpt-*.meta 2>/dev/null | head -1)
            if [ -z "$LATEST_META" ]; then
                echo "❌ 无可用检查点"
                exit 1
            fi
            CHECKPOINT_ID=$(basename "$LATEST_META" .meta)
            echo "🔄 使用最新检查点: $CHECKPOINT_ID"
        fi
        
        ARCHIVE="$CHECKPOINT_DIR/${CHECKPOINT_ID}.tar.gz"
        
        if [ ! -f "$ARCHIVE" ]; then
            echo "❌ 检查点不存在: $ARCHIVE"
            echo "可用检查点:"
            ls -t "$CHECKPOINT_DIR"/cpt-*.tar.gz 2>/dev/null | head -5
            exit 1
        fi
        
        echo "🔄 恢复检查点: $CHECKPOINT_ID"
        echo "   正在解压..."
        
        # 创建临时目录
        TMPDIR=$(mktemp -d)
        tar xzf "$ARCHIVE" -C "$TMPDIR" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            # 恢复workspace
            if [ -d "$TMPDIR/workspace" ]; then
                rsync -av --delete "$TMPDIR/workspace/" "$HOME/.openclaw/workspace/" 2>/dev/null
                echo "   ✅ Workspace已恢复"
            fi
            # 恢复config
            if [ -d "$TMPDIR/config" ]; then
                rsync -av "$TMPDIR/config/" "$HOME/.openclaw/config/" 2>/dev/null
                echo "   ✅ Config已恢复"
            fi
            rm -rf "$TMPDIR"
            echo ""
            echo "✅ 状态恢复完成"
            echo "💡 建议: 运行 'scripts/resume-from-summary.sh' 查看上下文"
        else
            echo "❌ 解压失败"
            rm -rf "$TMPDIR"
            exit 1
        fi
        ;;
        
    clean|cl)
        echo "🧹 清理旧检查点..."
        BEFORE=$(ls "$CHECKPOINT_DIR"/cpt-*.tar.gz 2>/dev/null | wc -l)
        
        # 保留最近20个
        ls -t "$CHECKPOINT_DIR"/cpt-*.tar.gz 2>/dev/null | tail -n +21 | xargs -r rm -vf
        ls -t "$CHECKPOINT_DIR"/cpt-*.meta 2>/dev/null | tail -n +21 | xargs -r rm -vf
        
        AFTER=$(ls "$CHECKPOINT_DIR"/cpt-*.tar.gz 2>/dev/null | wc -l)
        REMOVED=$((BEFORE - AFTER))
        
        echo "✅ 清理完成，移除 $REMOVED 个旧检查点，保留 $AFTER 个"
        ;;
        
    summary|sm)
        # 生成新的摘要
        python3 "$HOME/.openclaw/workspace/scripts/generate-resume-summary.py"
        ;;
        
    *)
        echo "Claw状态管理工具 - 零Token状态永生系统"
        echo ""
        echo "用法:"
        echo "  openclaw-state list      列出可用检查点"
        echo "  openclaw-state restore   恢复到最新检查点"
        echo "  openclaw-state restore [ID] 恢复到指定检查点"
        echo "  openclaw-state clean     清理旧检查点（保留20个）"
        echo "  openclaw-state summary   生成恢复摘要"
        echo ""
        echo "检查点目录: $CHECKPOINT_DIR"
        ;;
esac
