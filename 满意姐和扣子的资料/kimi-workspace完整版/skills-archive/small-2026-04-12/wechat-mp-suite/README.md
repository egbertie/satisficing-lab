# 📱 微信公众号工作台 (wechat-mp-suite)

> OpenClaw Skill — 微信公众号一站式工作台，集成搜索、爬虫、写作、洗稿、配图、发布六大功能

## ✨ 功能模块

| 模块 | 功能 | 说明 |
|------|------|------|
| 🔍 **搜索** | 关键词搜索公众号文章 | 基于搜狗微信搜索，支持抓取正文 |
| 📥 **爬虫** | 下载公众号文章为 Markdown+图片 | URL → Markdown + 本地图片 |
| ✍️ **写作** | 热点选题、文章撰写、风格适配 | 技术/故事/观点多风格支持 |
| 🔄 **洗稿** | AI去痕迹+原创改写 | 结构重组、语言改写、SEO优化 |
| 🎨 **配图** | 封面图设计、配图建议 | 根据文章类型推荐配图 |
| 📤 **发布** | 一键发布到公众号草稿箱 | 基于 wenyan-cli，支持主题和视频嵌入 |

## 🚀 快速开始

### 环境要求

- **Node.js** ≥ 18
- **Python 3**
- **Google Chrome**（下载模块需要）
- [OpenClaw](https://github.com/anthropics/openclaw) 运行环境

### 安装依赖

```bash
# 1. Node.js 依赖
npm install -g cheerio @wenyan-md/cli

# 2. 下载模块依赖
cd /root/skills/wechat-mp-suite/scripts/downloader && npm install

# 3. 爬虫模块依赖
cd /root/skills/wechat-mp-suite/scripts/spider
pip install -r requirements.txt
```

## 📖 使用方法

### 🔍 搜索文章

```bash
# 基础搜索
node scripts/search/search_wechat.js "关键词"

# 指定数量 + 抓取正文
node scripts/search/search_wechat.js "关键词" -n 5 -c

# 保存结果
node scripts/search/search_wechat.js "关键词" -n 20 -o result.json
```

### 📥 下载文章（爬虫）

```bash
# 基础用法
python3 scripts/spider/main.py https://mp.weixin.qq.com/s/xxxxx

# 指定输出目录
python3 scripts/spider/main.py https://mp.weixin.qq.com/s/xxxxx ./my-articles
```

**输出结构：**
```
output/
├── 文章标题.md
└── images/
    ├── img_001.jpg
    └── img_002.png
```

### ✍️ 写作

通过 OpenClaw 自然语言指令触发：
- "帮我写篇公众号文章"
- "写一篇技术干货文章"
- "用故事叙事风格写"

### 🔄 洗稿改写

通过 OpenClaw 自然语言指令触发：
- "帮我洗稿这篇文章"
- "改写成原创"
- "去掉 AI 味"

### 📤 发布到公众号

```bash
# 配置环境变量
export WECHAT_APP_ID=your_app_id
export WECHAT_APP_SECRET=your_app_secret

# 发布
node scripts/publisher/publish.js /path/to/article.md
wenyan publish -f article.md -t lapis -h solarized-light
```

> ⚠️ **重要：** IP 必须添加到微信公众号后台白名单！

## 📁 项目结构

```
wechat-mp-suite/
├── SKILL.md                        # OpenClaw Skill 定义
├── README.md                       # 本文件
├── references/
│   └── USAGE.md                    # 完整使用文档
└── scripts/
    ├── search/                     # 搜索模块
    ├── downloader/                 # 下载模块
    ├── spider/                     # 爬虫模块
    └── publisher/                  # 发布模块
```

## ⚠️ 注意事项

- 所有工具仅供**个人学习**使用，请遵守相关版权法规
- 搜索功能内置防封禁机制，请勿高频使用
- 微信公众号发布需确保内容合规

## 📄 License

MIT
