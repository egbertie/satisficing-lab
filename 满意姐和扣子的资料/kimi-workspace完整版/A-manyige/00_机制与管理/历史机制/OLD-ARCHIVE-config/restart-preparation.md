# OpenClaw Gateway 重启准备清单

**准备时间**: 2026-03-29 18:30  
**执行人**: Egbertie（手动重启）  
**状态**: ✅ 准备完成，等待执行

---

## 重启前状态

| 指标 | 数值 | 状态 |
|------|------|------|
| Gateway PID | 2139173 | 运行中 |
| 内存使用 | 1.3 Gi / 7.8 Gi | 正常（重启前已部分释放） |
| 磁盘使用 | 62% | 正常 |
| 系统负载 | 待检查 | - |

**注意**: 内存从之前的7.0Gi降至1.3Gi，可能已部分自动释放，但仍建议重启确保干净状态。

---

## 重启步骤

### Step 1: 保存当前工作（已完成）
- ✅ 五路图腾Skill已保存
- ✅ 监控脚本已部署
- ✅ 反思报告已记录

### Step 2: 优雅停止Gateway

```bash
# 方法1: 优雅停止（推荐）
kill -15 2139173

# 等待10秒确认停止
sleep 10
ps aux | grep openclaw-gateway

# 如果仍在运行，强制停止
kill -9 2139173
```

### Step 3: 检查并修复Config（如需要）

**已知问题**: config中有未识别键
```
- agents.defaults.subagents.reserveForUser
- agents.defaults.subagents.description
```

**修复命令**:
```bash
openclaw doctor --fix
```

**或手动修复**:
编辑 `/root/.openclaw/openclaw.json`，删除上述两个键

### Step 4: 启动Gateway

```bash
# 方法1: 使用openclaw命令
openclaw gateway start

# 方法2: 直接启动（如命令不可用）
# 查看具体启动方式
which openclaw-gateway
```

### Step 5: 验证启动

```bash
# 检查进程
ps aux | grep openclaw-gateway

# 检查内存使用
free -h

# 检查日志
tail -20 /root/.openclaw/logs/openclaw.log
```

---

## 重启后验证清单

- [ ] Gateway进程已启动
- [ ] 内存使用 < 1GB（初始状态）
- [ ] 日志无报错
- [ ] 连接器能正常接收消息
- [ ] 工具调用正常

---

## 风险与回滚

| 风险 | 概率 | 应对 |
|------|------|------|
| 启动失败 | 低 | 检查config，使用doctor --fix |
| 连接丢失 | 中 | 重新扫描二维码绑定 |
| 配置丢失 | 低 | config已备份，可手动恢复 |

**回滚方案**: 如启动失败，保留当前运行的PID 2139173，不要强制杀死，先排查问题。

---

## 配置文件备份

位置: `/root/.openclaw/openclaw.json`

关键配置已确认:
- ✅ Kimi API Key 已配置
- ✅ 浏览器路径已配置
- ✅ 日志路径已配置
- ⚠️ 两个未识别键需要修复

---

## 执行命令摘要

```bash
# 1. 停止
kill -15 2139173
sleep 10

# 2. 修复config
openclaw doctor --fix

# 3. 启动
openclaw gateway start

# 4. 验证
ps aux | grep openclaw-gateway
free -h
```

---

**准备完成，等待执行指令。**

## 知识内化记录
**内化时间**: 2026-03-31 | **状态**: ✅ 已内化
