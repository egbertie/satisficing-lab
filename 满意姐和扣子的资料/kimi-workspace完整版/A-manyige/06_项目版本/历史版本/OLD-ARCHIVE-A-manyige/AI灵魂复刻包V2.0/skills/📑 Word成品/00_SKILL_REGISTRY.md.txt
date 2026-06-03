# 🛠️ Skill注册表与重建指南

> **（skill已完成更新 - 2026-03-12）**

---

## 📋 现有Skill清单

| Skill名称 | 状态 | 用途 | 重建优先级 |
|:---|:---:|:---|:---:|
| **task-coordinator** | ✅ 运行中 | 任务协调与调度 | P0 |
| **file-delivery** | ✅ 运行中 | 文件投递与交付 | P0 |
| **github-integration** | ✅ 已安装 | GitHub集成 | P1 |
| **notion-integration** | ✅ 已安装 | Notion集成 | P1 |
| **kimi-search** | ✅ 已配置 | Kimi搜索与深度研究 | P0 |

---

## 🔧 Skill重建方式

### 方式1：通过ClawHub安装（推荐）

```bash
# 安装已发布的Skill
openclaw skills install github-integration
openclaw skills install notion-integration
```

### 方式2：通过源代码重建（自定义Skill）

对于 `task-coordinator` 和 `file-delivery` 等自定义Skill，需要：

#### task-coordinator 重建步骤

1. **创建Skill目录**
```bash
mkdir -p ~/.openclaw/skills/task-coordinator
cd ~/.openclaw/skills/task-coordinator
```

2. **核心逻辑**（见下节）

3. **注册Skill**
在 `~/.openclaw/openclaw.json` 中添加：
```json
{
  "skills": {
    "task-coordinator": {
      "enabled": true,
      "path": "~/.openclaw/skills/task-coordinator"
    }
  }
}
```

---

## 📁 各Skill详细配置

### task-coordinator（任务协调）

**功能：**
- 每小时扫描任务状态
- 识别阻塞和延期风险
- 自动启动子代理处理并行任务

**重建指令：**
```bash
# 创建目录结构
mkdir -p skills/task-coordinator/{src,config,tests}

# 核心文件（简化版）
```

**配置参数：**
```json
{
  "scanInterval": 3600,
  "parallelThreshold": 2,
  "escalationTimeout": 86400,
  "riskScoreThreshold": 70
}
```

---

### file-delivery（文件交付）

**功能：**
- Markdown文件代码块交付
- 表格预览+CSV双重格式
- SVG图片路径指引

**重建指令：**
```bash
mkdir -p skills/file-delivery
cat > skills/file-delivery/config.json << 'EOF'
{
  "deliveryMode": "codeblock",
  "supportedFormats": ["md", "csv", "svg"],
  "workspacePath": "/root/.openclaw/workspace/A满意哥专属文件夹"
}
EOF
```

---

### kimi-search（Kimi搜索）

**功能：**
- 深度研究
- 网页提取
- 资讯采集

**重建方式：**
通过OpenClaw插件已配置：
```json
{
  "plugins": {
    "kimi-search": {
      "enabled": true,
      "config": {
        "search": {
          "baseUrl": "https://api.kimi.com/coding/v1/search"
        },
        "fetch": {
          "baseUrl": "https://api.kimi.com/coding/v1/fetch"
        }
      }
    }
  }
}
```

**API调用方式：**
```python
# 深度研究
kimi_search(query="人工智能 硬科技", depth="deep")

# 网页提取
kimi_fetch(url="https://example.com")
```

---

## 🔑 API密钥配置

### 必需API Key清单

| 服务 | Key名称 | 获取方式 | 用途 |
|:---|:---|:---|:---|
| **Kimi** | `KIMI_API_KEY` | Kimi开放平台 | 核心AI能力 |
| **Kimi Plugin** | `KIMI_PLUGIN_API_KEY` | Kimi插件管理 | 插件调用 |
| **GitHub** | `GITHUB_TOKEN` | GitHub Settings | 代码托管 |
| **Notion** | `NOTION_TOKEN` | Notion Integration | 文档备份 |
| **飞书** | `FEISHU_APP_ID/SECRET` | 飞书开放平台 | 第二通道 |

### 密钥存储（加密）

所有密钥存储在：`~/.openclaw/.env`

```bash
# 加密存储
cat > ~/.openclaw/.env << 'EOF'
KIMI_API_KEY=sk-kimi-...
KIMI_PLUGIN_API_KEY=sk-kimi-...
GITHUB_TOKEN=ghp_...
NOTION_TOKEN=secret_...
FEISHU_APP_ID=cli_...
FEISHU_APP_SECRET=...
EOF

chmod 600 ~/.openclaw/.env
```

---

## ✅ 重建验证清单

每个Skill重建后，必须验证：

- [ ] **task-coordinator**
  - [ ] 每小时自动扫描任务
  - [ ] 正确识别阻塞任务
  - [ ] 成功启动子代理

- [ ] **file-delivery**
  - [ ] Markdown代码块交付正常
  - [ ] 表格双重格式正常
  - [ ] 文件入库到正确位置

- [ ] **kimi-search**
  - [ ] 搜索功能正常
  - [ ] 深度研究功能正常
  - [ ] 网页提取功能正常

- [ ] **github-integration**
  - [ ] 仓库同步正常
  - [ ] Issue/PR管理正常

- [ ] **notion-integration**
  - [ ] 页面读取正常
  - [ ] 数据库同步正常

---

*重建完成后，新AI即具备与满意妞相同的核心能力。*
