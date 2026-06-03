# 合伙人决策成熟度测评系统 - 部署检查清单

> 部署前逐项确认，确保系统可用

## 前置条件检查

- [ ] 飞书多维表格已创建并配置问卷表单
- [ ] 多维表格Token已记录（当前: `EvF8bhloAaUZVGsUOVHcc2ZJn55`）
- [ ] 数据表ID已确认（当前: `tbltu58p5Xp8oqSN`）
- [ ] Python3 环境可用（`python3 --version`）
- [ ] 工作目录可写权限（`/root/.openclaw/workspace/`）

## 文件完整性检查

- [ ] `scripts/maturity_scoring_algorithm.py` 存在且可执行
- [ ] `scripts/partner_assessment_v1.py` 存在且可执行
- [ ] `scripts/pdf_report_generator.py` 存在且可执行
- [ ] `scripts/test_end_to_end.py` 存在（用于验证）
- [ ] `config/assessment_cron.txt` 存在
- [ ] `README_PARTNER_ASSESSMENT.md` 存在

## 目录结构检查

- [ ] `reports/assessments/` 目录存在
- [ ] `reports/assessments/pdf/` 子目录存在
- [ ] `/tmp/` 可写（用于状态文件）

## 依赖检查

```bash
# 运行依赖测试
python3 scripts/test_end_to_end.py
```

- [ ] 评分算法测试通过
- [ ] 报告生成测试通过
- [ ] 状态持久化测试通过
- [ ] 去重逻辑测试通过

## Cron配置步骤

### 方法1: 添加到系统crontab

```bash
sudo crontab -e
```

粘贴以下内容：

```
# 合伙人决策成熟度测评自动化
*/5 * * * * cd /root/.openclaw/workspace && /usr/bin/python3 scripts/partner_assessment_v1.py >> /tmp/assessment_cron.log 2>&1
0 * * * * cd /root/.openclaw/workspace && /usr/bin/python3 scripts/pdf_report_generator.py >> /tmp/pdf_gen_cron.log 2>&1
0 3 * * * find /tmp/assessment_cron.log -mtime +7 -delete
0 3 * * * find /tmp/pdf_gen_cron.log -mtime +7 -delete
```

### 方法2: 使用OpenClaw Cron技能

```bash
openclaw cron add "*/5 * * * * partner_assessment_check"
```

## 验证部署

### 手动测试

```bash
# 1. 单次运行测试
cd /root/.openclaw/workspace
python3 scripts/partner_assessment_v1.py

# 2. 检查输出
cat reports/assessments/*.md

# 3. 检查状态
cat /tmp/partner_assessment_state.json
```

### Cron测试

```bash
# 等待5分钟后检查
sleep 300 && cat /tmp/assessment_cron.log
```

## 故障排查

| 问题 | 排查步骤 |
|:-----|:---------|
| 没有生成报告 | 检查`reports/assessments/`权限；检查状态文件 |
| 评分异常 | 检查`maturity_scoring_algorithm.py`语法错误 |
| Cron不执行 | 检查crontab语法；检查日志文件权限 |
| PDF未生成 | md-to-pdf CLI未安装，使用占位符方案 |

## 上线后监控

- [ ] 首次运行后检查`assessment_cron.log`
- [ ] 确认报告文件正常生成
- [ ] 24小时后确认Cron正常运行
- [ ] 一周后检查报告累积情况

## 交付确认

- [ ] 系统可独立运行（无需人工干预）
- [ ] 报告质量通过创始人检验
- [ ] Cron任务已激活
- [ ] 文档已交付给用户

---

**部署完成日期**: _______________  
**部署人员**: _______________  
**用户验收**: _______________
