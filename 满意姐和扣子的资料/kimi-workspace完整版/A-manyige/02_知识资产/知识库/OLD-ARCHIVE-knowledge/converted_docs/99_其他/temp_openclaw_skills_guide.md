# temp_openclaw_skills_guide
> 原始文件: `temp_openclaw_skills_guide.pdf`
> 转换时间: 2026-03-27 13:36:41
> 转换工具: pdfplumber → Markdown

---

## 第 1 页

Sharp科技
OpenClaw Skills
完全指南
系统性整理 OpenClaw 官方及社区常用 Skills
为中国用户提供实用的使用手册
作者：Sharp科技 · AI 助手整理 日期：2026 年 2 月 26 日 版本：v1.0

## 第 2 页

目 录
第一部分：概述 ............................................................................................. 3
1.1 OpenClaw Skills 机制简介 .......................................................................... 3
1.2 Skills 安装的通用方法 .............................................................................. 3
1.3 国内环境特殊配置 .................................................................................. 5
第二部分：Skills 分类目录 ................................................................................. 6
2.1 搜索类 Skills ......................................................................................... 6
2.2 网页操作类 Skills .................................................................................... 8
2.3 文件处理类 Skills .................................................................................... 9
2.4 代码执行类 Skills .................................................................................. 11
2.5 数据库类 Skills ..................................................................................... 12
2.6 AI 模型类 Skills ..................................................................................... 13
2.7 通讯类 Skills ........................................................................................ 15
2.8 工具类 Skills ........................................................................................ 17
第三部分：国内用户专属推荐 ........................................................................... 18
3.1 开箱即用 Skills 清单 ............................................................................... 18
3.2 国产平替方案汇总 ................................................................................. 19
3.3 最佳实践组合推荐 ................................................................................. 19
第四部分：附录 ........................................................................................... 20
4.1 常见报错及解决方案 .............................................................................. 20
4.2 API Key 申请指南汇总表 .......................................................................... 22
4.3 费用对比一览表 .................................................................................... 22
参考资源 .................................................................................................... 23
官方资源 ................................................................................................ 23
社区资源 ................................................................................................ 24
国内部署教程 .......................................................................................... 24
更新日志 .................................................................................................... 24

## 第 3 页

OpenClaw Skills 完全指南 Sharp科技
第一部分：概述
1.1 OpenClaw Skills 机制简介
什么是 OpenClaw
OpenClaw（原名 Clawdbot/Moltbot）是一款开源的个人 AI 助手框架，能够在你的设备上本地运行，连
接各种消息平台（WhatsApp、Telegram、Slack、Discord、飞书、企业微信、QQ 等），并通过 Skills
（技能）系统扩展其能力。
OpenClaw 的核心价值在于：
● 本地执行：数据存储在本地，完全掌控隐私
● 真实执行：不只是对话，能真正操作你的电脑和外部服务
● 多平台集成：支持 10+ 通讯平台，统一入口管理
● 持久记忆：保存对话历史和用户偏好，越用越智能
● 开源免费：零订阅费用，自主可控
什么是 Skills
Skills 是 OpenClaw 的模块化扩展机制，每个 Skill 是一个包含 SKILL.md 文件的文件夹，通过自
然语言描述教 AI 如何执行特定任务。
Skills 的核心特点：
● 自包含：每个 Skill 独立封装，包含描述、使用说明和实现代码
● 即插即用：安装后立即生效，无需重启整个系统
● 权限可控：每个 Skill 声明所需权限，用户自主决定是否授权
● 可组合：多个 Skills 可以联动，构建复杂工作流
Skills 生态系统规模
截至 2026 年 2 月：
● ClawHub 官方市场收录 5,700+ 个社区 Skills
- 经 Awesome-OpenClaw-Skills 筛选后约 3,000+ 高质量 Skills
● 覆盖 30+ 个功能分类
● 日新增 Skills 数量持续增长
1.2 Skills 安装的通用方法
方式一：ClawHub CLI（推荐）
OpenClaw 提供官方 CLI 工具 clawhub，这是最简便的安装方式：
# 安装指定 Skill
clawhub install <skill-name>
# 示例：安装天气查询 Skill
clawhub install weather
— 3 —

## 第 4 页

OpenClaw Skills 完全指南 Sharp科技
# 安装指定版本
clawhub install nano-pdf --version 1.2.0
# 强制安装（覆盖旧版本）
clawhub install summarize --force
常用 CLI 命令：
命令 功能
clawhub search <关键词> 搜索 Skills
clawhub info <skill-name> 查看 Skill 详情
clawhub list 列出已安装的 Skills
clawhub update <skill-name> 更新指定 Skill
clawhub update --all 更新所有 Skills
clawhub uninstall <skill-name> 卸载 Skill
clawhub disable <skill-name> 禁用 Skill（不卸载）
clawhub enable <skill-name> 启用已禁用的 Skill
方式二：手动安装
如果你想修改 Skill 源码或安装未上架的 Skill：
# 全局安装（所有项目可用）
cp -r <skill-folder> ~/.openclaw/skills/
# 项目内安装（仅当前项目可用）
cp -r <skill-folder> <your-project>/skills/
# 安装后重启 Gateway
openclaw gateway restart
Skills 加载优先级：
项目目录 /skills/ > 本地目录 ~/.openclaw/skills/ > 内置 Skills
方式三：对话安装（最简单）
直接在 OpenClaw 聊天框粘贴 GitHub Skill 仓库链接：
帮我安装这个技能：https://github.com/openclaw/skills/tree/main/web-search
AI 会自动下载、配置并安装该 Skill，适合零基础用户。
安装后的配置
— 4 —

## 第 5 页

OpenClaw Skills 完全指南 Sharp科技
部分 Skills 需要额外配置：
# 配置指定 Skill
openclaw skill configure <skill-name>
# 示例：配置 Obsidian Skill
openclaw skill configure obsidian --vault-path /root/ObsidianVault
1.3 国内环境特殊配置
网络代理配置
由于 OpenClaw 的官方文档和安装脚本托管在海外服务器，国内用户建议配置代理：
# 临时设置代理（当前终端会话有效）
export https_proxy=http://127.0.0.1:你的代理端口
# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export https_proxy=http://127.0.0.1:7890' >> ~/.bashrc
source ~/.bashrc
Docker 镜像源配置
如果使用 Docker 部署，建议配置国内镜像源：
# 编辑 Docker 配置文件
sudo nano /etc/docker/daemon.json
# 添加以下内容
{
"registry-mirrors": [
"https://docker.1ms.run",
"https://docker.mirrors.ustc.edu.cn",
"https://hub-mirror.c.163.com"
]
}
# 重启 Docker 服务
sudo systemctl restart docker
Skills 镜像源配置
部分 Skills 依赖的外部包可能需要切换国内源：
# 配置 OpenClaw 使用国内 Skills 镜像源
openclaw config set skills.registry https://registry.cn-hangzhou.aliyuncs.com/openclaw/skills
# Python pip 国内镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
— 5 —

## 第 6 页

OpenClaw Skills 完全指南 Sharp科技
# Node.js npm 国内镜像
npm config set registry https://registry.npmmirror.com
国内大模型配置（推荐）
优先使用国内大模型，延迟更低、费用更省：
# 配置通义千问（免费额度充足）
openclaw config set 'models.providers.qwen' --json '{
"baseUrl": "https://dashscope.aliyun.com/compatible-mode/v1",
"apiKey": "你的Qwen_API_Key",
"api": "openai-completions",
"models": [{ "id": "qwen-plus", "name": "Qwen Plus" }]
}'
# 设置默认模型
openclaw models set qwen/qwen-plus
第二部分：Skills 分类目录
2.1 搜索类 Skills
Skill 名称 功能简介 国内可用性 API Key 费用
web_search 网页搜索（默认 需代理 Brave API Key 免费额度
Brave）
serper Google 搜索 via 需代理 Serper API Key 免费+付费
Serper API
perplexity AI 搜索+总结 需代理 Perplexity API 付费
Key
firecrawl 网页抓取+搜索 直接可用 Firecrawl API 免费额度
Key
tavily AI 优化搜索 需代理 Tavily API Key 免费额度
exa 神经网络搜索 需代理 Exa API Key 付费
web_search（内置搜索）
功能简介：OpenClaw 内置的网页搜索工具，支持多种搜索后端
详细能力：
● 支持 Brave（默认）、Perplexity、Gemini
三种搜索后端 - 返回结构化搜索结果（标题、URL、摘要） - 支持区域和语言定制 - 结果缓存 15 分钟
国内可用性：需代理（Brave 为国内不可用）
API Key 要求：
— 6 —

## 第 7 页

OpenClaw Skills 完全指南 Sharp科技
● Brave：免费申请 BRAVE_API_KEY -
Perplexity：需要 Perplexity 账号 - Gemini：需要 Google API Key
费用情况：
● Brave：每月 2,000 次免费查询 -
Perplexity：按调用量付费 - Gemini：免费额度充足
安装命令：
# 无需安装，内置工具
# 配置 Brave API Key
openclaw config set tools.web.search.apiKey "你的Brave_API_Key"
配置示例：
{
"tools": {
"web": {
"search": {
"enabled": true,
"provider": "brave",
"apiKey": "BRAVE_API_KEY_HERE",
"maxResults": 5,
"timeoutSeconds": 30
}
}
}
}
国内替代方案：
● 使用 Gemini 搜索（国内可访问）
● 使用
Firecrawl 的搜索功能 - 自建 SearXNG 搜索实例
firecrawl
功能简介：强大的网页抓取和搜索工具，支持 JS 渲染页面
详细能力：
● 网页内容抓取（支持 JavaScript 渲染） -
网站地图生成 - 结构化数据提取 - 搜索功能
国内可用性：直接可用
API Key 要求：Firecrawl API Key（免费注册）
费用情况：
● 免费版：每月 500 积分
● 付费版：$0.002/积分起
安装命令：
clawhub install firecrawl-skills
配置示例：
— 7 —

## 第 8 页

OpenClaw Skills 完全指南 Sharp科技
{
"tools": {
"web": {
"fetch": {
"firecrawl": {
"apiKey": "fc-YOUR-API-KEY"
}
}
}
}
}
常见问题：
● 免费额度用完后会报错，需等待下月重置或升级付费 -
部分网站有反爬机制，可能需要重试
2.2 网页操作类 Skills
Skill 名称 功能简介 国内可用性 API Key 费用
browser 浏览器自动化（Playwright） 直接可用 无需 免费
agent-browser 无头浏览器控制 直接可用 无需 免费
browsy 轻量级网页浏览 直接可用 无需 免费
playwright-cli Playwright CLI 封装 直接可用 无需 免费
web-scraper 结构化数据采集 直接可用 无需 免费
screenshot-skill 网页截图 直接可用 无需 免费
browser（内置浏览器）
功能简介：基于 Playwright 的完整浏览器自动化
详细能力：
● 网页导航、点击、表单填写
● 数据提取和截图 -
多步骤工作流自动化 - 支持登录态保持
国内可用性：直接可用
API Key 要求：无需
费用情况：免费
安装命令：
# 内置工具，需安装 Playwright 依赖
npx playwright install chromium
配置示例：
{
"tools": {
— 8 —

## 第 9 页

OpenClaw Skills 完全指南 Sharp科技
"browser": {
"enabled": true,
"headless": false
}
}
}
使用示例：
用户：帮我查询 Amazon 上 AirPods Pro 的价格
OpenClaw：打开 Amazon → 搜索 AirPods Pro → 提取价格信息
常见问题：
● 首次使用需下载 Chromium，约 100MB -
部分网站检测自动化工具，可能需要 stealth 模式 - 内存占用较高，低配服务器建议用 browsy 替代
browsy
功能简介：轻量级网页浏览工具，速度快、资源占用低
详细能力：
● 快速网页内容提取
● 自动处理 Cookie 同意弹窗 -
支持登录墙绕过 - 表单自动检测和填写
国内可用性：直接可用
API Key 要求：无需
费用情况：免费
安装命令：
clawhub install browsy
配置示例：
{
"openclaw-browsy": {
"preferBrowsy": true
}
}
与 browser 的区别： | 特性 | browsy | browser | |——|——–|———| | 速度 | 快 | 较慢 | | 内
存占用 | 低 | 高 | | JS 渲染 | 不支持 | 支持 | | 截图 | 不支持 | 支持 | | 复杂交互 | 不
支持 | 支持 |
使用建议：
● 简单网页抓取用 browsy
● 需要 JS 渲染或复杂交互用
browser
2.3 文件处理类 Skills
— 9 —

## 第 10 页

OpenClaw Skills 完全指南 Sharp科技
Skill 名称 功能简介 国内可用性 API Key 费用
nano-pdf PDF 自然语言编辑 直接可用 无需 免费
pdf-processor PDF 处理工具集 直接可用 无需 免费
excel-handler Excel 读写操作 直接可用 无需 免费
csv-data-summarizer CSV 数据分析 直接可用 无需 免费
image-gen 图像生成 需代理 图像模型 API 按模型计费
file-manager 文件系统管理 直接可用 无需 免费
nano-pdf
功能简介：通过自然语言指令编辑 PDF 文件
详细能力：
● 页面合并、拆分、裁剪
● 文字修改（有限支持） -
水印添加 - 密码保护
国内可用性：直接可用
API Key 要求：无需
费用情况：免费
安装命令：
clawhub install nano-pdf
使用示例：
用户：将这份 PDF 的第 1-3 页合并为新文件，添加水印"内部资料"
OpenClaw：执行 PDF 合并 → 添加水印 → 保存新文件
依赖要求：
# 安装系统依赖
sudo apt-get install poppler-utils qpdf
常见问题：
● 扫描版 PDF 需要 OCR 才能编辑文字
● 复杂排版 PDF
修改后可能格式错乱
excel-handler
功能简介：Excel 文件的读写和操作
详细能力：
● 读取、修改、创建 Excel 文件
● 单元格格式设置 -
公式计算 - 数据筛选和排序
国内可用性：直接可用
— 10 —

## 第 11 页

OpenClaw Skills 完全指南 Sharp科技
API Key 要求：无需
费用情况：免费
安装命令：
clawhub install excel-handler
使用示例：
用户：读取 sales.xlsx，计算每月销售额汇总
OpenClaw：读取 Excel → 按月份分组 → 计算汇总 → 返回结果
2.4 代码执行类 Skills
Skill 名称 功能简介 国内可用性 API Key 费用
code_execution Python 代码执行 直接可用 无需 免费
shell Shell 命令执行 直接可用 无需 免费
safe-exec 安全命令执行 直接可用 无需 免费
jupyter Jupyter Notebook 集成 直接可用 无需 免费
docker-skill Docker 容器管理 直接可用 无需 免费
code_execution（内置）
功能简介：执行 Python 代码进行数据处理和分析
详细能力：
● 执行 Python 代码块
● 数据分析（pandas、numpy） -
可视化（matplotlib、seaborn） - 文件读写
国内可用性：直接可用
API Key 要求：无需
费用情况：免费
配置示例：
{
"tools": {
"code_execution": {
"enabled": true,
"sandbox": true
}
}
}
安全建议：
● 生产环境建议启用沙盒模式
● 限制敏感目录访问 -
定期检查执行日志
— 11 —

## 第 12 页

OpenClaw Skills 完全指南 Sharp科技
shell（内置）
功能简介：执行系统 Shell 命令
详细能力：
● 执行任意 Shell 命令
● 脚本运行
● 系统管理 -
文件操作
国内可用性：直接可用
API Key 要求：无需
费用情况：免费
配置示例：
{
"tools": {
"shell": {
"enabled": true,
"dangerous": true
}
}
}
⚠️ 安全警告： - Shell 工具具有最高权限，可删除系统文件 - 建议仅在受信任的环境中启用 - 配合
Docker 沙箱使用更安全
2.5 数据库类 Skills
Skill 名称 功能简介 国内可用性 API Key 费用
db-query 数据库查询 直接可用 无需 免费
mysql-skill MySQL 操作 直接可用 无需 免费
postgres-skill PostgreSQL 操作 直接可用 无需 免费
mongo-skill MongoDB 操作 直接可用 无需 免费
redis-skill Redis 操作 直接可用 无需 免费
db-query
功能简介：统一的数据库查询接口，支持多种数据库
详细能力：
● 支持 PostgreSQL、MySQL、SQLite、MongoDB -
自然语言转 SQL - 查询结果可视化 - 自动 SSH 隧道管理
国内可用性：直接可用
API Key 要求：无需（需数据库连接信息）
费用情况：免费
安装命令：
— 12 —

## 第 13 页

OpenClaw Skills 完全指南 Sharp科技
clawhub install db-query
配置示例：
{
"skills": {
"database": {
"enabled": true,
"connections": {
"production": {
"type": "postgresql",
"host": "localhost",
"port": 5432,
"database": "myapp",
"user": "readonly_user",
"password": "${DB_PASSWORD}"
}
}
}
}
}
使用示例：
用户：查询最近一周订单总额并按日期分组
OpenClaw：生成 SQL → 执行查询 → 返回可视化结果
常见问题：
● 确保数据库用户权限最小化 -
生产环境建议使用只读账号 - 连接信息使用环境变量存储密码
2.6 AI 模型类 Skills
Skill 名称 功能简介 国内可用性 API Key 费用
openai-skill OpenAI API 调用 需代理 OpenAI API Key 按量付费
claude-skill Claude API 调用 需代理 Anthropic API 按量付费
Key
deepseek-skill DeepSeek 调用 直接可用 DeepSeek API 按量付费
Key
qwen-skill 通义千问调用 直接可用 阿里云 API Key 免费额度
kimi-skill Kimi 调用 直接可用 Moonshot API 免费额度
Key
glm-skill 智谱 GLM 调用 直接可用 Z.ai API Key 免费额度
ollama-skill 本地模型调用 直接可用 无需 免费
国产大模型配置指南
— 13 —

## 第 14 页

OpenClaw Skills 完全指南 Sharp科技
DeepSeek（深度求索）
# 配置 DeepSeek
openclaw config set 'models.providers.deepseek' --json '{
"baseUrl": "https://api.deepseek.com/v1",
"apiKey": "sk-你的DeepSeekKey",
"api": "openai-completions",
"models": [
{ "id": "deepseek-chat", "name": "DeepSeek V3" },
{ "id": "deepseek-reasoner", "name": "DeepSeek R1" }
]
}'
# 设置默认模型
openclaw models set deepseek/deepseek-chat
通义千问（阿里云）
# 配置通义千问
openclaw config set 'models.providers.qwen' --json '{
"baseUrl": "https://dashscope.aliyun.com/compatible-mode/v1",
"apiKey": "sk-你的阿里云Key",
"api": "openai-completions",
"models": [
{ "id": "qwen-plus", "name": "Qwen Plus" },
{ "id": "qwen-max", "name": "Qwen Max" }
]
}'
openclaw models set qwen/qwen-plus
Kimi（月之暗面）
# 配置 Kimi
openclaw config set 'models.providers.moonshot' --json '{
"baseUrl": "https://api.moonshot.cn/v1",
"apiKey": "sk-你的KimiKey",
"api": "openai-completions",
"models": [
{ "id": "kimi-k2.5", "name": "Kimi K2.5" }
]
}'
openclaw models set moonshot/kimi-k2.5
智谱 GLM
# 配置 GLM
openclaw config set 'models.providers.glm' --json '{
"baseUrl": "https://open.bigmodel.cn/api/paas/v4",
"apiKey": "你的GLMKey",
"api": "openai-completions",
"models": [
— 14 —

## 第 15 页

OpenClaw Skills 完全指南 Sharp科技
{ "id": "glm-4.7", "name": "GLM 4.7" },
{ "id": "glm-5", "name": "GLM 5" }
]
}'
openclaw models set glm/glm-4.7
Ollama（本地模型）
# 配置 Ollama
openclaw config set 'models.providers.ollama' --json '{
"baseUrl": "http://localhost:11434/v1",
"api": "openai-completions",
"models": [
{ "id": "llama3.2", "name": "Llama 3.2" },
{ "id": "qwen2.5", "name": "Qwen 2.5" }
]
}'
openclaw models set ollama/llama3.2
2.7 通讯类 Skills
Skill 名称 功能简介 国内可用性 API Key 费用
email 邮件发送 直接可用 SMTP 信息 免费
slack Slack 集成 需代理 Slack Bot Token 免费
telegram Telegram Bot 直接可用 Bot Token 免费
whatsapp WhatsApp 集成 需代理 WhatsApp Business 免费
feishu 飞书集成 直接可用 飞书 App ID 免费
wecom 企业微信集成 直接可用 企业微信凭证 免费
qqbot QQ 机器人 直接可用 QQ Bot Token 免费
himalaya 邮件全功能管理 直接可用 IMAP/SMTP 信息 免费
email
功能简介：通过 SMTP 发送邮件
详细能力：
● 发送纯文本/HTML 邮件
● 支持附件
● 支持多收件人 -
兼容 Gmail、Outlook、QQ 邮箱、163 邮箱等
国内可用性：直接可用
API Key 要求：SMTP 服务器信息
— 15 —

## 第 16 页

OpenClaw Skills 完全指南 Sharp科技
费用情况：免费
安装命令：
clawhub install email
配置示例：
{
"skills": {
"email": {
"smtp": {
"host": "smtp.qq.com",
"port": 587,
"user": "your_qq@qq.com",
"pass": "你的授权码"
}
}
}
}
常见邮箱 SMTP 设置：
邮箱 SMTP 服务器 端口 备注
QQ 邮箱 smtp.qq.com 587 需开启 SMTP 并获取授权码
163 邮箱 smtp.163.com 587 需开启客户端授权密码
Gmail smtp.gmail.com 587 需开启两步验证并创建应用密码
Outlook smtp.office365.com 587 使用微软账号密码
feishu（飞书）
功能简介：飞书机器人集成
详细能力：
● 接收/发送飞书消息
● 群聊集成
● 卡片消息
● 事件订阅
国内可用性：直接可用
API Key 要求：飞书 App ID 和 App Secret
费用情况：免费
安装命令：
clawhub install feishu-bot
配置步骤： 1. 访问 飞书开放平台 2. 创建企业自建应用 3. 获取 App ID 和 App Secret 4. 配置
事件订阅和权限
配置示例：
— 16 —

## 第 17 页

OpenClaw Skills 完全指南 Sharp科技
{
"channels": {
"feishu": {
"appId": "cli_xxxxxxxx",
"appSecret": "xxxxxxxx",
"encryptKey": "可选的加密密钥"
}
}
}
2.8 工具类 Skills
Skill 名称 功能简介 国内可用性 API Key 费用
weather 天气查询 直接可用 无需 免费
calculator 计算器 直接可用 无需 免费
translator 翻译工具 直接可用 无需 免费
qqbot-cron 定时提醒 直接可用 无需 免费
unit-converter 单位转换 直接可用 无需 免费
qr-generator 二维码生成 直接可用 无需 免费
password-gen 密码生成 直接可用 无需 免费
tushare A股行情 直接可用 Tushare Token 免费额度
weather
功能简介：全球城市天气查询
详细能力：
● 实时天气查询
● 3-7 天预报 -
支持风力、湿度、体感温度 - 全球城市覆盖
国内可用性：直接可用
API Key 要求：无需
费用情况：免费
安装命令：
# 通常已内置
clawhub install weather
使用示例：
用户：明天上海天气怎么样？
OpenClaw：🌤️ 上海明天：多云 10-20°C，湿度45%，东北风3级，适合外出
数据来源：wttr.in、Open-Meteo
— 17 —

## 第 18 页

OpenClaw Skills 完全指南 Sharp科技
tushare
功能简介：A股实时行情数据
详细能力：
● 实时股价查询
● 历史数据获取
● 持仓分析
● 涨跌提醒
国内可用性：直接可用
API Key 要求：Tushare Token（免费注册）
费用情况：
● 免费版：基础数据有限额
● 付费版：更多数据权限
安装命令：
clawhub install tushare
openclaw config set skills.tushare.token "你的TushareToken"
使用示例：
用户：查询贵州茅台（600519）实时行情
OpenClaw：📈 贵州茅台（600519）现价1895.00元，涨幅+1.23%，成交量5.3万手
第三部分：国内用户专属推荐
3.1 开箱即用 Skills 清单
以下 Skills 无需 API Key、无需代理、国内直连，推荐新手优先安装：
— 18 —

## 第 19 页

OpenClaw Skills 完全指南 Sharp科技
Skill 用途 安装命令
weather 天气查询 clawhub install weather
calculator 计算器 内置
browser 浏览器自动化 npx playwright install chromium
browsy 轻量网页浏览 clawhub install browsy
file-manager 文件管理 内置
code_execution Python 执行 内置
nano-pdf PDF 处理 clawhub install nano-pdf
excel-handler Excel 操作 clawhub install excel-handler
db-query 数据库查询 clawhub install db-query
qqbot-cron 定时提醒 clawhub install qqbot-cron
3.2 国产平替方案汇总
对于需要代理的 Skills，国内用户可使用以下替代方案：
原 Skill 替代方案 说明
web_search (Brave) Gemini 搜索 国内可访问
web_search (Brave) 自建 SearXNG 私有化部署
firecrawl 爬虫脚本 自建 Python 爬虫
OpenAI API 通义千问 免费额度充足
OpenAI API DeepSeek 性价比高
Claude API Kimi 长文本能力强
Claude API GLM-5 开源可本地部署
Slack 飞书 国内主流
WhatsApp 企业微信 企业场景
Gmail QQ邮箱/163 国内邮箱服务
3.3 最佳实践组合推荐
场景一：个人日常助手
推荐组合：
● weather + qqbot-cron + browser + file-manager
— 19 —

## 第 20 页

OpenClaw Skills 完全指南 Sharp科技
用途：
● 每日天气提醒
● 待办事项定时提醒
● 网页信息查询 -
文件整理
月费用：免费
场景二：开发者工作流
推荐组合：
● github + db-query + code_execution + browser +
docker-skill
用途：
● GitHub 仓库管理
● 数据库查询和监控 -
数据分析和脚本执行 - 网页调试 - 容器管理
月费用：约 5-30 元（国产模型 API）
场景三：内容创作者
推荐组合：
● summarize + browser + nano-pdf + email + telegram
用途：
● 文章摘要生成
● 素材搜集
● PDF 处理
● 邮件分发 -
社群运营
月费用：约 10-50 元
场景四：企业运维监控
推荐组合：
● db-query + healthcheck + docker-skill + feishu +
qqbot-cron
用途：
● 数据库监控
● 服务器健康检查
● 容器管理 -
告警通知（飞书） - 定时任务
月费用：约 20-100 元
第四部分：附录
4.1 常见报错及解决方案
— 20 —

## 第 21 页

OpenClaw Skills 完全指南 Sharp科技
安装阶段
问题 1：Skills 安装提示 “blocked”
原因：部分 Skills 依赖 brew 软件，无法一键安装
解决：
# 安装 Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.
sh)"
# 或使用国内镜像安装 Brew
/bin/zsh -c "$(curl -fsSL https://gitee.com/cunkai/HomebrewCN/raw/master/Homebrew.sh)"
问题 2：安装失败，提示”依赖缺失/下载超时”
原因：服务器网络问题，无法访问 Clawhub 平台
解决：
# 1. 检查网络连通性
ping clawhub.openclaw.cn
# 2. 切换国内镜像源
openclaw config set skills.registry https://registry.cn-hangzhou.aliyuncs.com/openclaw/skills
# 3. 安装缺失依赖
pip install --upgrade pip
pip install -r ~/.openclaw/workspace/skills/<skill-name>/requirements.txt
配置阶段
问题 3：TUI 卡在 “twiddling thumbs” / “noodling”
现象：长时间显示 twiddling thumbs... 无响应
原因：模型 context window 配置过小（OpenClaw 要求最少 16K）
解决：
# 修改配置文件
cat ~/.openclaw/openclaw.json
# 确保 contextWindow >= 16000
{
"models": {
"providers": {
"your-provider": {
"contextWindow": 200000,
"maxTokens": 128000
}
}
}
}
# 重启服务
openclaw gateway restart
— 21 —

## 第 22 页

OpenClaw Skills 完全指南 Sharp科技
问题 4：HTTP 401: Invalid Authentication
原因：API Key 配置错误或过期
解决： 1. 检查 API Key 是否正确复制（注意空格） 2. 确认 Key 未过期 3. 区分 Coding Plan 和
普通 API Key 4. 检查国内外版本 URL 是否正确
使用阶段
问题 5：web_fetch 失败
现象：日志显示 web_fetch failed: fetch failed
原因：网络波动、WSL2 DNS 问题、网站限制
解决：
# 测试网络
curl -I https://www.google.com
# 检查 DNS
cat /etc/resolv.conf
# 设置 Google DNS
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
# 或禁用 web_fetch（如不需要）
openclaw config set agents.main.skills.web_fetch.enabled false
openclaw gateway restart
问题 6：切换模型后返回 “no output”
原因：输出在其他环境中（Web、Telegram 等）
解决： 1. 检查其他已配置的环境 2. 使用 /new 开新窗口后再切换模型 3. 确认 fallbacks 中已
配置该模型
4.2 API Key 申请指南汇总表
服务商 申请地址 免费额度 备注
DeepSeek console.deepseek.com 5000万 Tokens 性价比高
通义千问 dashscope.aliyun.com 100万 Tokens 中文友好
Kimi platform.moonshot.cn 15元额度 长文本强
智谱 GLM open.bigmodel.cn 100万 Tokens 开源可本地部署
MiniMax platform.minimaxi.com 有免费额度 编程能力强
Brave Search brave.com/search/api 2000次/月 搜索 API
Firecrawl firecrawl.dev 500积分/月 网页抓取
Tushare tushare.pro 有限免费 A股数据
4.3 费用对比一览表
— 22 —

## 第 23 页

OpenClaw Skills 完全指南 Sharp科技
国产大模型费用对比（每百万 Tokens）
模型 输入费用 输出费用 备注
DeepSeek V3 ¥2 ¥8 性价比最高
DeepSeek R1 ¥4 ¥16 推理能力强
Qwen Plus ¥2 ¥6 均衡选择
Qwen Max ¥10 ¥30 最强效果
Kimi K2.5 ¥12 ¥24 长文本专家
GLM 4.7 ¥5 ¥10 开源可本地
MiniMax M2.1 ¥1 ¥4 编程首选
国际模型费用对比（每百万 Tokens，美元）
模型 输入费用 输出费用 备注
GPT-4o $2.50 $10.00 通用能力强
GPT-o3-mini $1.10 $4.40 推理优化
Claude 3.5 Sonnet $3.00 $15.00 代码能力强
Claude 3 Opus $15.00 $75.00 最强模型
Gemini 2.0 Flash $0.10 $0.40 最便宜
Gemini 2.0 Pro $3.50 $10.50 长上下文
使用成本估算
使用场景 月调用量 国产模型费用 国际模型费用
轻度使用（个人） 100万 Tokens ¥5-20 $1-5
中度使用（开发者） 1000万 Tokens ¥50-200 $10-50
重度使用（企业） 1亿 Tokens ¥500-2000 $100-500
参考资源
官方资源
● OpenClaw 官网：openclaw.ai
● 官方文档：docs.openclaw.ai
● GitHub 仓库：github.com/openclaw/openclaw
— 23 —

## 第 24 页

OpenClaw Skills 完全指南 Sharp科技
● ClawHub 市场：clawhub.openclaw.ai
社区资源
● Awesome OpenClaw Skills：github.com/VoltAgent/awesome-openclaw-skills
● 中文社区：clawcn.net
● Discord 社区：discord.gg/clawd
国内部署教程
● 腾讯云一键部署：腾讯云 OpenClaw 专题页
● 阿里云部署指南：阿里云开发者社区
更新日志
日期 版本 更新内容
2026-02-26 v1.0 初始版本，整理 50+ 常用 Skills
免责声明：本文档信息截止于 2026 年 2 月 26 日，Skills 生态快速发展，具体功能和费用请以官方
最新文档为准。使用第三方 Skills 时请注意安全审查。
本文档由 AI 助手整理生成，如有错误或遗漏，欢迎反馈指正。
— 24 —

