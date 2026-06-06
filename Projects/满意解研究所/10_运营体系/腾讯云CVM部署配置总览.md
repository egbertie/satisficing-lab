# 腾讯云 CVM 部署配置总览

> 2026-06-06 21:50 · 阶段一：摸底+规划
> 原则：不经过 GitHub，全部由腾讯云承接，发掘最大能力

---

## 一、硬件配置

| 项目 | 详情 |
|:--|:--|
| **实例ID** | ins-h3yc7m0w |
| **CPU** | 2核 AMD EPYC 7K62 @ 2.6GHz |
| **内存** | 3.6 GB (无 Swap) |
| **系统盘** | 50GB SSD 云硬盘 (/dev/vda1 · XFS · 已用 8%) |
| **数据盘** | 50GB SSD 云硬盘 (/dev/vdb · EXT4 · 已用 2%) |
| **公网IP** | 101.33.219.144 |
| **内网IP** | 172.16.16.3/20 |
| **带宽** | ~5 Mbps (估) |
| **OS** | TencentOS Server 4 (RHEL 9兼容) |
| **内核** | 6.6.117 x86_64 |
| **时区** | Asia/Shanghai |

## 二、当前服务

| 服务 | 端口 | 状态 | 路径 |
|:--|:--|:--|:--|
| SSH | 22 | ✅ | `/etc/ssh/sshd_config` |
| Nginx | 80 | ✅ | `/etc/nginx/conf.d/satisficing-lab.conf` |
| Python API (Flask) | 127.0.0.1:5050 | ✅ | `/mnt/datadisk0/satisficing-lab/server/app.py` |
| 腾讯云TAT | — | ✅ | 自动化助手 |

## 三、部署架构规划

```
                        101.33.219.144
                              │
                    ┌─────────┴─────────┐
                    │   Nginx :80/:443  │  ← 反向代理 + HTTPS + 静态文件
                    │   静态文件根:      │
                    │   /mnt/datadisk0/  │
                    │   satisficing-lab/ │
                    └────────┬──────────┘
                             │ proxy_pass
                    ┌────────┴──────────┐
                    │  Gunicorn :5050   │  ← 生产级 WSGI
                    │  (4 workers)      │
                    │  Flask app        │
                    └───────────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
        飞书API         飞书邮件       多维表格
        (Webhook)      (SMTP)        (Bitable)
```

## 四、磁盘规划

```
/dev/vda (50GB 系统盘)
  /                          50GB  ← OS + 系统软件
  (预留 45GB)

/dev/vdb (50GB 数据盘)
  /mnt/datadisk0/
    ├── satisficing-lab/     2GB  ← 项目代码 + 静态文件
    ├── backups/              ×GB  ← 定时备份 (tar.gz)
    ├── logs/                 ×GB  ← Nginx + App 日志
    ├── data/                 ×GB  ← SQLite 数据库 + JSON
    └── uploads/              ×GB  ← 用户上传文件
```

## 五、待完成清单

### 阶段一：安全加固 (进行中)
- [ ] 关闭密码登录，仅密钥认证
- [ ] 修改 SSH 端口 (22 → 非标)
- [ ] 安装 fail2ban 防暴力破解
- [ ] 飞书 Secret 移入环境变量
- [ ] 配置防火墙规则 (仅开放 80/443)

### 阶段二：生产级部署
- [ ] Gunicorn 替代 Flask dev server
- [ ] systemd 服务优化 (worker数量/权限)
- [ ] Nginx HTTPS 预留 (等域名备案)
- [ ] 静态资源缓存策略优化
- [ ] 日志轮转 (logrotate)

### 阶段三：腾讯云能力挖掘
- [ ] 对象存储 COS (静态文件加速分发)
- [ ] CDN 加速 (等域名)
- [ ] 云监控 Agent 安装
- [ ] 快照策略 (每日自动快照数据盘)
- [ ] 告警策略 (CPU>80% / 磁盘>80%)

### 阶段四：飞书集成
- [ ] 飞书邮箱 SMTP 配置 (等域名)
- [ ] Webhook 通知测试
- [ ] 多维表格数据同步验证

### 阶段五：备份体系
- [ ] 每日 tar 备份 (代码+数据)
- [ ] 快照自动策略
- [ ] 备份保留 (7天循环)
- [ ] 恢复演练

### 阶段六：Cron 迁移
- [ ] 评估哪些 Cron 需要迁移到 CVM
- [ ] 创建 CVM 上的 Cron 任务
- [ ] 同步校验 (本地 ↔ 云端)
