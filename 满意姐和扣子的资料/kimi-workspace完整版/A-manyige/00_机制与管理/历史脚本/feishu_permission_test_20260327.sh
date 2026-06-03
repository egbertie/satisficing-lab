#!/bin/bash
# 飞书日历/任务权限测试脚本 - 2026-03-27 09:00执行

echo "===== 飞书权限测试 $(date) =====" > /tmp/feishu_permission_test_20260327.log

# 测试1: 日历API
echo "[TEST 1] 日历列表..." >> /tmp/feishu_permission_test_20260327.log
cd /root/.openclaw/workspace/plugins && python3 -c "
import sys
sys.path.insert(0, '.')
from feishu_drive_uploader import FeishuDriveUploader
uploader = FeishuDriveUploader()
token = uploader._get_token()
print(f'Token获取成功: {token[:20]}...')
" 2>&1 >> /tmp/feishu_permission_test_20260327.log

# 测试2: 尝试调用日历API
echo "" >> /tmp/feishu_permission_test_20260327.log
echo "[TEST 2] 日历事件列表API..." >> /tmp/feishu_permission_test_20260327.log
curl -s -X GET "https://open.feishu.cn/open-apis/calendar/v4/calendars" \
  -H "Authorization: Bearer $(cd /root/.openclaw/workspace/plugins && python3 -c 'from feishu_drive_uploader import FeishuDriveUploader; print(FeishuDriveUploader()._get_token())')" \
  -H "Content-Type: application/json" 2>&1 | head -100 >> /tmp/feishu_permission_test_20260327.log

echo "" >> /tmp/feishu_permission_test_20260327.log
echo "===== 测试完成 $(date) =====" >> /tmp/feishu_permission_test_20260327.log

cat /tmp/feishu_permission_test_20260327.log
