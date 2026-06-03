#!/bin/bash
# ============================================================
# 智能 Git Push — 双经济约束动态调度
# ============================================================
# 原则:
#   Token经济: 省着用，只在需要时push
#   时间经济: 别太频繁，也别太久不push（风险累积）
#
# 机制:
#   - 检测到文件变更 → 记录时间，但不立即push
#   - 等待冷却期(cooldown)后再push，期间新变更重置冷却
#   - 最小间隔7分钟，最大强制间隔2小时
#   - 夜间(01:00-07:00)降频: 最小30分钟
#   - 每天最多push 20次(token硬预算)
# ============================================================

WORKSPACE="/Users/egbertielau/.openclaw/workspace"
STATE_FILE="$WORKSPACE/.git-push-state.json"
LOG_FILE="$WORKSPACE/.fb-launchd.log"

# 默认参数
MIN_INTERVAL_DAY=420       # 白天最小间隔(秒)=7分钟
MIN_INTERVAL_NIGHT=1800    # 夜间最小间隔=30分钟
MAX_INTERVAL=7200          # 最大强制间隔=2小时
DAILY_MAX_PUSHES=20        # 每日最多push次数

cd "$WORKSPACE"

# ===== 读取/初始化状态 =====
now=$(date +%s)
today=$(date +%Y-%m-%d)
hour=$(date +%H)

if [ -f "$STATE_FILE" ]; then
  last_push=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('last_push',0))" 2>/dev/null || echo 0)
  last_change=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('last_change',0))" 2>/dev/null || echo 0)
  push_day=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('day',''))" 2>/dev/null || echo "")
  push_count_today=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('count',0))" 2>/dev/null || echo 0)
  pending=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('pending','false'))" 2>/dev/null || echo "false")
else
  last_push=0; last_change=0; push_day=""; push_count_today=0; pending="false"
fi

# 跨天重置计数
if [ "$push_day" != "$today" ]; then
  push_count_today=0
fi

save_state() {
  python3 -c "
import json
json.dump({
  'last_push': $1,
  'last_change': $2,
  'day': '$today',
  'count': $3,
  'pending': '$4'
}, open('$STATE_FILE','w'))
" 2>/dev/null
}

# ===== 确定最小间隔 =====
if [ "$hour" -ge 1 ] && [ "$hour" -lt 7 ]; then
  MIN_INTERVAL=$MIN_INTERVAL_NIGHT  # 夜间
else
  MIN_INTERVAL=$MIN_INTERVAL_DAY    # 白天
fi

# ===== 检测变更 =====
has_changes=false
# 检查非site子模块的变更
git update-index -q --refresh 2>/dev/null
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
  has_changes=true
fi
# 检查untracked
if [ -n "$(git ls-files --others --exclude-standard 2>/dev/null)" ]; then
  has_changes=true
fi

if $has_changes; then
  last_change=$now
  pending="true"
  save_state $last_push $last_change $push_count_today "true"
  echo "[$(date '+%H:%M')] Changes detected, pending push" >> "$LOG_FILE"
fi

# ===== 判断是否该push =====
should_push=false
reason=""

# 条件1: 超过最大强制间隔 → 必须push (防风险)
if [ $((now - last_push)) -ge $MAX_INTERVAL ] && [ "$pending" = "true" ]; then
  should_push=true
  reason="max_interval_forced"
fi

# 条件2: 有pending变更 + 超过最小间隔 + 未超日预算
if [ "$pending" = "true" ] && [ $((now - last_change)) -ge $MIN_INTERVAL ] && [ $push_count_today -lt $DAILY_MAX_PUSHES ]; then
  should_push=true
  reason="cooldown_met"
fi

# ===== 执行push =====
if $should_push; then
  echo "[$(date '+%H:%M')] Pushing ($reason) count=$((push_count_today+1))/$DAILY_MAX_PUSHES" >> "$LOG_FILE"

  # git add + commit + push
  git add -A 2>/dev/null
  git add site/ 2>/dev/null

  if git diff --cached --quiet 2>/dev/null && git diff --quiet 2>/dev/null; then
    # 无实际变更，只更新状态
    pending="false"
    save_state $now $last_change $push_count_today "false"
    exit 0
  fi

  commit_ok=false
  if git commit --no-verify -m "auto: 智能同步 $(date '+%m-%d %H:%M') [$reason]" 2>&1; then
    commit_ok=true
  else
    echo "[$(date '+%H:%M')] Commit failed (maybe nothing to commit)" >> "$LOG_FILE"
  fi

  if $commit_ok; then
    # 先尝试直接push，失败则pull --rebase后重试
    push_output=$(git push origin main 2>&1)
    push_rc=$?

    if [ $push_rc -ne 0 ]; then
      echo "[$(date '+%H:%M')] Push rejected, trying pull --rebase..." >> "$LOG_FILE"
      echo "$push_output" | tail -2 >> "$LOG_FILE"
      if git pull --rebase origin main 2>&1 >> "$LOG_FILE"; then
        if git push origin main 2>&1 | tail -1 >> "$LOG_FILE"; then
          push_rc=0
        fi
      fi
    else
      echo "$push_output" | tail -1 >> "$LOG_FILE"
    fi

    if [ $push_rc -eq 0 ]; then
      last_push=$now
      push_count_today=$((push_count_today + 1))
      pending="false"
      save_state $last_push $last_change $push_count_today "false"
      echo "[$(date '+%H:%M')] Push OK. Today: $push_count_today/$DAILY_MAX_PUSHES" >> "$LOG_FILE"
    else
      # Push失败：保留pending标记，下次重试
      last_change=$now
      save_state $last_push $last_change $push_count_today "true"
      echo "[$(date '+%H:%M')] Push FAILED (will retry). Today: $push_count_today/$DAILY_MAX_PUSHES" >> "$LOG_FILE"
    fi
  fi
fi