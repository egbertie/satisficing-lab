#!/bin/bash
# Auto Git Commit Script - Secure Version
# 深度记忆: GITHUB_TOKEN已固化，无需重复询问，除非Token失效

REPO_DIR="/root/.openclaw/workspace"
LOCK_FILE="/tmp/auto-git-commit.lock"
LOG_FILE="/tmp/auto-git-commit.log"

# 加载环境变量（优先从文件，否则硬编码）
if [ -f "$REPO_DIR/.env.github" ]; then
    source "$REPO_DIR/.env.github"
fi

# 深度记忆: Token固化（2026-03-26验证有效）
GITHUB_TOKEN="${GITHUB_TOKEN:-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}"
GITHUB_USER="${GITHUB_USER:-egbertie}"

# 检查锁文件（防止并发）
if [ -f "$LOCK_FILE" ]; then
    PID=$(cat "$LOCK_FILE" 2>/dev/null)
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "[$(date)] Another instance is running (PID: $PID)" >> "$LOG_FILE"
        exit 0
    fi
fi
    PID=$(cat "$LOCK_FILE" 2>/dev/null)
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "[$(date)] Another instance is running (PID: $PID)" >> "$LOG_FILE"
        exit 0
    fi


# 创建锁文件
echo $$ > "$LOCK_FILE"

# 清理函数
cleanup() {
    rm -f "$LOCK_FILE"
}
trap cleanup EXIT

cd "$REPO_DIR" || exit 1

# 检查是否有更改
if [ -z "$(git status --porcelain)" ]; then
    echo "[$(date)] No changes to commit" >> "$LOG_FILE"
    exit 0
fi

# 配置git（仅当前仓库）
git config user.email "kimi@satisficing.institute"
git config user.name "Kimi Claw"

# 添加所有更改
git add -A

# 提交（包含统计信息）
CHANGE_COUNT=$(git diff --cached --numstat | wc -l)
FILE_COUNT=$(git diff --cached --name-only | wc -l)
COMMIT_MSG="Auto-commit: $(date '+%Y-%m-%d %H:%M') - $FILE_COUNT files, $CHANGE_COUNT changes"

git commit -m "$COMMIT_MSG" >> "$LOG_FILE" 2>&1

# 如果有Token，则推送
if [ -n "$GITHUB_TOKEN" ]; then
    # 临时设置远程URL（带token）
    git remote set-url origin "https://egbertie:${GITHUB_TOKEN}@github.com/egbertie/satisficing-institute.git"
    git push origin main >> "$LOG_FILE" 2>&1
    PUSH_STATUS=$?
    # 恢复远程URL（移除token）
    git remote set-url origin "https://github.com/egbertie/satisficing-institute.git"
    
    if [ $PUSH_STATUS -eq 0 ]; then
        echo "[$(date)] ✅ Push successful" >> "$LOG_FILE"
    else
        echo "[$(date)] ❌ Push failed (code: $PUSH_STATUS)" >> "$LOG_FILE"
    fi
else
    echo "[$(date)] ⚠️ No GITHUB_TOKEN, commit only (no push)" >> "$LOG_FILE"
fi

echo "[$(date)] Done" >> "$LOG_FILE"
