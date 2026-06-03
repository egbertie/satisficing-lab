#!/bin/bash
################################################################################
# Weekly Essential Snapshot - 精简灾备快照
# 蓝军执行 | 2026-04-10
# 双经济要求版本：不建平行目录，只补 Git 遗漏的关键状态文件
################################################################################

set -euo pipefail

WORKSPACE="/root/.openclaw/workspace"
SNAPSHOT_DIR="${WORKSPACE}/backups/essential-snapshot"
DATE_STR=$(date +%Y%m%d-%H%M%S)
SNAPSHOT_NAME="essential-${DATE_STR}"
SNAPSHOT_PATH="${SNAPSHOT_DIR}/${SNAPSHOT_NAME}"
MAX_SNAPSHOTS=2

echo "[$(date -Iseconds)] 开始精简灾备快照: ${SNAPSHOT_NAME}"

mkdir -p "${SNAPSHOT_PATH}"

# 1. 元协议层（身份与规则）
cp "${WORKSPACE}/SOUL.md" "${SNAPSHOT_PATH}/" 2>/dev/null || true
cp "${WORKSPACE}/AGENTS.md" "${SNAPSHOT_PATH}/" 2>/dev/null || true
cp "${WORKSPACE}/USER.md" "${SNAPSHOT_PATH}/" 2>/dev/null || true
cp "${WORKSPACE}/TOOLS.md" "${SNAPSHOT_PATH}/" 2>/dev/null || true
cp "${WORKSPACE}/HEARTBEAT.md" "${SNAPSHOT_PATH}/" 2>/dev/null || true
cp "${WORKSPACE}/MEMORY.md" "${SNAPSHOT_PATH}/" 2>/dev/null || true
cp "${WORKSPACE}/BOOTSTRAP.md" "${SNAPSHOT_PATH}/" 2>/dev/null || true

# 2. 动态记忆层（Git 不跟踪的每日记录）
mkdir -p "${SNAPSHOT_PATH}/memory"
find "${WORKSPACE}/memory" -maxdepth 1 -type f -name "*.md" -exec cp {} "${SNAPSHOT_PATH}/memory/" \;
find "${WORKSPACE}/memory" -maxdepth 1 -type f -name "*.json" -exec cp {} "${SNAPSHOT_PATH}/memory/" \;

# 3. 环境配置（不含密钥内容，只记录存在性）
mkdir -p "${SNAPSHOT_PATH}/env"
for f in "${WORKSPACE}/.env" "${WORKSPACE}/.env.local" "${WORKSPACE}/.env.lexiang"; do
  if [ -f "$f" ]; then
    basename_f=$(basename "$f")
    echo "exists=true" > "${SNAPSHOT_PATH}/env/${basename_f}.meta"
  fi
done

# 4. 任务与追踪文件
cp "${WORKSPACE}/TASK_MASTER.md" "${SNAPSHOT_PATH}/" 2>/dev/null || true
cp "${WORKSPACE}/token_economic_ledger.json" "${SNAPSHOT_PATH}/" 2>/dev/null || true

# 5. 生成快照元数据
SIZE=$(du -sh "${SNAPSHOT_PATH}" | cut -f1)
cat > "${SNAPSHOT_PATH}/snapshot-meta.json" <<EOF
{
  "snapshot_id": "${SNAPSHOT_NAME}",
  "created_at": "$(date -Iseconds)",
  "source": "weekly_essential_snapshot.sh",
  "size": "${SIZE}",
  "note": "本快照只包含 Git 未完整覆盖的关键状态文件。完整代码恢复请使用: git clone / git pull"
}
EOF

# 6. 清理旧快照，只保留最近 N 个
cd "${SNAPSHOT_DIR}"
ls -t | tail -n +$((MAX_SNAPSHOTS + 1)) | xargs -r rm -rf

echo "[$(date -Iseconds)] 快照完成: ${SNAPSHOT_PATH} (${SIZE})"
echo "[$(date -Iseconds)] 保留快照数: $(ls -1 | wc -l)"
