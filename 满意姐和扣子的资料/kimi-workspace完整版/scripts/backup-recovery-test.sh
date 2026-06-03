#!/bin/bash
# backup-recovery-test.sh - 备份恢复测试
# 每月1日02:00执行

BACKUP_DIR="/backup/daily"
TEST_DIR="/tmp/backup-recovery-test"
LOG_FILE="/var/log/openclaw/backup-recovery-test.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

mkdir -p "$TEST_DIR"
mkdir -p "$(dirname $LOG_FILE)"

echo "[$DATE] 开始备份恢复测试..." >> "$LOG_FILE"

# 查找最新的备份
LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/workspace-*.tar.gz 2>/dev/null | head -1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "[$DATE] ❌ 未找到备份文件!" >> "$LOG_FILE"
    exit 1
fi

echo "[$DATE] 测试恢复: $(basename $LATEST_BACKUP)" >> "$LOG_FILE"

# 清理测试目录
rm -rf "$TEST_DIR"/*

# 执行恢复测试
tar -xzf "$LATEST_BACKUP" -C "$TEST_DIR" 2>> "$LOG_FILE"

if [ $? -eq 0 ]; then
    # 验证恢复内容
    RECOVERED_SIZE=$(du -sb "$TEST_DIR"/workspace 2>/dev/null | cut -f1)
    echo "[$DATE] ✅ 恢复成功! 大小: $RECOVERED_SIZE bytes" >> "$LOG_FILE"
    
    # 验证关键文件存在
    if [ -f "$TEST_DIR"/workspace/SOUL.md ] && [ -f "$TEST_DIR"/workspace/AGENTS.md ]; then
        echo "[$DATE] ✅ 关键文件验证通过" >> "$LOG_FILE"
        TEST_RESULT="PASS"
    else
        echo "[$DATE] ❌ 关键文件缺失!" >> "$LOG_FILE"
        TEST_RESULT="FAIL"
    fi
else
    echo "[$DATE] ❌ 恢复失败!" >> "$LOG_FILE"
    TEST_RESULT="FAIL"
fi

# 保存测试结果
echo "{\"date\":\"$DATE\",\"backup\":\"$(basename $LATEST_BACKUP)\",\"result\":\"$TEST_RESULT\",\"size\":$RECOVERED_SIZE}" > /root/.openclaw/workspace/memory/last-backup-recovery-test.json

# 清理测试目录
rm -rf "$TEST_DIR"

[ "$TEST_RESULT" = "PASS" ] && exit 0 || exit 1
