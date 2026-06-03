# Cron 配置说明 - 合伙人决策成熟度测评系统

## 快速配置（推荐）

### 步骤1: 编辑crontab

```bash
sudo crontab -e
```

### 步骤2: 添加以下行

```
# 合伙人决策成熟度测评自动化系统
# 每5分钟检查一次新记录
*/5 * * * * cd /root/.openclaw/workspace && /usr/bin/python3 scripts/partner_assessment_v1.py >> /tmp/assessment_cron.log 2>&1

# 每小时批量生成PDF报告
0 * * * * cd /root/.openclaw/workspace && /usr/bin/python3 scripts/pdf_report_generator.py >> /tmp/pdf_gen_cron.log 2>&1

# 每日清理旧日志（保留7天）
0 3 * * * find /tmp/assessment_cron.log -mtime +7 -delete
0 3 * * * find /tmp/pdf_gen_cron.log -mtime +7 -delete
```

### 步骤3: 保存并验证

```bash
# 查看当前crontab
sudo crontab -l

# 重启cron服务
sudo systemctl restart cron

# 验证cron运行状态
sudo systemctl status cron
```

## 任务说明

| 任务 | 频率 | 功能 |
|:-----|:-----|:-----|
| `partner_assessment_v1.py` | 每5分钟 | 轮询飞书多维表格，分析新记录，生成Markdown报告 |
| `pdf_report_generator.py` | 每小时 | 批量将Markdown转换为PDF |
| 日志清理 | 每天3:00 | 删除7天前的旧日志 |

## 日志位置

```
/tmp/assessment_cron.log      # 主程序执行日志
/tmp/pdf_gen_cron.log         # PDF生成日志
/tmp/partner_assessment_state.json  # 处理状态
```

## 手动触发测试

```bash
# 立即执行一次（测试用）
cd /root/.openclaw/workspace
python3 scripts/partner_assessment_v1.py

# 查看结果
ls -la reports/assessments/
cat reports/assessments/*.md
```

## 修改Cron配置

```bash
# 编辑
sudo crontab -e

# 常用修改选项：
# - 调整检查频率: */5 改为 */10（每10分钟）或 */1（每分钟）
# - 调整PDF生成频率: 0 * * * *（每小时）改为 0 */6 * * *（每6小时）
# - 禁用某项: 在行首加 # 注释
```

## 禁用/暂停自动化

```bash
# 临时禁用（注释掉所有行）
sudo crontab -e
# 在行首添加 # 注释

# 或完全清空cron
sudo crontab -r

# 恢复时重新添加
sudo crontab -e
# 粘贴配置内容
```

## 故障排查

### 问题: Cron不执行

```bash
# 1. 检查cron服务
sudo systemctl status cron

# 2. 检查日志
tail -f /var/log/syslog | grep CRON

# 3. 检查环境变量
sudo crontab -e
# 添加: SHELL=/bin/bash
# 添加: PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
```

### 问题: 脚本执行失败

```bash
# 查看详细错误日志
cat /tmp/assessment_cron.log

# 手动执行对比
cd /root/.openclaw/workspace && python3 scripts/partner_assessment_v1.py
```

## 高级配置

### 添加邮件通知（可选）

```
# 需要配置邮件服务
MAILTO=admin@example.com
*/5 * * * * cd /root/.openclaw/workspace && /usr/bin/python3 scripts/partner_assessment_v1.py
```

### 使用OpenClaw Cron技能（如果可用）

```bash
# 检查OpenClaw cron技能
openclaw cron list

# 添加任务
openclaw cron add "*/5 * * * * partner_assessment"

# 查看状态
openclaw cron status
```

---

**配置日期**: 2026-04-18  
**系统版本**: V1.0  
**维护者**: 满意解研究所
