# 2026-06-06 腾讯云CVM部署全程实录

> 📅 2026-06-06 周六  
> ⏱️ 21:00 ~ 23:10 CST  
> 🖥️ 腾讯云 CVM ins-h3yc7m0w · IP 101.33.219.144  
> 👤 操作人: 满意红 (OpenClaw Agent)  
> 👨 用户: Egbertie Lau

---

## 对话流程

### 1. 用户给出服务器信息
```
公网IP: 101.33.219.144
root密码: (已提供)
域名: 先不用
```

### 2. SSH 连接与摸底
- 尝试 sshpass → 不可用 → 用 expect + ssh-copy-id 部署密钥
- 连接成功 → OS: TencentOS Server 4 · CPU: 2核 AMD EPYC · Mem: 3.6G
- 磁盘: 系统盘 50G (8% used) · 数据盘 50G (挂载到 /mnt/datadisk0)
- 已装: Python3 · 待装: Git / Nginx / pip3

### 3. 基础环境安装
```
dnf install -y git nginx python3-pip
pip3 install flask flask-cors bcrypt pyjwt gunicorn
systemctl enable nginx --now
```

### 4. 项目部署
- 尝试 git clone → 仓库太大超时
- 改用 tar 打包 → macOS xattr 导致解压后仅剩 server/ 目录
- **改用 rsync -avz** → 314 文件完整同步 ✅
- `chmod -R a+rX` 修权限 → 解决 Nginx 403

### 5. Nginx 配置
- 站点配置: /etc/nginx/conf.d/satisficing-lab.conf
- 根目录: /mnt/datadisk0/satisficing-lab
- /api/ → proxy_pass http://127.0.0.1:5050
- 安全头: include security-headers.conf

### 6. 端口不匹配修复
- config.py 默认 PORT=5000，Nginx 代理到 5050
- 统一改 config.py 为 5050 → API 正常

### 7. SSH 安全加固 (2次失败，1次成功)
**第1次失败**: sed 误匹配，Port 22 → Port 222222
- 21:53 VNC 恢复 → sed误写 → iptables DROP 22
- 21:55 VNC → iptables -F → sshd restart → 22端口恢复

**第2次失败**: 再次 sed 改 Port，`#Port 22 → Port 22 (original, kept for fallback)` 
- sshd -t 失败 → 22端口全断
- 22:41 VNC → 登录 → cp sshd_config.orig → systemctl start sshd → 恢复

**第3次成功**: 改用零风险方案
- 不动 sshd Port，只改认证方式
- iptables 独立控制端口暴露: policy DROP · 仅开 22/80/443/ICMP
- 恢复方式: VNC → iptables -F (极简)

### 8. Flask → Gunicorn 生产部署
- 安装 gunicorn → systemd 服务化
- 首次启动失败: `Failed to find attribute 'app' in 'server.app'`
- 原因: Flask app 在 `if __name__ == "__main__"` 内创建
- 修复: app.py 末尾添加 `app = create_app()`
- 最终: Gunicorn 2 workers, 正常运行

### 9. 飞书集成测试
- Webhook: ✅ 发送成功 (msg: success)
- App Secret: ❌ `app secret invalid` — 需到飞书后台确认

### 10. 备份体系
- 备份脚本: /usr/local/bin/sri-backup.sh (tar代码+配置文件)
- 首次备份: 520MB
- Cron: 每天3点自动备份，7天保留
- logrotate: 每日轮转，7天保留

### 11. 云端 Cron
- 5条定时任务: 备份/健康检查/日志清理/磁盘监控/日志轮转

### 12. 浏览器操作 (VNC救援)
- 登录腾讯云控制台 (邮箱+密码+验证码)
- 查看安全组: sg-rviz2a9t，入站规则含 TCP:22 ✅
- VNC 登录: 命令行操作 → 恢复 SSH

---

## 最终状态

| 服务 | 端口 | 状态 | 自启 |
|:--|:--|:--|:--|
| sshd | 22 | ✅ active | ✅ |
| nginx | 80 | ✅ active | ✅ |
| sri-api (Gunicorn) | 127.0.0.1:5050 | ✅ active | ✅ |
| 飞书 Webhook | — | ✅ | — |
| 备份 | — | ✅ 520MB | 每天3点 |

## 访问地址
- http://101.33.219.144/ — 品牌首页
- http://101.33.219.144/dashboard-v3.html — 驾驶舱
- http://101.33.219.144/admin-windows.html — 管理后台
- http://101.33.219.144/api/health — API健康

---

> 📄 技术报告: `Projects/满意解研究所/10_运营体系/腾讯云CVM部署技术报告_2026-06-06.md`  
> 📄 配置快照: `Projects/满意解研究所/10_运营体系/腾讯云CVM配置快照_2026-06-06.md`  
> 📄 记忆: `memory/2026-06-06.md`
