# 满意解研究所 · 腾讯云 CVM 部署指南 v1.0

> 目标：一键部署前端（COS/EdgeOne）+ 后端（Flask + SQLite）+ 飞书集成

---

## 前置条件

- [x] 腾讯云账号 + 实名认证
- [x] 域名（备案通过后可用）
- [ ] CVM 云服务器（建议：2核4G 5M · 轻量应用服务器 ~¥188/年）
- [ ] 云硬盘（50GB 起步，存放 SQLite + 静态文件）

---

## 第一步：CVM 初始化

```bash
# SSH 登录
ssh root@你的CVM公网IP

# 安装基础环境
yum install -y python3 git nginx  # CentOS
# 或
apt install -y python3 git nginx  # Ubuntu

# 安装 Python 依赖
pip3 install flask flask-cors bcrypt pyjwt
```

---

## 第二步：代码部署

```bash
# 克隆项目
cd /opt
git clone https://github.com/egbertie/satisficing-lab.git
cd satisficing-lab

# 初始化数据库
python3 -c "from server.app import create_app; create_app()"

# 启动后端
nohup python3 server/app.py > /var/log/sri.log 2>&1 &
```

---

## 第三步：Nginx 反向代理

```nginx
server {
    listen 80;
    server_name 你的域名.com www.你的域名.com;

    # 前端静态文件
    root /opt/satisficing-lab;
    index index.html;

    # 后端 API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:5050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 静态文件缓存
    location ~* \.(html|css|js|png|jpg|svg)$ {
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## 第四步：修改前端 API 地址

部署前需要修改两个文件中的 API base URL：

### sri-api.js
```javascript
base: "http://127.0.0.1:5050" → "https://api.你的域名.com"
```

### sri-track.js
```javascript
base: "http://127.0.0.1:5050" → "https://api.你的域名.com"
```

### admin-windows.html
```javascript
// 搜索所有 'http://127.0.0.1:5050' → 替换为 'https://api.你的域名.com'
```

---

## 第五步：飞书邮箱配置

域名备案通过后，在飞书管理后台绑定域名：

1. 飞书管理后台 → 邮箱 → 域名管理 → 添加域名
2. 配置 MX 记录指向飞书
3. 配置 SPF/DKIM 防伪造
4. 生成 SMTP 专用密码

然后更新 `server/config.py`：
```python
EMAIL_SENDER = "hello@你的域名.com"
```

---

## 第六步：HTTPS + 自动续期

```bash
# 安装 certbot
yum install -y certbot python3-certbot-nginx

# 申请证书
certbot --nginx -d 你的域名.com -d www.你的域名.com

# 自动续期
echo "0 3 * * * root certbot renew --quiet" >> /etc/crontab
```

---

## 第七步：监控 + 自动重启

```bash
# systemd 服务文件 /etc/systemd/system/sri-api.service
[Unit]
Description=满意解研究所 API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/satisficing-lab
ExecStart=/usr/bin/python3 server/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
systemctl enable sri-api
systemctl start sri-api
systemctl status sri-api
```

---

## 回滚方案

如果部署出错：
```bash
git checkout <上一个稳定版本>
systemctl restart sri-api
```

---

## 成本预估

| 项目 | 年费 |
|------|------|
| 轻量应用服务器 2核4G 5M | ¥188 |
| 云硬盘 50GB | ~¥200 |
| COS 静态托管（备选） | ~¥56 |
| 域名 | ~¥60 |
| SSL 证书 | ¥0（Let's Encrypt） |
| **合计** | **~¥504/年** |
