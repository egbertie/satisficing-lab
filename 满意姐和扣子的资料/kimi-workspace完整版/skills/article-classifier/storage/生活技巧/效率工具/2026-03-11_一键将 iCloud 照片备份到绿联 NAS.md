# 一键将 iCloud 云盘照片/视频直接备份到绿联 NAS 私有云

**来源**: 绿联 NAS 私有云 (微信公众号)  
**原文链接**: https://mp.weixin.qq.com/s/te5Bw3LVsHxZ3W-utmoIaQ  
**收录日期**: 2026-03-11  
**分类**: 生活技巧 / 效率工具  

---

## 文章摘要

针对 iPhone 用户想换 Android 手机时，iCloud 大量照片同步困难的问题，提供通过 Docker Compose 部署一键将 iCloud 所有照片直接备份到绿联 NAS 的解决方案。

---

## 核心内容

### 适用场景
- iPhone 用户想换 Android 手机
- iCloud 有成千上万张照片需要快速同步
- 不想从 iCloud 一张张手动下载

### 系统要求
- 绿联 NAS UGOS Pro 系统
- 支持 Docker 环境

### 部署步骤

#### 1. 前期准备
1. 在文件管理器的【共享文件夹-docker】下创建 `iCloud` 文件夹
2. 在该文件夹下创建两个子文件夹：
   - `config` - 存放配置文件
   - `picture` - 存放从 iCloud 下载的照片
3. 新建一个文本文档，命名为 `.mounted`（空文件），上传到 `picture` 文件夹
   - ⚠️ 注意：没有该文件，备份任务不会运行
4. 在 Docker 应用中创建专用网络：
   - 网络名称：`icloudpd_bridge`
   - IPv4 配置：取消"自动分配"，手动设置子网和网关

#### 2. Docker Compose 部署
1. 打开 Docker 应用，选择"项目 - 创建"
2. 项目名称：建议命名为 `icloudpd`
3. 存储路径：选择【共享文件夹-docker-iCloud】
4. 导入 yaml 配置文件（公众号后台发送"iCloud"获取）
5. 配置参数调整：
   - `TZ`: 时区，默认 `Asia/Shanghai`（非国区 Apple ID 需调整）
   - 两个布尔参数：默认 `True`（非国区改为 `false`）
   - `apple_id`: 替换为你的 Apple ID
   - 如果 Apple ID 未启用双重验证，需改为 `web`
   - `{user_id}`: 换成 UGOS Pro 系统的本地账号名
   - `config` 路径：换成 `/共享/docker-iCloud-config` 的实际路径
   - `iCloud` 路径：换成 `/共享/docker-iCloud-picture` 的实际路径
6. 点击"立即部署"（如镜像拉取超时，需配置 Docker 加速源）

#### 3. icloudpd 配置
1. 在 Docker-容器中确认 `icloudpd` 已部署
2. 进入控制台 → 终端 → 新增，命令修改为 `/bin/sh`
3. 输入命令：`/usr/local/bin/sync-icloud.sh --Initialise`
4. 配置 Apple ID 的 MFA 认证：
   - 输入 Apple ID 密码（不显示）
   - 输入 `y` 确认
   - 在 iPhone/Mac/Apple Watch/iPad 上获取验证码并输入
   - 再次输入收到的验证码
5. 看到 `successful` 提示表示配置成功
6. 输入 `exit` 退出，重启容器
7. 查看日志，等待照片下载完成

---

## 注意事项

⚠️ **重要提醒**:
- 路径严格区分大小写，请仔细核对
- 镜像属第三方开发，具体配置变动和 Bug 修复请关注第三方信息
- 绿联仅提供 Docker 环境支持，不对操作失误造成的风险负责
- 请自行判断并承担使用风险

---

## 关键词

iCloud, NAS, 绿联, Docker, 照片备份, 数据同步, 效率工具

---

*本文档由 article-classifier 技能自动分类存储*
