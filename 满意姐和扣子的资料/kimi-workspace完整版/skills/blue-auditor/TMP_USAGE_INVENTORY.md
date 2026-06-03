# /tmp使用情况清单
生成时间: Sun Mar 29 09:14:49 PM CST 2026

## /root/.openclaw/cron/backup-verify.sh
```
4:python3 skills/baseline-checker/scripts/baseline-checker-runner.py check --category backup 2>/dev/null || echo "Baseline check run at $(date)" >> /tmp/cron-backup.log
```

## /root/.openclaw/cron/calendar-prep.sh
```
5:echo "$(date '+%Y-%m-%d %H:%M:%S') Calendar prep check starting" >> /tmp/cron-calendar.log
10:echo "$(date '+%Y-%m-%d %H:%M:%S') Calendar prep check completed" >> /tmp/cron-calendar.log
```

## /root/.openclaw/cron/morning-report.sh
```
5:echo "$(date '+%Y-%m-%d %H:%M:%S') Morning report generation starting" >> /tmp/cron-morning.log
20:echo "$(date '+%Y-%m-%d %H:%M:%S') Morning report completed" >> /tmp/cron-morning.log
```

## /root/.openclaw/cron/token-alert.sh
```
4:echo "$(date '+%Y-%m-%d %H:%M:%S') Token check: threshold ${THRESHOLD}%" >> /tmp/cron-token.log
```

## /root/.openclaw/cron/overdue-alert.sh
```
3:echo "$(date '+%Y-%m-%d %H:%M:%S') Overdue check for P0/P1 tasks" >> /tmp/cron-overdue.log
```

## /root/.openclaw/extensions/dingtalk-connector/node_modules/playwright-core/bin/reinstall_msedge_dev_linux.sh
```
42:curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /tmp/microsoft.gpg
43:install -o root -g root -m 644 /tmp/microsoft.gpg /etc/apt/trusted.gpg.d/
45:rm /tmp/microsoft.gpg
```

## /root/.openclaw/extensions/dingtalk-connector/node_modules/playwright-core/bin/reinstall_msedge_stable_linux.sh
```
42:curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /tmp/microsoft.gpg
43:install -o root -g root -m 644 /tmp/microsoft.gpg /etc/apt/trusted.gpg.d/
45:rm /tmp/microsoft.gpg
```

## /root/.openclaw/extensions/dingtalk-connector/node_modules/playwright-core/bin/reinstall_msedge_beta_mac.sh
```
9:sudo installer -pkg /tmp/msedge_beta.pkg -target /
10:rm -rf /tmp/msedge_beta.pkg
```

## /root/.openclaw/extensions/dingtalk-connector/node_modules/playwright-core/bin/reinstall_msedge_stable_mac.sh
```
9:sudo installer -pkg /tmp/msedge_stable.pkg -target /
10:rm -rf /tmp/msedge_stable.pkg
```

## /root/.openclaw/extensions/dingtalk-connector/node_modules/playwright-core/bin/reinstall_chrome_beta_mac.sh
```
11:rm -rf /tmp/googlechromebeta.dmg
```

## /root/.openclaw/extensions/dingtalk-connector/node_modules/playwright-core/bin/reinstall_chrome_stable_mac.sh
```
11:rm -rf /tmp/googlechrome.dmg
```

## /root/.openclaw/extensions/dingtalk-connector/node_modules/playwright-core/bin/reinstall_msedge_beta_linux.sh
```
42:curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /tmp/microsoft.gpg
43:install -o root -g root -m 644 /tmp/microsoft.gpg /etc/apt/trusted.gpg.d/
45:rm /tmp/microsoft.gpg
```

## /root/.openclaw/extensions/dingtalk-connector/node_modules/playwright-core/bin/reinstall_msedge_dev_mac.sh
```
9:sudo installer -pkg /tmp/msedge_dev.pkg -target /
10:rm -rf /tmp/msedge_dev.pkg
```

## /root/.openclaw/extensions/dingtalk-connector/node_modules/openclaw/skills/video-frames/scripts/frame.sh
```
10:  frame.sh video.mp4 --out /tmp/frame.jpg
11:  frame.sh video.mp4 --time 00:00:10 --out /tmp/frame-10s.jpg
12:  frame.sh video.mp4 --index 0 --out /tmp/frame0.png
```

## /root/.openclaw/workspace/run_llama2_benchmark.sh
```
85:cat > /tmp/benchmark_transformers.py << 'EOF'
144:python3 /tmp/benchmark_transformers.py ~/models/$MODEL_NAME_SHORT 2>&1 | tee -a $RESULT_FILE
```

## /root/.openclaw/workspace/disaster-recovery/02-自动化备份脚本/backup-master.sh
```
17:LOCK_FILE="/tmp/dr-backup.lock"
```

## /root/.openclaw/workspace/disaster-recovery/02-自动化备份脚本/backup-github.sh
```
38:    local repos_file="/tmp/github_repos_$$.json"
```

## /root/.openclaw/workspace/disaster-recovery/auto-git-commit.sh
```
10:LOG_FILE="/tmp/auto-git-commit.log"
11:LOCK_FILE="/tmp/auto-git-commit.lock"
```

## /root/.openclaw/workspace/.workspace_optimization/backup_critical/skills/presentation-helper/presentation-helper.sh
```
84:  local tmp="/tmp/pres_meta_tmp.json"
```

## /root/.openclaw/workspace/.workspace_optimization/backup_critical/skills/video-frames/frame.sh
```
10:  frame.sh video.mp4 --out /tmp/frame.jpg
11:  frame.sh video.mp4 --time 00:00:10 --out /tmp/frame-10s.jpg
12:  frame.sh video.mp4 --index 0 --out /tmp/frame0.png
```

## /root/.openclaw/workspace/skills/quality-assurance/scripts/qa-adversarial-test.sh
```
19:TEST_DIR="/tmp/qa-adversarial-test-$$"
```

## /root/.openclaw/workspace/skills/quality-assurance/cron-config.sh
```
6:0 */6 * * * cd /root/.openclaw/workspace && bash skills/quality-assurance/scripts/confidence-stats.sh >> /tmp/quality-stats.log 2>&1
9:0 20 * * 0 cd /root/.openclaw/workspace && bash skills/quality-assurance/scripts/quality-report.sh weekly >> /tmp/quality-weekly.log 2>&1
12:0 3 * * * cd /root/.openclaw/workspace && bash skills/quality-assurance/scripts/qa-adversarial-test.sh --quick >> /tmp/qa-adversarial.log 2>&1
15:0 2 * * 0 cd /root/.openclaw/workspace && bash skills/quality-assurance/scripts/qa-adversarial-test.sh >> /tmp/qa-adversarial-full.log 2>&1
18:0 9 * * 1 cd /root/.openclaw/workspace && bash skills/quality-assurance/scripts/qa-review.sh --batch skills/ >> /tmp/qa-batch.log 2>&1
```

## /root/.openclaw/workspace/skills/backup-verification/verify-backup-v2.sh
```
20:REPORT_FILE="/tmp/backup_verification_latest.json"
21:LOG_FILE="/tmp/backup_verification.log"
140:    python3 "$PYTHON_SCRIPT" --json > /tmp/verify_temp.json
143:    issues_count=$(jq '.layers | to_entries | map(.value.failed) | add' /tmp/verify_temp.json 2>/dev/null || echo "0")
159:    rm -f /tmp/verify_temp.json
```

## /root/.openclaw/workspace/skills/z_archive_unified/.archive_execution-protocol/cron-config.sh
```
6:*/5 * * * * cd /root/.openclaw/workspace && bash skills/execution-protocol/scripts/task-chain-checker.sh >> /tmp/exec-protocol-chain.log 2>&1
9:*/15 * * * * cd /root/.openclaw/workspace && bash skills/execution-protocol/scripts/protocol-check.sh >> /tmp/exec-protocol-monitor.log 2>&1
12:0 22 * * * cd /root/.openclaw/workspace && bash skills/execution-protocol/scripts/daily-stats.sh >> /tmp/exec-protocol-stats.log 2>&1
```

## /root/.openclaw/workspace/skills/z_archive_unified/.archive_kimi-cli-task-manager/scripts/execute_task.sh
```
81:    elif grep -q "429" /tmp/kimi_output_$$.txt 2>/dev/null; then
```

## /root/.openclaw/workspace/skills/z_archive_unified/.archive_presentation-helper/presentation-helper.sh
```
84:  local tmp="/tmp/pres_meta_tmp.json"
```

## /root/.openclaw/workspace/skills/z_archive_unified/.archive_knowledge-upkeep/cron-config.sh
```
7:echo "0 3 * * * cd /root/.openclaw/workspace && python3 skills/knowledge-upkeep/scripts/upkeeper.py expert >> /tmp/knowledge-upkeep.log 2>&1"
10:echo "7 9 * * * cd /root/.openclaw/workspace && python3 skills/knowledge-upkeep/scripts/upkeeper.py knowledge >> /tmp/knowledge-upkeep.log 2>&1"
13:echo "0 10 * * 1 cd /root/.openclaw/workspace && python3 skills/knowledge-upkeep/scripts/upkeeper.py maintenance >> /tmp/knowledge-upkeep.log 2>&1"
16:echo "0 4 1 * * cd /root/.openclaw/workspace && python3 skills/knowledge-upkeep/scripts/upkeeper.py knowledge >> /tmp/knowledge-upkeep.log 2>&1"
19:echo "0 22 * * 0 cd /root/.openclaw/workspace && python3 skills/knowledge-upkeep/scripts/upkeeper.py knowledge >> /tmp/knowledge-upkeep.log 2>&1"
```

## /root/.openclaw/workspace/skills/z_archive_unified/.archive_cost-control/cron-config.sh
```
6:*/30 * * * * cd /root/.openclaw/workspace && bash skills/cost-control/scripts/daily-cost-check.sh >> /tmp/cost-monitor.log 2>&1
9:0 23 * * * cd /root/.openclaw/workspace && bash skills/cost-control/scripts/cost-stats.sh daily >> /tmp/cost-daily-report.log 2>&1
12:0 21 * * 0 cd /root/.openclaw/workspace && bash skills/cost-control/scripts/cost-stats.sh weekly >> /tmp/cost-weekly-report.log 2>&1
```

## /root/.openclaw/workspace/skills/z_archive_unified/.archive_decision-guardian/cron-config.sh
```
7:echo "0 * * * * cd /root/.openclaw/workspace && python3 skills/decision-guardian/scripts/guardian.py redteam >> /tmp/decision-guardian.log 2>&1"
10:echo "0 9,15 * * * cd /root/.openclaw/workspace && python3 skills/decision-guardian/scripts/guardian.py prereview >> /tmp/decision-guardian.log 2>&1"
13:echo "0 */2 * * * cd /root/.openclaw/workspace && python3 skills/decision-guardian/scripts/guardian.py escalation >> /tmp/decision-guardian.log 2>&1"
16:echo "0 1 * * * cd /root/.openclaw/workspace && python3 skills/decision-guardian/scripts/guardian.py all >> /tmp/decision-guardian.log 2>&1"
19:echo "0 10 1 * * cd /root/.openclaw/workspace && python3 skills/decision-guardian/scripts/guardian.py redteam >> /tmp/decision-guardian.log 2>&1"
```

## /root/.openclaw/workspace/skills/z_archive_unified/.archive_video-frames/frame.sh
```
10:  frame.sh video.mp4 --out /tmp/frame.jpg
11:  frame.sh video.mp4 --time 00:00:10 --out /tmp/frame-10s.jpg
12:  frame.sh video.mp4 --index 0 --out /tmp/frame0.png
```

## /root/.openclaw/workspace/skills/z_archive_unified/.archive_management-enforcer/cron-config.sh
```
7:echo "30 22 * * * cd /root/.openclaw/workspace && python3 skills/management-enforcer/scripts/enforcer.py report >> /tmp/management-enforcer.log 2>&1"
10:echo "0 */4 * * * cd /root/.openclaw/workspace && python3 skills/management-enforcer/scripts/enforcer.py comm >> /tmp/management-enforcer.log 2>&1"
13:echo "30 9,14 * * * cd /root/.openclaw/workspace && python3 skills/management-enforcer/scripts/enforcer.py violation >> /tmp/management-enforcer.log 2>&1"
16:echo "0 2 * * * cd /root/.openclaw/workspace && python3 skills/management-enforcer/scripts/enforcer.py all >> /tmp/management-enforcer.log 2>&1"
```

## /root/.openclaw/workspace/skills/z_archive_unified/.archive_reporting-standards/cron-config.sh
```
6:0 20 * * * cd /root/.openclaw/workspace && bash skills/reporting-standards/scripts/generate-report.sh daily >> /tmp/daily-report.log 2>&1
9:0 22 * * 6 cd /root/.openclaw/workspace && bash skills/reporting-standards/scripts/generate-report.sh weekly >> /tmp/weekly-compliance.log 2>&1
```

## /root/.openclaw/workspace/skills/5standard-integration/cron-config.sh
```
7:echo "*/30 * * * * cd /root/.openclaw/workspace && python3 skills/zero-idle-enforcer/scripts/enforcer.py >> /tmp/zero-idle.log 2>&1"
13:echo "7 9 * * * cd /root/.openclaw/workspace && python3 skills/file-integrity-checker/scripts/integrity-checker.py >> /tmp/integrity-check.log 2>&1"
16:echo "47 23 * * * cd /root/.openclaw/workspace && python3 skills/knowledge-extraction/scripts/extractor.py >> /tmp/knowledge-extraction.log 2>&1"
19:echo "0 * * * * cd /root/.openclaw/workspace && python3 skills/closed-loop-enforcer/scripts/loop-tracker.py >> /tmp/closed-loop.log 2>&1"
22:echo "30 8 * * * cd /root/.openclaw/workspace && python3 skills/7x24-autonomous-system/scripts/autonomous-runner.py morning >> /tmp/7x24.log 2>&1"
```

## /root/.openclaw/workspace/scripts/forgotten_tasks_scan.sh
```
2:echo "[$(date '+%Y-%m-%d %H:%M:%S')] 被遗忘任务扫描" >> /tmp/forgotten_tasks.log
```

## /root/.openclaw/workspace/scripts/expert_profile_check.sh
```
2:echo "[$(date '+%Y-%m-%d %H:%M:%S')] 专家档案状态检查" >> /tmp/expert_profile.log
```

## /root/.openclaw/workspace/scripts/project_status_check.sh
```
2:echo "[$(date '+%Y-%m-%d %H:%M:%S')] 项目状态检查" >> /tmp/project_status.log
```

## /root/.openclaw/workspace/scripts/feishu_permission_test_20260327.sh
```
4:echo "===== 飞书权限测试 $(date) =====" > /tmp/feishu_permission_test_20260327.log
7:echo "[TEST 1] 日历列表..." >> /tmp/feishu_permission_test_20260327.log
15:" 2>&1 >> /tmp/feishu_permission_test_20260327.log
18:echo "" >> /tmp/feishu_permission_test_20260327.log
19:echo "[TEST 2] 日历事件列表API..." >> /tmp/feishu_permission_test_20260327.log
```

## /root/.openclaw/workspace/scripts/token_weekly_monitor.sh
```
3:echo "[$(date '+%Y-%m-%d %H:%M:%S')] Token周度监控" >> /tmp/token_weekly.log
4:echo "📊 Token监控完成" >> /tmp/token_weekly.log
```

## /root/.openclaw/workspace/scripts/disaster-recovery-sync-v3.sh
```
711:    local temp_workspace="/tmp/test_dr_nonexistent_$$"
733:    local test_dir="/tmp/test_dr_perm_$$"
749:    local lock_file="/tmp/test_dr_lock_$$"
765:    local bad_config="/tmp/test_dr_bad_config_$$"
781:    local temp_backup_dir="/tmp/test_dr_interrupt_$$"
```

## /root/.openclaw/workspace/scripts/merged-daily-tasks.sh
```
5:LOG_FILE="/tmp/merged-tasks.log"
```

## /root/.openclaw/workspace/scripts/auto-git-commit.sh
```
6:LOCK_FILE="/tmp/auto-git-commit.lock"
7:LOG_FILE="/tmp/auto-git-commit.log"
```

## /root/.openclaw/workspace/scripts/evening_totem_return.sh
```
3:echo "[$(date '+%Y-%m-%d %H:%M:%S')] 黄昏图腾归位开始" >> /tmp/evening_totem.log
4:echo "🌅 图腾归位，知识固化" >> /tmp/evening_totem.log
5:echo "[$(date '+%Y-%m-%d %H:%M:%S')] 黄昏图腾归位完成" >> /tmp/evening_totem.log
```

## /root/.openclaw/workspace/scripts/auto-checkpoint.sh
```
8:LOG_FILE="/tmp/checkpoint.log"
```

## /root/.openclaw/workspace/scripts/feishu_bitable_sync.sh
```
2:echo "[$(date '+%Y-%m-%d %H:%M:%S')] 飞书多维表格同步" >> /tmp/feishu_sync.log
```

## /root/.openclaw/workspace/scripts/heartbeat_coordination.sh
```
2:echo "[$(date '+%Y-%m-%d %H:%M:%S')] 心跳协调执行" >> /tmp/heartbeat_coordination.log
```

## /root/.openclaw/workspace/scripts/knowledge_os_maint.sh
```
3:echo "[$(date '+%Y-%m-%d %H:%M:%S')] 知识OS维护" >> /tmp/knowledge_os.log
4:echo "🧠 知识OS维护完成" >> /tmp/knowledge_os.log
```

## /root/.openclaw/workspace/scripts/memory-guardian-cron-setup.sh
```
45:crontab -l > /tmp/crontab.backup 2>/dev/null || echo "# 备份创建时间: $(date)" > /tmp/crontab.backup
```

## /root/.openclaw/workspace/scripts/expert_update.sh
```
3:echo "[$(date '+%Y-%m-%d %H:%M:%S')] 专家资料更新" >> /tmp/expert_update.log
4:echo "👥 专家资料更新完成" >> /tmp/expert_update.log
```

## /root/.openclaw/workspace/scripts/implicit-rules-cron-all.sh
```
12:*/5 * * * * cd /root/.openclaw/workspace && bash skills/execution-protocol/scripts/task-chain-checker.sh >> /tmp/exec-protocol-chain.log 2>&1
15:*/15 * * * * cd /root/.openclaw/workspace && bash skills/execution-protocol/scripts/protocol-check.sh >> /tmp/exec-protocol-monitor.log 2>&1
18:0 22 * * * cd /root/.openclaw/workspace && bash skills/execution-protocol/scripts/daily-stats.sh >> /tmp/exec-protocol-stats.log 2>&1
26:*/30 * * * * cd /root/.openclaw/workspace && bash skills/cost-control/scripts/daily-cost-check.sh >> /tmp/cost-monitor.log 2>&1
29:0 23 * * * cd /root/.openclaw/workspace && bash skills/cost-control/scripts/cost-stats.sh daily >> /tmp/cost-daily-report.log 2>&1
```

## /root/.openclaw/workspace/scripts/implicit-rules-cron-manager-v2.sh
```
28:readonly LOCK_FILE="/tmp/${SCRIPT_NAME}.lock"
818:    local test_lock="/tmp/test_cron_manager_lock_$$"
831:    local bad_config="/tmp/test_bad_cron_config_$$"
848:    local bad_backup="/tmp/test_bad_backup_$$.json"
```

## /root/.openclaw/workspace/scripts/calendar_check.sh
```
3:echo "[$(date '+%Y-%m-%d %H:%M:%S')] 日程检查" >> /tmp/calendar_check.log
4:echo "📅 日程检查完成" >> /tmp/calendar_check.log
```

## /root/.openclaw/workspace/scripts/deploy-cron-p0.sh
```
20:echo "$(date): Token check placeholder" >> /tmp/cron-token.log
31:echo "$(date): Morning report generation" >> /tmp/cron-morning.log
64:echo "$(date): Calendar prep check" >> /tmp/cron-calendar.log
```

## /root/.openclaw/workspace/scripts/token-fuse.sh
```
4:LOG_FILE="/tmp/token-fuse.log"
19:    echo "hibernation" > /tmp/token-mode.txt
22:    echo "reduced" > /tmp/token-mode.txt
25:    echo "caution" > /tmp/token-mode.txt
28:    echo "normal" > /tmp/token-mode.txt
```

## /root/.openclaw/workspace/scripts/verify-backup-v2.sh
```
755:    local test_file="/tmp/test_verify_perm_$$"
773:    local bad_json="/tmp/test_bad_json_$$"
```

## /root/.openclaw/workspace/scripts/memory_maintenance.sh
```
2:echo "[$(date '+%Y-%m-%d %H:%M:%S')] MEMORY.md维护" >> /tmp/memory_maintenance.log
```

## /root/.openclaw/workspace/scripts/sentinel-guard.sh
```
64:        mv /root/.openclaw/workspace/shadow-clone "/tmp/trash-shadow-clone-$(date +%Y%m%d-%H%M%S)" 2>/dev/null
```

## /root/.openclaw/workspace/scripts/info_firewall_check.sh
```
3:echo "[$(date '+%Y-%m-%d %H:%M:%S')] 信息防火墙检查" >> /tmp/info_firewall.log
4:echo "✅ 信息防火墙正常" >> /tmp/info_firewall.log
```

## /root/.openclaw/workspace/scripts/morning_report.sh
```
5:echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始生成晨报..." >> /tmp/morning_report.log
8:/usr/bin/python3 /root/.openclaw/workspace/skills/todo-management/morning_report.py >> /tmp/morning_report.log 2>&1
11:echo "[$(date '+%Y-%m-%d %H:%M:%S')] 晨报生成完成" >> /tmp/morning_report.log
```

## /root/.openclaw/workspace/scripts/token_mode_controller.sh
```
10:STATE_FILE="/tmp/token_mode_state.json"
11:LOG_FILE="/tmp/token_mode_controller.log"
```

## /root/.openclaw/workspace/scripts/morning_totem_ritual.sh
```
3:echo "[$(date '+%Y-%m-%d %H:%M:%S')] 晨间图腾仪式开始" >> /tmp/morning_totem.log
4:echo "🔥 点燃图腾之火" >> /tmp/morning_totem.log
5:echo "[$(date '+%Y-%m-%d %H:%M:%S')] 晨间图腾仪式完成" >> /tmp/morning_totem.log
```

## /root/.openclaw/workspace/scripts/self_assessment_calib.sh
```
3:echo "[$(date '+%Y-%m-%d %H:%M:%S')] 自我评估校准" >> /tmp/self_assessment.log
4:echo "✅ 评估校准完成" >> /tmp/self_assessment.log
```

## /root/.openclaw/workspace/scripts/mentions_notify.sh
```
3:echo "[$(date '+%Y-%m-%d %H:%M:%S')] 提及通知检查" >> /tmp/mentions.log
4:echo "🔔 提及通知检查完成" >> /tmp/mentions.log
```

## /root/.openclaw/workspace/scripts/suicide-rebirth-test.sh
```
7:TEST_DIR="/tmp/rebirth-test-$(date +%s)"
```

## /root/.openclaw/workspace/scripts/checkpoint_health.sh
```
3:echo "[$(date '+%Y-%m-%d %H:%M:%S')] 检查点健康验证" >> /tmp/checkpoint_health.log
4:echo "✅ 检查点健康" >> /tmp/checkpoint_health.log
```

## /root/.openclaw/workspace/scripts/memory_cleanup.sh
```
3:echo "[$(date '+%Y-%m-%d %H:%M:%S')] 内存清理" >> /tmp/memory_cleanup.log
4:echo "🧹 内存清理完成" >> /tmp/memory_cleanup.log
```

## /root/.openclaw/workspace/archive/notion_sync_old/notion_batch_sync.sh
```
24:find "$WORKSPACE" -type f \( -name "*.md" -o -name "*.html" -o -name "*.py" -o -name "*.json" -o -name "*.txt" -o -name "*.js" -o -name "*.css" -o -name "*.yml" -o -name "*.yaml" \) ! -path "*/.git/*" ! -path "*/node_modules/*" > /tmp/all_files.txt
25:TOTAL=$(cat /tmp/all_files.txt | wc -l)
110:done < /tmp/all_files.txt
```

## /root/.openclaw/scripts/task-progress-monitor.sh
```
5:LOG_FILE="/tmp/full-tasks-progress.log"
```

## /root/.openclaw/scripts/satisfied_girl_greed_detector.sh
```
4:WORK_LOG="/tmp/satisfied_girl_work_timeline"
5:ALERT_LOG="/tmp/satisfied_girl_greed_alerts"
25:        date -d '+30 minutes' +%s > /tmp/satisfied_girl_forced_break
```

## /root/.openclaw/scripts/workflow_lock_check.sh
```
5:LOCK_FILE="/tmp/workflow_lock.json"
```

## /root/.openclaw/scripts/satisfied_girl_progress_hold.sh
```
24:HOLD_FILE="/tmp/satisfied_girl_progress_hold_$(date +%s)"
```

## /root/.openclaw/scripts/audit_pass.sh
```
4:LOCK_FILE="/tmp/workflow_lock.json"
```

## /root/.openclaw/scripts/blue_army_delay_tracker.sh
```
4:DELAY_LOG="/tmp/blue_army_delay_log.json"
5:DELAY_POINTS_FILE="/tmp/blue_army_delay_points"
39:        echo "DOUBLE_AUDIT_NEXT=true" > /tmp/blue_army_punishment_flag
```

## /root/.openclaw/scripts/satisfied_girl_false_report_public.sh
```
30:    CREDIT_FILE="/tmp/satisfied_girl_credit"
```

## /root/.openclaw/scripts/submit_for_audit.sh
```
5:LOCK_FILE="/tmp/workflow_lock.json"
```

## /root/.openclaw/scripts/satisfied_girl_cooldown.sh
```
4:COOLDOWN_FILE="/tmp/satisfied_girl_cooldown_end"
5:CREDIT_FILE="/tmp/satisfied_girl_credit"
6:VIOLATION_FILE="/tmp/satisfied_girl_violation_count"
```

## /root/.openclaw/scripts/daily-maintenance.sh
```
15:    rm -rf /tmp/tmp.* 2>/dev/null
```

## /root/.openclaw/scripts/satisfied_girl_quota.sh
```
4:QUOTA_FILE="/tmp/satisfied_girl_daily_quota"
5:CREDIT_FILE="/tmp/satisfied_girl_credit"
6:CLAIM_LOG="/tmp/satisfied_girl_claim_log"
```

## /root/.openclaw/scripts/batch_audit_interceptor.sh
```
4:LAST_AUDIT_FILE="/tmp/blue_army_last_audit_time"
5:INTERCEPT_LOG="/tmp/blue_army_intercept_log"
```

