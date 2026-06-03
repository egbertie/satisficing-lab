#!/bin/bash
echo "=== 紧箍咒数据恢复 ==="
PERSIST_DIR="/root/.openclaw/workspace/skills/blue-auditor/tightening_spell_data"

[ -f "$PERSIST_DIR/blue_army/blue_army_delay_points" ] && cp "$PERSIST_DIR/blue_army/blue_army_delay_points" /tmp/ && echo "✅ 恢复延迟积分"
[ -f "$PERSIST_DIR/satisfied_girl/satisfied_girl_credit" ] && cp "$PERSIST_DIR/satisfied_girl/satisfied_girl_credit" /tmp/ && echo "✅ 恢复信用额度"
[ -f "$PERSIST_DIR/satisfied_girl/satisfied_girl_daily_quota" ] && cp "$PERSIST_DIR/satisfied_girl/satisfied_girl_daily_quota" /tmp/ && echo "✅ 恢复每日额度"

echo "✅ 紧箍咒数据恢复完成"
