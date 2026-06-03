# OpenClaw 存储安全红线 V1.0

> 创建时间: 2026-03-27  
> 目的: 防止循环备份等存储事故再次发生

---

## 🚫 六大红线（硬约束）

| 红线 | 阈值 | 超限后果 | 自动防护 |
|------|------|----------|----------|
| 备份嵌套 | ≤ 1 层 | 无限循环、磁盘耗尽 | ✅ 脚本自动检测终止 |
| 单次备份大小 | ≤ 2GB | IO阻塞、同步失败 | ✅ 脚本自动跳过 |
| workspace总占用 | ≤ 20GB | 根目录满、系统崩溃 | ✅ 定时监控告警 |
| 磁盘剩余空间 | ≥ 5GB | ENOSPC错误 | ✅ 自动清理触发 |
| 临时文件保留 | ≤ 24小时 | /tmp溢出 | ✅ 自动清理 |
| 备份频率 | ≥ 1小时 | 资源争抢 | ✅ 当前已禁用手动触发 |

---

## ⚙️ 防护机制清单

### 已部署的防护

| 机制 | 文件路径 | 运行频率 | 作用 |
|------|----------|----------|------|
| 嵌套检测 | `scripts/shadow-clone-sync-v2.sh` | 手动触发 | 备份前检查嵌套，发现即终止 |
| 循环扫描 | `scripts/backup-safety-check.sh` | 每小时 | 扫描全系统，发现嵌套立即告警 |
| 磁盘监控 | `scripts/disk-monitor.sh` | 每30分钟 | 超80%自动清理临时文件 |
| 大小限制 | 内置于v2脚本 | 每次备份 | 超2GB自动跳过 |

### 安全脚本使用指南

```bash
# 手动执行安全备份（修复版）
./scripts/shadow-clone-sync-v2.sh

# 手动检查循环备份
./scripts/backup-safety-check.sh

# 手动清理磁盘
./scripts/disk-monitor.sh
```

---

## 📊 监控日志位置

| 日志 | 路径 | 查看命令 |
|------|------|----------|
| 备份日志 | `/var/log/shadow-clone.log` | `tail -f /var/log/shadow-clone.log` |
| 安全检查日志 | `/var/log/backup-safety-check.log` | `tail -20 /var/log/backup-safety-check.log` |
| 磁盘监控日志 | `/var/log/disk-monitor.log` | `tail -20 /var/log/disk-monitor.log` |

---

## 🚨 应急预案

### 场景1: 发现嵌套备份
```bash
# 立即停止所有备份任务
crontab -l | grep -v "shadow-clone" | crontab -

# 移动问题目录到回收站
mv /root/.openclaw/workspace/shadow-clone /tmp/trash-shadow-clone-$(date +%Y%m%d-%H%M%S)

# 验证清理结果
df -h && du -sh /root/.openclaw/workspace
```

### 场景2: 磁盘满 (ENOSPC)
```bash
# 紧急清理
df -h  # 确认问题
find /tmp -type f -delete  # 清理临时文件
rm -rf /tmp/trash-*  # 清理回收站

# 重启OpenClaw（如果需要）
openclaw gateway restart
```

### 场景3: 误删恢复
影子备份已被安全移动到 `/tmp/trash-shadow-clone-时间戳/`，可随时恢复第一层非嵌套数据。

---

## 📝 审计记录

| 日期 | 事件 | 处理 | 状态 |
|------|------|------|------|
| 2026-03-27 | 发现20+层嵌套备份 | 停止任务、清理8.9GB、修复脚本 | ✅ 已解决 |

---

## 责任人
- **监控执行**: 系统自动
- **异常响应**: Kimi Claw (满意妞)
- **策略更新**: Egbertie (指挥官)

---

*最后更新: 2026-03-27 13:30*
