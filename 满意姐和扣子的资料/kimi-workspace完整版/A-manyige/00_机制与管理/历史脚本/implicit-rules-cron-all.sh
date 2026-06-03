#!/bin/bash
# 隐性规则12个批量转化 - 整合Cron配置
# 生成时间: 2026-03-20
# 包含4个Skill的定时任务配置

# ============================================
# Skill 1: execution-protocol (执行流程协议)
# 覆盖规则: 1-4 (安排确认/执行汇报/问题升级/先完成再完美/砍冗余/任务衔接)
# ============================================

# 任务链检查 - 每5分钟检查一次完成的任务
*/5 * * * * cd /root/.openclaw/workspace && bash skills/execution-protocol/scripts/task-chain-checker.sh >> /tmp/exec-protocol-chain.log 2>&1

# 协议监控 - 每15分钟检查执行状态
*/15 * * * * cd /root/.openclaw/workspace && bash skills/execution-protocol/scripts/protocol-check.sh >> /tmp/exec-protocol-monitor.log 2>&1

# 每日协议统计 - 每晚22:00
0 22 * * * cd /root/.openclaw/workspace && bash skills/execution-protocol/scripts/daily-stats.sh >> /tmp/exec-protocol-stats.log 2>&1

# ============================================
# Skill 2: cost-control (成本控制协议)
# 覆盖规则: 5-7 (Opus需理由/≥¥20记录/日限额¥50)
# ============================================

# 成本监控 - 每30分钟检查日限额
*/30 * * * * cd /root/.openclaw/workspace && bash skills/cost-control/scripts/daily-cost-check.sh >> /tmp/cost-monitor.log 2>&1

# 每日成本报告 - 每晚23:00
0 23 * * * cd /root/.openclaw/workspace && bash skills/cost-control/scripts/cost-stats.sh daily >> /tmp/cost-daily-report.log 2>&1

# 每周成本分析 - 每周日晚21:00
0 21 * * 0 cd /root/.openclaw/workspace && bash skills/cost-control/scripts/cost-stats.sh weekly >> /tmp/cost-weekly-report.log 2>&1

# ============================================
# Skill 3: quality-assurance (质量保证协议)
# 覆盖规则: 8-9 (置信度标注/交叉验证)
# ============================================

# 质量统计更新 - 每6小时更新
0 */6 * * * cd /root/.openclaw/workspace && bash skills/quality-assurance/scripts/confidence-stats.sh >> /tmp/quality-stats.log 2>&1

# 质量报告 - 每周日晚20:00生成
0 20 * * 0 cd /root/.openclaw/workspace && bash skills/quality-assurance/scripts/quality-report.sh weekly >> /tmp/quality-weekly.log 2>&1

# ============================================
# Skill 4: reporting-standards (汇报标准协议)
# 覆盖规则: 10-12 (5要素汇报/每日汇报/周六执行率)
# ============================================

# 每日汇报生成 - 每晚20:00 (错峰，与execution-protocol同时)
0 20 * * * cd /root/.openclaw/workspace && bash skills/reporting-standards/scripts/generate-report.sh daily >> /tmp/daily-report.log 2>&1

# 周执行率报告 - 每周六晚22:00
0 22 * * 6 cd /root/.openclaw/workspace && bash skills/reporting-standards/scripts/generate-report.sh weekly >> /tmp/weekly-compliance.log 2>&1

# ============================================
# 汇总: 共12个Cron任务
# ============================================
# execution-protocol: 3个任务 (每5分/每15分/每日22:00)
# cost-control: 3个任务 (每30分/每日23:00/每周日21:00)
# quality-assurance: 2个任务 (每6小时/每周日20:00)
# reporting-standards: 2个任务 (每日20:00/每周六22:00)
# ============================================
