#!/bin/bash
PERSIST_DIR="/root/.openclaw/workspace/skills/blue-auditor/tightening_spell_data"
[ -f /tmp/blue_army_delay_points ] && cp /tmp/blue_army_delay_points "$PERSIST_DIR/blue_army/"
[ -f /tmp/satisfied_girl_credit ] && cp /tmp/satisfied_girl_credit "$PERSIST_DIR/satisfied_girl/"
[ -f /tmp/satisfied_girl_daily_quota ] && cp /tmp/satisfied_girl_daily_quota "$PERSIST_DIR/satisfied_girl/"
date +%Y%m%d > "$PERSIST_DIR/last_update_date"
