#!/bin/bash
# 读取恢复摘要，生成Claw可理解的上下文
# 零Token恢复协议

SUMMARY_FILE="/root/.openclaw/workspace/.claw-resume-summary.json"
CHECKPOINT_DIR="$HOME/.openclaw/immortal-state/checkpoints"

if [ -f "$SUMMARY_FILE" ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              🧬 零Token状态恢复系统                          ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    
    # 解析JSON显示关键信息
    python3 -c "
import json
import sys

try:
    with open('$SUMMARY_FILE', 'r', encoding='utf-8') as f:
        s = json.load(f)
    
    print('📂 上次会话状态')
    print('─' * 50)
    print(f\"生成时间: {s.get('generated_at', 'N/A')[:19]}\")
    print(f\"会话ID: {s.get('session_id', 'N/A')}\")
    print()
    
    # 待办任务
    tasks = s.get('pending_tasks', [])
    if tasks:
        print('📝 中断前待办:')
        for i, t in enumerate(tasks[:5], 1):
            print(f'  {i}. {t[:60]}{\"...\" if len(t) > 60 else \"\"}')
        print()
    
    # 最近文件
    files = s.get('recent_files', [])
    if files:
        print('📄 最近修改文件:')
        for f in files[:5]:
            if f.strip():
                fname = f.split('/')[-1]
                print(f'  • {fname}')
        print()
    
    # 检查点信息
    cpt = s.get('checkpoints_available', 0)
    if cpt > 0:
        print(f'💾 可用检查点: {cpt} 个')
        print('   如需恢复文件状态，运行: openclaw-state restore')
    
    print()
    print('─' * 50)
    print('✅ 状态摘要加载完成 (零Token消耗)')
    
except Exception as e:
    print(f'读取摘要出错: {e}')
    sys.exit(1)
"
    echo ""
else
    echo "✨ 无恢复摘要，正常启动"
fi
