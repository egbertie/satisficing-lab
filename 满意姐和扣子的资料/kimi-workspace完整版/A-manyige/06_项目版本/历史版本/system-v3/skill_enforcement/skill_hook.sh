#!/bin/bash
# Skill强制检查钩子 - 系统级集成
# 满意妞直接执行 - 2026-03-31
# 
# 此脚本应在每次执行命令前调用
# 集成到bashrc或作为pre-exec钩子

COMMAND="$@"
WORKSPACE="/root/.openclaw/workspace"
ENFORCER="${WORKSPACE}/system-v3/skill_enforcement/skill_enforcer.py"
LOG_FILE="${WORKSPACE}/logs/skill_enforcement/hook.log"

# 记录调用
mkdir -p "$(dirname "$LOG_FILE")"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] HOOK: $COMMAND" >> "$LOG_FILE"

# 检查是否应该强制Skill
if [[ "$COMMAND" == *"python"* ]] && [[ "$COMMAND" == *".py"* ]]; then
    # 检测是否是通过Skill调用
    if [[ "$COMMAND" == *"skills/"* ]] || [[ "$COMMAND" == *"skill"* ]]; then
        # 可能是Skill调用，允许
        exit 0
    fi
    
    # 检测是否涉及强制Skill任务
    # 这里可以调用Python enforcer进行更复杂的检测
    
    # 简单规则：如果包含某些关键词，警告
    if [[ "$COMMAND" == *"ingest"* ]] || \
       [[ "$COMMAND" == *"fetch"* ]] || \
       [[ "$COMMAND" == *"calendar"* ]] || \
       [[ "$COMMAND" == *"task"* ]] || \
       [[ "$COMMAND" == *"upload"* ]]; then
        
        echo "⚠️  警告: 此命令可能需要通过Skill框架执行"
        echo "    命令: $COMMAND"
        echo "    建议: 使用 openclaw skill run <skill-name>"
        echo ""
        
        # 记录警告
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: Possible skill bypass - $COMMAND" >> "$LOG_FILE"
    fi
fi

exit 0
