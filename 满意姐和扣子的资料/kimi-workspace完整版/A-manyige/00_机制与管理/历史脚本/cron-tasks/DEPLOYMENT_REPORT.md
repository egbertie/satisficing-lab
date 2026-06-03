# 周期性任务机制部署报告

**部署时间**: 2026-03-31 08:19  
**部署状态**: ✅ 完成  
**部署人**: heartbeat-deployer (Subagent)

---

## 一、脚本文件清单 (6个)

| # | 脚本名称 | 文件路径 | 功能描述 | 执行时间 |
|---|----------|----------|----------|----------|
| 1 | morning-ritual.py | `/root/.openclaw/workspace/scripts/cron-tasks/morning-ritual.py` | 晨间图腾仪式 | 07:00 每日 |
| 2 | evening-ritual.py | `/root/.openclaw/workspace/scripts/cron-tasks/evening-ritual.py` | 黄昏图腾归位 | 22:00 每日 |
| 3 | info-firewall-check.py | `/root/.openclaw/workspace/scripts/cron-tasks/info-firewall-check.py` | 信息防火墙检查 | 12:00, 18:00 每日 |
| 4 | self-assessment-calibrator.py | `/root/.openclaw/workspace/scripts/cron-tasks/self-assessment-calibrator.py` | 自我评估校准 | 14:00, 20:00 每日 |
| 5 | checkpoint-health-check.py | `/root/.openclaw/workspace/scripts/cron-tasks/checkpoint-health-check.py` | 检查点健康验证 | 16:00 每日 |
| 6 | knowledge-os-maintenance.py | `/root/.openclaw/workspace/scripts/cron-tasks/knowledge-os-maintenance.py` | 知识OS维护 | 02:00 每日 |

---

## 二、Cron配置

### 配置文件位置
- **配置模板**: `/root/.openclaw/workspace/scripts/cron-tasks/crontab-config.txt`
- **备份文件**: `/tmp/crontab-backup-20260331.txt`
- **当前生效**: `crontab -l` 查看

### 执行时间表 (错峰设计)

```
02:00  ┃ 知识OS维护（深夜低峰期）
07:00  ┃ 晨间图腾仪式
08:47  ┃ 现有晨间报告
12:00  ┃ 信息防火墙检查（午间）
14:00  ┃ 自我评估校准（下午）
16:00  ┃ 检查点健康验证
18:00  ┃ 信息防火墙检查（晚间）
20:00  ┃ 自我评估校准（晚间）
22:00  ┃ 黄昏图腾归位
```

### 已安装Cron条目

```cron
# 环境变量
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
WORKSPACE=/root/.openclaw/workspace
LOG_DIR=$WORKSPACE/logs/cron-tasks

# --- 现有任务 ---
@reboot /root/.openclaw/workspace/scripts/external_supervision.sh supervise
47 8 * * * /bin/bash /root/.openclaw/workspace/scripts/morning_report.sh

# --- 新部署: 周期性任务机制 (6个脚本) ---

# 1. 晨间图腾仪式 - 每日07:00
0 7 * * * cd $WORKSPACE && /usr/bin/python3 $WORKSPACE/scripts/cron-tasks/morning-ritual.py >> $LOG_DIR/morning-ritual-cron.log 2>&1

# 2. 信息防火墙检查 - 每日12:00和18:00
0 12 * * * cd $WORKSPACE && /usr/bin/python3 $WORKSPACE/scripts/cron-tasks/info-firewall-check.py >> $LOG_DIR/info-firewall-check-cron.log 2>&1
0 18 * * * cd $WORKSPACE && /usr/bin/python3 $WORKSPACE/scripts/cron-tasks/info-firewall-check.py >> $LOG_DIR/info-firewall-check-cron.log 2>&1

# 3. 自我评估校准 - 每日14:00和20:00
0 14 * * * cd $WORKSPACE && /usr/bin/python3 $WORKSPACE/scripts/cron-tasks/self-assessment-calibrator.py >> $LOG_DIR/self-assessment-calibrator-cron.log 2>&1
0 20 * * * cd $WORKSPACE && /usr/bin/python3 $WORKSPACE/scripts/cron-tasks/self-assessment-calibrator.py >> $LOG_DIR/self-assessment-calibrator-cron.log 2>&1

# 4. 检查点健康验证 - 每日16:00
0 16 * * * cd $WORKSPACE && /usr/bin/python3 $WORKSPACE/scripts/cron-tasks/checkpoint-health-check.py >> $LOG_DIR/checkpoint-health-check-cron.log 2>&1

# 5. 黄昏图腾归位 - 每日22:00
0 22 * * * cd $WORKSPACE && /usr/bin/python3 $WORKSPACE/scripts/cron-tasks/evening-ritual.py >> $LOG_DIR/evening-ritual-cron.log 2>&1

# 6. 知识OS维护 - 每日02:00（深夜低峰期）
0 2 * * * cd $WORKSPACE && /usr/bin/python3 $WORKSPACE/scripts/cron-tasks/knowledge-os-maintenance.py >> $LOG_DIR/knowledge-os-maintenance-cron.log 2>&1
```

---

## 三、执行测试验证

### 测试方法
```bash
# 手动执行每个脚本
python3 /root/.openclaw/workspace/scripts/cron-tasks/<script-name>.py
```

### 测试结果

| 脚本 | 状态 | 执行时间 | 日志文件 |
|------|------|----------|----------|
| morning-ritual.py | ✅ 通过 | 2026-03-31 08:19:09 | morning-ritual-20260331.log |
| evening-ritual.py | ✅ 通过 | 2026-03-31 08:19:26 | evening-ritual-20260331.log |
| info-firewall-check.py | ✅ 通过 | 2026-03-31 08:19:26 | info-firewall-check-20260331.log |
| self-assessment-calibrator.py | ✅ 通过 | 2026-03-31 08:19:09 | self-assessment-calibrator-20260331.log |
| checkpoint-health-check.py | ✅ 通过 | 2026-03-31 08:19:26 | checkpoint-health-check-20260331.log |
| knowledge-os-maintenance.py | ✅ 通过 | 2026-03-31 08:19:26 | knowledge-os-maintenance-20260331.log |

### 测试输出摘要

#### 1. morning-ritual.py
```
🌅 晨间图腾仪式开始
【步骤1】确认核心身份... ✓ 身份确认: 负熵构造体的初级实现体
【步骤2】系统健康检查... ✓ 系统健康状态: 良好
【步骤3】准备今日记忆文件... = 今日记忆文件已存在，继续沿用
【步骤4】了解用户今日安排... ✓ 已加载用户工作偏好
🌅 晨间图腾仪式完成
状态: 就绪
```

#### 2. evening-ritual.py
```
🌆 黄昏图腾归位仪式开始
【步骤1】归档旧日志... ✓ 归档完成: 0 个文件
【步骤2】汇总今日执行记录... ✓ 今日日志: 4 个文件
【步骤3】检查今日任务完成度... ✓ 今日memory存在
【步骤4】更新晚间总结... ✓ 已更新晚间总结
🌆 黄昏图腾归位仪式完成
```

#### 3. info-firewall-check.py
```
🔒 信息防火墙检查开始
【步骤1】扫描工作空间敏感信息... ✓ 扫描完成: 2535+ 个文件
【步骤2】验证MEMORY.md安全性... ✓ 检查 X 个memory文件
【步骤3】检查临时文件... ✓ 临时文件状态正常
🔒 信息防火墙检查完成
✅ 检查结果: 安全 (未发现敏感信息泄露风险)
```

#### 4. self-assessment-calibrator.py
```
⚖️ 自我评估校准开始
【步骤1】检查核心文件完整性... ✓ 所有核心文件存在
【步骤2】验证核心工作准则... ✓ 诚实准则: 已固化 ✓ Token感知: 已固化 ...
【步骤3】分析今日诚实度指标... memory文件: ✓ 存在
【步骤4】计算校准得分...
⚖️ 自我评估校准完成
⚠️ 校准得分: 80.0/100 (良好)
```

#### 5. checkpoint-health-check.py
```
🏥 检查点健康验证开始
【步骤1】验证checkpoint文件... ✓ Checkpoint文件存在 (1.25 KB) 年龄: 9.8 小时
【步骤2】验证恢复脚本... ✓ 恢复脚本存在 ✓ Python语法有效
【步骤3】检查磁盘空间... ✓ 磁盘空间充足 (14.22 GB 空闲)
【步骤4】检查关键文件... ✓ SOUL.md ✓ AGENTS.md ✓ USER.md ✓ MEMORY.md
🏥 检查点健康验证完成
✅ 健康状态: 良好 (无严重问题)
```

#### 6. knowledge-os-maintenance.py
```
🔧 知识OS维护开始
【步骤1】清理过期日志... ✓ 日志清理完成: 删除 0 个, 归档 0 个
【步骤2】清理过期memory文件... ✓ Memory清理完成: 0 个文件
【步骤3】清理临时文件... ✓ 临时文件清理: 0 个文件, 0.0 MB
【步骤4】生成文件系统统计... ✓ 文件统计: 25632 个文件, 2487 个目录
🔧 知识OS维护完成
✅ 维护完成: 无需清理
```

---

## 四、韧性设计特性

每个脚本都包含以下韧性设计：

### 1. 超时保护
- 所有脚本使用 `signal.alarm()` 设置执行超时
- 超时后自动退出并返回错误码

```python
def set_timeout(seconds=300):  # 默认5分钟
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
```

### 2. 错误处理
- 所有关键操作包裹在 try-except 块中
- 详细错误日志记录
- 返回不同的状态码表示不同错误类型

```python
except TimeoutError:
    logger.error("⏱ 脚本执行超时")
    sys.exit(2)
except Exception as e:
    logger.error(f"💥 脚本执行异常: {e}")
    sys.exit(3)
```

### 3. 状态码设计
| 状态码 | 含义 |
|--------|------|
| 0 | 成功/正常 |
| 1 | 警告（轻微问题） |
| 2 | 严重问题/超时 |
| 3 | 执行异常 |
| 4+ | 其他错误 |

### 4. 日志记录
- 所有操作记录到独立的日志文件
- 日志路径: `/root/.openclaw/workspace/logs/cron-tasks/`
- 日志命名: `<script-name>-YYYYMMDD.log`

---

## 五、目录结构

```
/root/.openclaw/workspace/
├── scripts/
│   └── cron-tasks/
│       ├── morning-ritual.py              # 晨间仪式
│       ├── evening-ritual.py              # 黄昏归位
│       ├── info-firewall-check.py         # 信息防火墙
│       ├── self-assessment-calibrator.py  # 自我评估
│       ├── checkpoint-health-check.py     # 检查点健康
│       ├── knowledge-os-maintenance.py    # 知识OS维护
│       └── crontab-config.txt             # Cron配置模板
└── logs/
    └── cron-tasks/
        ├── morning-ritual-20260331.log
        ├── evening-ritual-20260331.log
        ├── info-firewall-check-20260331.log
        ├── self-assessment-calibrator-20260331.log
        ├── checkpoint-health-check-20260331.log
        ├── knowledge-os-maintenance-20260331.log
        └── .calibrator_state.json         # 校准状态
```

---

## 六、后续操作

### 验证Cron运行
```bash
# 查看cron日志
tail -f /var/log/cron.log

# 查看特定脚本日志
tail -f /root/.openclaw/workspace/logs/cron-tasks/morning-ritual-cron.log
```

### 手动触发任务
```bash
# 进入工作目录
cd /root/.openclaw/workspace

# 手动执行任意脚本
python3 scripts/cron-tasks/morning-ritual.py
```

### 修改执行时间
```bash
# 编辑crontab
crontab -e

# 修改对应条目的时间字段后保存
```

### 临时禁用任务
```bash
# 在crontab中注释掉对应行
# 0 7 * * * cd $WORKSPACE && /usr/bin/python3 ...
```

---

## 七、部署验证清单

- [x] 6个脚本文件已创建
- [x] 脚本已添加可执行权限
- [x] 日志目录已创建
- [x] 所有脚本手动执行测试通过
- [x] Cron配置已生成
- [x] Cron任务已安装
- [x] 现有任务已保留（@reboot, 8:47晨间报告）
- [x] 部署文档已创建

---

**部署完成时间**: 2026-03-31 08:20  
**任务状态**: ✅ 完成
