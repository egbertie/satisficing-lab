#!/bin/bash
# 5标准Skill Cron集成配置
# 生成时间: 2026-03-20
# 说明: 为今日转化的12个Skill补充Cron定时任务

# 零空置强制执行 (30分钟检查)
echo "*/30 * * * * cd /root/.openclaw/workspace && python3 skills/zero-idle-enforcer/scripts/enforcer.py >> /tmp/zero-idle.log 2>&1"

# 决策安全红线检查 (每次输出前)
# 注: 此检查需要在对话流程中集成，非纯Cron

# 文件完整性检查 (每日09:07)
echo "7 9 * * * cd /root/.openclaw/workspace && python3 skills/file-integrity-checker/scripts/integrity-checker.py >> /tmp/integrity-check.log 2>&1"

# 知识沉淀自动化 (每日23:47)
echo "47 23 * * * cd /root/.openclaw/workspace && python3 skills/knowledge-extraction/scripts/extractor.py >> /tmp/knowledge-extraction.log 2>&1"

# 信息闭环三原则检查 (每小时)
echo "0 * * * * cd /root/.openclaw/workspace && python3 skills/closed-loop-enforcer/scripts/loop-tracker.py >> /tmp/closed-loop.log 2>&1"

# 7×24自主推进体系 - 晨报 (每日08:30)
echo "30 8 * * * cd /root/.openclaw/workspace && python3 skills/7x24-autonomous-system/scripts/autonomous-runner.py morning >> /tmp/7x24.log 2>&1"

# 7×24自主推进体系 - 小时协调 (每2小时)
echo "0 */2 * * * cd /root/.openclaw/workspace && python3 skills/7x24-autonomous-system/scripts/autonomous-runner.py hourly >> /tmp/7x24.log 2>&1"

# 7×24自主推进体系 - 夜间学习 (每日23:00)
echo "0 23 * * * cd /root/.openclaw/workspace && python3 skills/7x24-autonomous-system/scripts/autonomous-runner.py night >> /tmp/7x24.log 2>&1"

# 7×24自主推进体系 - 周复盘 (每周六18:00)
echo "0 18 * * 6 cd /root/.openclaw/workspace && python3 skills/7x24-autonomous-system/scripts/autonomous-runner.py weekly >> /tmp/7x24.log 2>&1"

# 第一性原则审计 (每周六)
echo "0 20 * * 6 cd /root/.openclaw/workspace && python3 skills/first-principle-enforcer/scripts/principle-auditor.py >> /tmp/first-principle-audit.log 2>&1"

# 决策安全红线检查 (每日14:00)
echo "0 14 * * * cd /root/.openclaw/workspace && python3 skills/decision-safety-redlines/scripts/redline-checker.py 'test' >> /tmp/redline-check.log 2>&1"