#!/bin/bash
# quality-assurance Cron配置
# 质量保证协议自动化监控 (7标准 + 5标准)

# 质量统计更新 - 每6小时更新
0 */6 * * * cd /root/.openclaw/workspace && bash skills/quality-assurance/scripts/confidence-stats.sh >> /tmp/quality-stats.log 2>&1

# 质量报告 - 每周日晚20:00生成
0 20 * * 0 cd /root/.openclaw/workspace && bash skills/quality-assurance/scripts/quality-report.sh weekly >> /tmp/quality-weekly.log 2>&1

# 每日对抗测试(快速模式) - 凌晨3点
0 3 * * * cd /root/.openclaw/workspace && bash skills/quality-assurance/scripts/qa-adversarial-test.sh --quick >> /tmp/qa-adversarial.log 2>&1

# 每周完整对抗测试 - 周日凌晨2点
0 2 * * 0 cd /root/.openclaw/workspace && bash skills/quality-assurance/scripts/qa-adversarial-test.sh >> /tmp/qa-adversarial-full.log 2>&1

# 每周Skill质量扫描 - 周一上午9点
0 9 * * 1 cd /root/.openclaw/workspace && bash skills/quality-assurance/scripts/qa-review.sh --batch skills/ >> /tmp/qa-batch.log 2>&1
