# 飞书对接百科指引 - Open Claw 版

> **文档版本**: 2026年5月实战版  
> **基于**: 满意扣子2026年5月实战经验编写  
> **目标读者**: 原生 Open Claw 系统（非 Coze 体系）的 AI Agent  
> **最后更新**: 2026-05-07

---

## 关键资源网址清单

| 资源名称 | 网址 |
|----------|------|
| 飞书开放平台 | https://open.feishu.cn |
| 飞书开发者后台（应用管理） | https://open.feishu.cn/app |
| 飞书CLI GitHub仓库 | https://github.com/larksuite/cli |
| 飞书CLI npm包 | https://www.npmjs.com/package/@larksuite/cli |
| 飞书CLI安装指南（官方文档） | https://open.feishu.cn/document/no_class/mcp-archive/feishu-cli-installation-guide.md |
| 飞书服务端API文档 | https://open.feishu.cn/document/server-docs |
| 飞书API Explorer（在线调试） | https://open.feishu.cn/document/server-docs/api-explorer |
| 飞书CLI许愿池 | https://bytedance.larkoffice.com/base/Ebxvb6usfakMENs2GHIcL5Ern2f |
| 飞书开发者社区 | https://open.feishu.cn/document/home |
| 飞书互助交流群 | 请在飞书开发者社区查找官方交流群二维码 |

---

## 目录

1. [飞书生态全景](#第一部分飞书生态全景)
2. [环境准备](#第二部分环境准备)
3. [权限体系详解](#第三部分权限体系详解)
4. [核心操作指南](#第四部分核心操作指南)
5. [高级场景](#第五部分高级场景)
6. [最佳实践和避坑指南](#第六部分最佳实践和避坑指南)
7. [快速参考](#第七部分快速参考)
8. [Skill与MCP工具生态](#第八部分skill与mcp工具生态)
9. [学习资源](#第九部分学习资源)

---

# 第一部分：飞书生态全景

> **📌 关键网址**
> - 飞书开放平台：https://open.feishu.cn
> - 服务端API文档：https://open.feishu.cn/document/server-docs
> - 飞书开发者社区：https://open.feishu.cn/document/home

## 1.1 飞书是什么

飞书（Lark）是字节跳动打造的一站式协作平台，类似于 Google Workspace、Microsoft 365，但更专注于团队协作场景。飞书整合了多种办公能力：

### 飞书核心模块

| 模块 | 中文名 | 说明 |
|------|--------|------|
| IM | 即时通讯 | 消息、群聊、表情互动 |
| Docs | 云文档 | 新版在线文档（类 Notion） |
| Drive | 云空间 | 文件管理、文件夹、权限 |
| Wiki | 知识库 | 结构化知识管理 |
| Bitable | 多维表格 | 类 Airtable 的数据库 |
| Sheets | 电子表格 | 在线表格（类 Google Sheets） |
| Calendar | 日历 | 日程、会议、忙闲查询 |
| Task | 任务 | 待办事项管理 |
| Mail | 邮箱 | 企业邮箱 |
| Contact | 通讯录 | 组织架构、人员管理 |
| Approval | 审批 | 工作流审批 |
| VC | 视频会议 | 会议录制、会议室 |
| Minutes | 妙记 | 会议录音转写 |
| Whiteboard | 白板 | 协作画板 |

## 1.2 飞书开放平台概述

飞书开放平台（open.feishu.cn）是飞书对外提供 API 能力的入口，允许第三方应用与飞书进行深度集成。

### 核心概念

```
┌─────────────────────────────────────────────────────────────┐
│                    飞书开放平台                               │
├─────────────────────────────────────────────────────────────┤
│  开发者后台（open.feishu.cn）                                │
│  ├── 创建应用（App）                                        │
│  ├── 配置权限（Scopes）                                     │
│  ├── 配置事件订阅（Webhooks）                               │
│  └── 管理应用版本和发布                                     │
├─────────────────────────────────────────────────────────────┤
│  开放 API（Open API）                                       │
│  ├── REST API（同步调用）                                   │
│  ├── WebSocket（长连接，事件推送）                          │
│  └── Webhook（HTTP POST，事件推送）                         │
├─────────────────────────────────────────────────────────────┤
│  认证体系                                                   │
│  ├── tenant_access_token（应用身份）                        │
│  ├── user_access_token（用户身份）                         │
│  └── OAuth 2.0（用户授权）                                 │
└─────────────────────────────────────────────────────────────┘
```

## 1.3 飞书 CLI 是什么

飞书 CLI（`lark-cli`）是飞书官方提供的命令行工具，为 AI Agent 场景优化，提供：

### CLI vs 原生 API 对比

| 维度 | lark-cli | 原生 REST API |
|------|----------|---------------|
| 认证 | 自动管理 token | 需手动处理 |
| 调用方式 | 命令行 | HTTP 请求 |
| 错误处理 | 统一格式 | 需自行处理 |
| 事件订阅 | 支持 WebSocket | Webhook |
| 学习成本 | 低 | 高 |

### CLI 的三层命令结构

```
┌─────────────────────────────────────────────────────────────┐
│  第一层：快捷命令（Shortcuts）                               │
│  lark-cli <module> +<verb>                                │
│  例：lark-cli docs +create                                  │
│  特点：智能默认值，一行搞定常见操作                          │
├─────────────────────────────────────────────────────────────┤
│  第二层：API 命令（API Commands）                           │
│  lark-cli <module> <resource> <method>                    │
│  例：lark-cli docs documents create                         │
│  特点：精确控制参数                                        │
├─────────────────────────────────────────────────────────────┤
│  第三层：通用 API 调用（Generic API）                       │
│  lark-cli api <METHOD> <PATH>                              │
│  例：lark-cli api POST /open-apis/docx/v1/documents       │
│  特点：覆盖所有飞书 API                                    │
└─────────────────────────────────────────────────────────────┘
```

## 1.4 飞书 API 体系概述

### REST API

标准 HTTP API，支持所有飞书能力。

```bash
# 请求格式
curl -X POST "https://open.feishu.cn/open-apis/{api_path}" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{json_body}'
```

### WebSocket（长连接）

适用于 AI Agent 实时接收事件，无需公网地址。

```bash
# CLI 方式订阅事件
lark-cli event +subscribe
```

### Webhook（HTTP 回调）

传统模式，需要公网可访问的服务器地址。

```bash
# 配置在开发者后台
# 飞书会在事件发生时 POST 到你的服务器
```

### 三种事件接收方式对比

| 方式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| WebSocket (CLI) | 无需公网地址、免签权 | 需要运行 CLI | AI Agent 场景 |
| Webhook | 成熟稳定 | 需要公网地址 | 传统服务器 |
| SDK | 封装完善 | 依赖 SDK | 有服务器的 Node.js 应用 |

## 1.5 飞书应用类型

### 自建应用 vs 商店应用

| 类型 | 说明 | 审核要求 |
|------|------|----------|
| 自建应用 | 企业内部使用 | 企业管理员审核 |
| 商店应用 | 上架飞书应用市场 | 飞书官方审核 + 企业管理员审核 |

### 应用可见范围

| 可见范围 | 说明 |
|----------|------|
| 全部成员 | 所有企业员工可用 |
| 部分成员 | 仅指定成员可用 |
| 部分部门 | 仅指定部门可用 |

## 1.6 Bot 身份 vs User 身份

### 身份类型详解

```
┌─────────────────────────────────────────────────────────────┐
│  Bot 身份（tenant_access_token）                            │
├─────────────────────────────────────────────────────────────┤
│  • 以"应用"身份操作                                        │
│  • 创建的资源属于应用                                       │
│  • 无法访问用户的私人资源                                   │
│  • 无需用户授权，即开即用                                   │
│  • 适合：自动化流程、消息推送、数据查询                      │
├─────────────────────────────────────────────────────────────┤
│  User 身份（user_access_token）                             │
├─────────────────────────────────────────────────────────────┤
│  • 以"用户"身份操作                                        │
│  • 创建的资源属于用户                                       │
│  • 可访问用户的全部资源                                     │
│  • 需要用户授权 OAuth                                      │
│  • 适合：代表用户操作、访问个人资源                         │
└─────────────────────────────────────────────────────────────┘
```

### CLI 中切换身份

```bash
# 使用 Bot 身份（默认）
lark-cli im +messages-send --chat-id "oc_xxx" --text "Hello" --as bot

# 使用 User 身份
lark-cli im +messages-send --chat-id "oc_xxx" --text "Hello" --as user

# auto 模式（CLI 自动选择）
lark-cli im +messages-send --chat-id "oc_xxx" --text "Hello" --as auto
```

### 身份选择指南

| 场景 | 推荐身份 | 说明 |
|------|----------|------|
| 发送通知消息 | Bot | Bot 身份即可 |
| 读取用户日历 | User | 需要用户授权 |
| 创建云文档 | User | 文档归属用户 |
| 查询群消息 | Bot 或 User | 取决于群归属 |
| 发送邮件 | User | 邮箱是用户个人资源 |

---

# 第二部分：环境准备

> **📌 关键网址**
> - 飞书CLI GitHub仓库：https://github.com/larksuite/cli
> - 飞书CLI npm包：https://www.npmjs.com/package/@larksuite/cli
> - 飞书CLI安装指南：https://open.feishu.cn/document/no_class/mcp-archive/feishu-cli-installation-guide.md
> - 飞书开发者后台（应用管理）：https://open.feishu.cn/app
> - 飞书API Explorer：https://open.feishu.cn/document/server-docs/api-explorer

## 2.1 Node.js 环境安装

### 检查是否已安装

```bash
# 检查 Node.js 版本
node --version
# 期望输出：v18.x.x 或更高

# 检查 npm 版本
npm --version
# 期望输出：8.x.x 或更高
```

### 如果未安装（Linux/macOS）

```bash
# 使用 nvm 安装（推荐）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc

# 安装 Node.js 18
nvm install 18
nvm use 18

# 验证安装
node --version  # v18.x.x
npm --version   # 8.x.x
```

### 如果未安装（Windows）

从 [Node.js 官网](https://nodejs.org/) 下载并安装 LTS 版本。

## 2.2 飞书 CLI 安装

### 安装命令

```bash
# 全局安装（推荐）
npm install -g lark-cli

# 验证安装成功
lark-cli --version
# 期望输出类似：@larksuite/cli/x.x.x linux-x64 node-v18.x.x

# 查看帮助
lark-cli --help

# 查看所有可用模块
lark-cli --help

# 查看特定模块帮助
lark-cli im --help
lark-cli docs --help
lark-cli calendar --help
lark-cli base --help
```

### 从 GitHub 安装（开发版）

```bash
# 克隆仓库
git clone https://github.com/larksuite/cli.git

# 进入目录
cd cli

# 从源码安装
npm install
npm link

# 验证
lark-cli --version
```

### 白板CLI（用于绘制图表）

```bash
# 白板功能需要单独安装
npm install -g @larksuite/whiteboard-cli@^0.1.0

# 验证安装
npx -y @larksuite/whiteboard-cli@^0.1.0 --version
```

### 常用子命令

```bash
# 查看所有可用模块
lark-cli --help

# 查看特定模块帮助
lark-cli im --help
lark-cli docs --help
lark-cli calendar --help
```

## 2.3 飞书开放平台注册和创建应用

### 步骤 1：注册开发者账号

1. 访问 [飞书开放平台](https://open.feishu.cn)
2. 使用企业飞书账号登录
3. 进入「开发者后台」

### 步骤 2：创建应用

1. 点击「创建应用」
2. 选择「自建应用」
3. 填写应用信息：
   - 应用名称
   - 应用描述
   - 应用图标（可选）
4. 点击「确认创建」

### 步骤 3：获取凭证

在应用详情页获取：

```bash
# App ID（应用 ID）
cli_a1b2c3d4e5f6g7h8

# App Secret（应用密钥）
# 点击"获取 App Secret"按钮查看
```

⚠️ **重要**：
- App Secret 等同于密码，**严禁泄露**
- 建议将凭证存储在环境变量中

## 2.4 配置飞书 CLI

### 配置文件位置

```
~/.lark-cli/
├── config.json          # 主配置文件
├── credentials/         # 凭证存储
└── cache/               # 缓存
```

### 初始化配置

```bash
# 首次使用需要初始化
lark-cli config init

# 按提示输入 App ID 和 App Secret
```

### 使用脚本绑定凭证（推荐）

如果环境变量已配置凭证：

```bash
# 使用 Python 脚本绑定
python lark-shared/scripts/bind_credentials.py
```

### 验证配置

```bash
# 查看当前配置状态
lark-cli auth status

# 期望输出示例
{
  "status": "OK",
  "app_id": "cli_a1b2c3d4e5f6g7h8",
  "app_name": "My Feishu App",
  "user_auth": {
    "status": "authorized"
  },
  "bot_auth": {
    "status": "authorized"
  }
}
```

## 2.5 用户授权流程

### OAuth 设备码模式

适用于 CLI 场景，无需浏览器重定向：

```
┌─────────────────────────────────────────────────────────────┐
│  授权流程                                                   │
├─────────────────────────────────────────────────────────────┤
│  1. Agent 生成授权链接                                       │
│     lark-cli auth login --no-wait --domain all            │
│                                                              │
│  2. 用户在浏览器打开链接完成授权                              │
│     https://accounts.feishu.cn/oauth/v1/device/verify...   │
│                                                              │
│  3. 用户告知授权完成                                         │
│                                                              │
│  4. Agent 确认授权并获取 token                               │
│     lark-cli auth login --device-code                       │
└─────────────────────────────────────────────────────────────┘
```

### 生成授权链接

```bash
# 推荐：一次性授权所有权限
lark-cli auth login --no-wait --domain all

# 按业务域授权
lark-cli auth login --no-wait --domain calendar,im,docs

# 精确指定 scope
lark-cli auth login --no-wait --scope "calendar:calendar:read im:message:send"
```

### 业务域映射表

| domain 参数 | 业务范围 |
|------------|----------|
| `calendar` | 日历日程 |
| `im` | 即时通讯 |
| `doc` | 云文档 |
| `base` | 多维表格 |
| `sheets` | 电子表格 |
| `task` | 任务待办 |
| `mail` | 邮箱 |
| `contact` | 通讯录 |
| `drive` | 云空间 |
| `wiki` | 知识库 |
| `approval` | 审批 |
| `vc` | 视频会议 |
| `minutes` | 妙记 |
| `whiteboard` | 白板 |
| `all` | 所有业务域 |

### 确认授权

```bash
# 用户完成授权后执行
lark-cli auth login --device-code

# 期望输出
Device authorization successful!
```

## 2.6 授权域和权限范围详解

### 授权域（Domain）

按业务模块批量授权，CLI 会自动选择最优的 scope 组合。

### 权限范围（Scope）

精确控制每个 API 的访问权限。

### Scope 命名规范

```
{module}:{resource}:{action}

示例：
├── im:message:send        # 即时通讯-消息-发送
├── calendar:event:create  # 日历-日程-创建
├── docs:doc:readonly      # 文档-文档-只读
└── drive:file:write      # 云空间-文件-写入
```

### 常见 scope 速查

| Scope | 说明 |
|-------|------|
| `im:message:send` | 发送消息 |
| `im:chat:readonly` | 读取群聊 |
| `calendar:calendar:read` | 读取日历 |
| `calendar:calendar.event:create` | 创建日程 |
| `docs:doc:readonly` | 只读文档 |
| `docs:doc:write` | 读写文档 |
| `drive:drive:read` | 读取云空间 |
| `drive:file:write` | 写入文件 |
| `base:app:readonly` | 读取多维表格 |
| `base:record:write` | 写入记录 |
| `sheets:spreadsheet:read` | 读取表格 |
| `mail:mail:readonly` | 读取邮件 |
| `mail:mail:write` | 发送邮件 |

## 2.7 常见授权问题和解决方案

### 问题 1：No user logged in

```
错误信息：
{
  "note": "No user logged in. Only bot identity is available."
}
```

**解决方案**：
```bash
# 生成授权链接
lark-cli auth login --no-wait --domain all

# 等待用户授权后
lark-cli auth login --device-code
```

### 问题 2：Permission denied

```
错误信息：
{
  "code": 99991663,
  "msg": "permission denied"
}
```

**解决方案**：
1. 确认已在开发者后台开通对应权限
2. 如果是 User 身份，确认用户已授权对应 scope
3. 如果是 Bot 身份，确认应用已发布且权限已审核通过

### 问题 3：Token expired

```
错误信息：
{
  "code": 99991664,
  "msg": "access token expired"
}
```

**解决方案**：
```bash
# 重新获取 token
lark-cli auth refresh

# 或重新授权
lark-cli auth login --device-code
```

### 问题 4：App ID/Secret 无效

```
错误信息：
{
  "code": 99991681,
  "msg": "app_id or app_secret is invalid"
}
```

**解决方案**：
1. 检查 App ID 和 App Secret 是否正确
2. 确认应用未被禁用
3. 在开发者后台重新获取凭证

---

# 第三部分：权限体系详解

## 3.1 飞书权限模型

### 两层权限体系

```
┌─────────────────────────────────────────────────────────────┐
│                    应用权限（App Scopes）                    │
├─────────────────────────────────────────────────────────────┤
│  • 在开发者后台申请                                         │
│  • 需要管理员审核（部分权限）                               │
│  • 决定应用能调用哪些 API                                   │
├─────────────────────────────────────────────────────────────┤
│                    用户授权（User Consent）                  │
├─────────────────────────────────────────────────────────────┤
│  • 用户主动授权                                             │
│  • 决定应用能访问用户的哪些数据                             │
│  • 通过 OAuth 流程完成                                      │
└─────────────────────────────────────────────────────────────┘
```

### 权限生效条件

```
Bot 身份：
  应用权限开通 → 应用发布 → 权限生效

User 身份：
  应用权限开通 → 用户授权 → 权限生效
```

## 3.2 各业务域权限列表

### 即时通讯（IM）

| 权限 | Scope | 类型 | 说明 |
|------|-------|------|------|
| 获取群信息 | `im:chat:read` | 应用 | 读取群详情 |
| 创建群 | `im:chat:create` | 应用 | 创建群聊 |
| 更新群 | `im:chat:update` | 应用 | 修改群信息 |
| 获取群成员 | `im:chat.members:read` | 应用 | 读取群成员 |
| 添加群成员 | `im:chat.members:write` | 应用 | 添加/移除成员 |
| 发送消息 | `im:message` | 应用 | 发送消息 |
| 接收消息 | `im:message:receive` | 应用 | 接收消息事件 |
| 撤回消息 | `im:message:recall` | 应用 | 撤回消息 |
| 表情回复 | `im:message.reactions:write` | 应用 | 添加表情 |

### 日历（Calendar）

| 权限 | Scope | 类型 | 说明 |
|------|-------|------|------|
| 读取日历 | `calendar:calendar:read` | 用户 | 读取日历 |
| 读写日历 | `calendar:calendar:write` | 用户 | 管理日历 |
| 读取日程 | `calendar:event:read` | 用户 | 读取日程 |
| 创建日程 | `calendar:event:create` | 用户 | 创建日程 |
| 更新日程 | `calendar:event:update` | 用户 | 修改日程 |
| 删除日程 | `calendar:event:delete` | 用户 | 删除日程 |
| 忙闲查询 | `calendar:free_busy:read` | 用户 | 查询忙闲 |

### 云文档（Docs）

| 权限 | Scope | 类型 | 说明 |
|------|-------|------|------|
| 读取文档 | `docs:doc:readonly` | 用户 | 只读文档 |
| 读写文档 | `docs:doc:write` | 用户 | 编辑文档 |
| 搜索文档 | `docs:search:read` | 用户 | 搜索文档 |
| 创建文档 | `docs:doc:create` | 用户 | 创建文档 |

### 多维表格（Bitable）

| 权限 | Scope | 类型 | 说明 |
|------|-------|------|------|
| 读取多维表格 | `base:app:readonly` | 用户 | 读取应用 |
| 读写多维表格 | `base:app:write` | 用户 | 编辑应用 |
| 读取数据表 | `base:table:readonly` | 用户 | 读取数据表 |
| 读写数据表 | `base:table:write` | 用户 | 编辑数据表 |
| 读取记录 | `base:record:readonly` | 用户 | 读取记录 |
| 写入记录 | `base:record:write` | 用户 | 写入记录 |

### 电子表格（Sheets）

| 权限 | Scope | 类型 | 说明 |
|------|-------|------|------|
| 读取表格 | `sheets:spreadsheet:read` | 用户 | 读取表格 |
| 写入表格 | `sheets:spreadsheet:write` | 用户 | 编辑表格 |
| 读取工作表 | `sheets:sheet:read` | 用户 | 读取工作表 |
| 写入工作表 | `sheets:sheet:write` | 用户 | 写入工作表 |

### 任务（Task）

| 权限 | Scope | 类型 | 说明 |
|------|-------|------|------|
| 读取任务 | `task:task:read` | 用户 | 读取任务 |
| 读写任务 | `task:task:write` | 用户 | 管理任务 |
| 读取清单 | `task:tasklist:read` | 用户 | 读取清单 |
| 读写清单 | `task:tasklist:write` | 用户 | 管理清单 |

### 邮箱（Mail）

| 权限 | Scope | 类型 | 说明 |
|------|-------|------|------|
| 读取邮件 | `mail:mail:readonly` | 用户 | 读取邮件 |
| 发送邮件 | `mail:mail:write` | 用户 | 发送邮件 |
| 管理草稿 | `mail:draft:write` | 用户 | 管理草稿 |

### 通讯录（Contact）

| 权限 | Scope | 类型 | 说明 |
|------|-------|------|------|
| 读取通讯录 | `contact:book:readonly` | 应用 | 读取通讯录 |
| 读取用户 | `contact:user.employee_id:read` | 应用 | 读取用户 |
| 读取部门 | `contact:department:read` | 应用 | 读取部门 |

### 云空间（Drive）

| 权限 | Scope | 类型 | 说明 |
|------|-------|------|------|
| 读取云空间 | `drive:drive:read` | 用户 | 读取云空间 |
| 写入云空间 | `drive:drive:write` | 用户 | 管理云空间 |
| 上传文件 | `drive:file:write` | 用户 | 上传文件 |
| 下载文件 | `drive:file:read` | 用户 | 下载文件 |
| 管理权限 | `drive:permission:manage` | 用户 | 管理权限 |

### 知识库（Wiki）

| 权限 | Scope | 类型 | 说明 |
|------|-------|------|------|
| 读取知识库 | `wiki:wiki:readonly` | 用户 | 读取知识库 |
| 读写知识库 | `wiki:wiki:write` | 用户 | 编辑知识库 |

### 审批（Approval）

| 权限 | Scope | 类型 | 说明 |
|------|-------|------|------|
| 读取审批 | `approval:approval:read` | 用户 | 读取审批 |
| 处理审批 | `approval:approval:write` | 用户 | 处理审批 |

### 视频会议（VC）

| 权限 | Scope | 类型 | 说明 |
|------|-------|------|------|
| 读取会议 | `vc:meeting:read` | 用户 | 读取会议 |
| 管理会议 | `vc:meeting:write` | 用户 | 管理会议 |
| 录制权限 | `vc:recording:read` | 用户 | 读取录制 |

### 妙记（Minutes）

| 权限 | Scope | 类型 | 说明 |
|------|-------|------|------|
| 读取妙记 | `minutes:minutes:readonly` | 用户 | 读取妙记 |
| 下载媒体 | `minutes:media:export` | 用户 | 下载音视频 |

### 白板（Whiteboard）

| 权限 | Scope | 类型 | 说明 |
|------|-------|------|------|
| 读取白板 | `whiteboard:document:read` | 用户 | 读取白板 |
| 写入白板 | `whiteboard:document:write` | 用户 | 写入白板 |

## 3.3 在开放平台开通权限

### 步骤 1：进入权限管理

1. 登录 [开发者后台](https://open.feishu.cn)
2. 选择目标应用
3. 点击「权限管理」

### 步骤 2：搜索并开通权限

1. 在权限列表中搜索关键词
2. 点击「开通」按钮
3. 确认权限范围

### 步骤 3：提交审核

对于需要审核的权限：
1. 创建应用版本
2. 提交审核
3. 等待管理员批准

## 3.4 权限的审核和发布流程

### 自建应用审核流程

```
申请权限 → 创建版本 → 提交审核 → 管理员审批 → 发布生效
```

### 免审权限

以下权限无需审核，开通后立即生效：
- `im:message:send`
- `im:chat:readonly`
- `calendar:event:read`
- `drive:file:read`

### 需审核权限

涉及敏感数据的权限需要审核：
- `contact:user:readonly`
- `mail:mail:write`
- `approval:approval:write`

## 3.5 Bot 身份 vs User 身份的权限差异

### Bot 身份可用权限

| 场景 | Bot 可用 | 说明 |
|------|----------|------|
| 发送消息 | ✅ | `im:message` |
| 创建群 | ✅ | `im:chat:create` |
| 读取消息 | ✅ | 需要在群中或 Bot 发送 |
| 管理 Bot 所在群 | ✅ | Bot 需是群成员 |
| 上传文件 | ✅ | `drive:file:write` |

### 仅 User 身份可用权限

| 场景 | User 必须 | 说明 |
|------|-----------|------|
| 读取用户日历 | ✅ | 日历是个人资源 |
| 访问用户邮箱 | ✅ | 邮箱是个人资源 |
| 读取个人文档 | ✅ | 非 Bot 创建的文档 |
| 发送邮件 | ✅ | 邮件有发件人身份 |

### 关键区别总结

```
┌─────────────────────────────────────────────────────────────┐
│  Bot 身份能做的事：                                         │
│  • 发送消息（以 Bot 名义）                                  │
│  • 管理 Bot 加入的群聊                                      │
│  • 读取/写入 Bot 创建的资源                                 │
│  • 调用不需要用户授权的 API                                 │
├─────────────────────────────────────────────────────────────┤
│  User 身份能做的事：                                         │
│  • 代表用户发送消息                                         │
│  • 访问用户的所有飞书资源                                   │
│  • 读取用户日历、邮箱、个人文档                             │
│  • 执行需要用户身份确认的操作                               │
└─────────────────────────────────────────────────────────────┘
```

---

# 第四部分：核心操作指南

## 4.1 即时通讯（IM）

### 发送消息

#### 发送文本消息

```bash
# 使用 Shortcut（推荐）
lark-cli im +messages-send \
  --chat-id "oc_xxxxx" \
  --text "你好，这是一条测试消息"
```

**参数说明**：
- `--chat-id`：群 ID，格式为 `oc_xxxxx`
- `--text`：消息文本内容

**返回值示例**：
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "message_id": "om_xxxxx",
    "msg_time": 1707123456789
  }
}
```

#### 发送富文本消息

```bash
lark-cli im +messages-send \
  --chat-id "oc_xxxxx" \
  --msg-type "post" \
  --content '{
    "zh_cn": {
      "title": "重要通知",
      "content": [
        [{"tag": "text", "text": "这是一个"}],
        [{"tag": "text", "text": "加粗文本", "bold": true}],
        [{"tag": "text", "text": "\n链接："}],
        [{"tag": "a", "text": "点击这里", "href": "https://example.com"}]
      ]
    }
  }'
```

**富文本标签说明**：

| 标签 | 说明 | 常用属性 |
|------|------|----------|
| `text` | 文本 | `text`, `bold`, `italic` |
| `a` | 超链接 | `text`, `href` |
| `at` | @人 | `user_id` 或 `user_name` |
| `img` | 图片 | `width`, `height`, `image_key` |
| `emotion` | 表情 | `emoji_id` |

#### 发送图片消息

```bash
# 先上传图片获取 image_key
lark-cli im images create \
  --image-type "message" \
  --file "@/path/to/image.png"

# 返回 image_key
# "img_v2_xxxxx"

# 发送图片消息
lark-cli im +messages-send \
  --chat-id "oc_xxxxx" \
  --msg-type "image" \
  --content '{"image_key":"img_v2_xxxxx"}'
```

#### 发送消息卡片

```bash
lark-cli im +messages-send \
  --chat-id "oc_xxxxx" \
  --msg-type "interactive" \
  --content '{
    "config": {
      "wide_screen_mode": true
    },
    "elements": [
      {
        "tag": "markdown",
        "content": "**标题**\n\n这是卡片内容"
      },
      {
        "tag": "action",
        "actions": [
          {
            "tag": "button",
            "text": {"tag": "plain_text", "content": "确认"},
            "type": "primary"
          }
        ]
      }
    ]
  }'
```

### 回复消息

```bash
# 回复指定消息（支持帖子模式）
lark-cli im +messages-reply \
  --message-id "om_xxxxx" \
  --text "这是回复内容"
```

**参数说明**：
- `--message-id`：被回复的消息 ID
- `--text`：回复内容

### 搜索消息

```bash
# 搜索消息（需要 User 身份）
lark-cli im +messages-search \
  --query "关键词" \
  --as user

# 带时间范围搜索
lark-cli im +messages-search \
  --query "会议纪要" \
  --start-time "2026-01-01T00:00:00+08:00" \
  --end-time "2026-05-01T00:00:00+08:00"
```

### 群聊管理

#### 创建群

```bash
# 创建公开群
lark-cli im +chat-create \
  --name "测试群" \
  --description "这是一个测试群" \
  --chat-mode "public"

# 创建私密群并添加成员
lark-cli im +chat-create \
  --name "项目群" \
  --user-ids "ou_xxxxx,ou_yyyyy" \
  --chat-mode "private"
```

#### 获取群信息

```bash
# 获取群详情
lark-cli im chat get \
  --params '{"chat_id":"oc_xxxxx"}'
```

#### 添加群成员

```bash
# 添加单个成员
lark-cli im chat.members create \
  --params '{"chat_id":"oc_xxxxx"}' \
  --data '{"id_list":["ou_xxxxx"]}'

# 批量添加成员
lark-cli im chat.members create \
  --params '{"chat_id":"oc_xxxxx"}' \
  --data '{"id_list":["ou_xxxxx","ou_yyyyy","ou_zzzzz"]}'
```

#### 移除群成员

```bash
lark-cli im chat.members delete \
  --params '{"chat_id":"oc_xxxxx"}' \
  --data '{"id_list":["ou_xxxxx"]}'
```

#### 获取群成员列表

```bash
# 获取所有成员
lark-cli im +chat-members-list \
  --chat-id "oc_xxxxx"

# 包含成员详细信息
lark-cli im chat.members get \
  --params '{"chat_id":"oc_xxxxx"}'
```

### 消息互动

#### 添加表情回应

```bash
# 添加表情
lark-cli im reactions create \
  --params '{"message_id":"om_xxxxx"}' \
  --data '{"reaction_type":{"emoji_type":"OK"}}'
```

#### 获取消息表情

```bash
lark-cli im reactions list \
  --params '{"message_id":"om_xxxxx"}'
```

### 接收消息（Webhook 事件订阅）

#### 使用 CLI 长连接订阅

```bash
# 订阅所有消息事件
lark-cli event +subscribe

# 输出格式为 NDJSON
# 每条消息事件格式：
{
  "schema": "2.0",
  "header": {
    "event_id": "xxx",
    "event_type": "im.message.receive_v1",
    "create_time": "1707123456789",
    "token": "xxx",
    "app_id": "cli_xxx",
    "tenant_key": "xxx"
  },
  "event": {
    "sender": {
      "sender_id": {"open_id": "ou_xxx"},
      "sender_type": "user"
    },
    "message": {
      "message_id": "om_xxx",
      "chat_id": "oc_xxx",
      "msg_type": "text",
      "content": "{\"text\":\"Hello\"}"
    }
  }
}
```

---

## 4.2 云文档（Docs）

### 创建文档

```bash
# 从 Markdown 创建
lark-cli docs +create \
  --title "我的文档" \
  --markdown "# 标题\n\n这是正文内容"
```

**参数说明**：
- `--title`：文档标题
- `--markdown`：Markdown 格式内容（可选）

**返回值示例**：
```json
{
  "code": 0,
  "data": {
    "document": {
      "document_id": "dox_xxxxx",
      "title": "我的文档"
    },
    "url": "https://xxx.feishu.cn/docx/dox_xxxxx"
  }
}
```

### 读取文档内容

```bash
# 读取文档（返回 Markdown 格式）
lark-cli docs +fetch \
  --doc "dox_xxxxx"

# 支持直接传入 URL
lark-cli docs +fetch \
  --url "https://xxx.feishu.cn/docx/dox_xxxxx"
```

### 更新文档

```bash
# 追加内容
lark-cli docs +update \
  --doc "dox_xxxxx" \
  --mode append \
  --markdown "## 新增章节\n\n这是新增的内容"

# 替换内容
lark-cli docs +update \
  --doc "dox_xxxxx" \
  --mode replace \
  --markdown "# 替换后的标题\n\n完全替换的内容"

# 插入内容到开头
lark-cli docs +update \
  --doc "dox_xxxxx" \
  --mode prepend \
  --markdown "# 开头新增\n\n插入到文档开头"
```

**mode 参数说明**：
- `append`：追加到文档末尾
- `prepend`：插入到文档开头
- `replace`：替换整个文档

### 搜索文档

```bash
# 搜索云空间文档
lark-cli docs +search \
  --query "项目报告"

# 限制返回数量
lark-cli docs +search \
  --query "会议" \
  --count 20
```

### 文档评论管理

```bash
# 添加全文评论
lark-cli drive +add-comment \
  --file-token "dox_xxxxx" \
  --content '[{"type":"text","text":"这是评论内容"}]'

# 添加局部评论（划词评论）
lark-cli drive +add-comment \
  --file-token "dox_xxxxx" \
  --content '[{"type":"text","text":"这是评论内容"}]' \
  --selection-with-ellipsis "选中的文本"

# 获取评论列表
lark-cli drive file.comments list \
  --params '{"file_token":"dox_xxxxx"}'
```

### Markdown 转飞书文档

飞书文档使用类似 Markdown 的块结构，但有以下差异：

| Markdown | 飞书块类型 |
|----------|-----------|
| `# Heading` | `heading1` |
| `## Heading` | `heading2` |
| `### Heading` | `heading3` |
| `**bold**` | `text` with bold |
| `*italic*` | `text` with italic |
| `[text](url)` | `text_link` |
| `` `code` `` | `code` |
| `---` | `horizontal_line` |
| `- item` | `bullet` |
| `1. item` | `ordered` |

### 飞书文档导出 Markdown

```bash
# 使用 docs +fetch 获取内容
lark-cli docs +fetch --doc "dox_xxxxx" > output.md

# 或使用导出功能
lark-cli drive +export \
  --file-token "dox_xxxxx" \
  --file-type "markdown"
```

---

## 4.3 云空间（Drive）

### 创建文件夹

```bash
# 在根目录创建
lark-cli drive files create_folder \
  --params '{"folder_token":"0"}' \
  --data '{"name":"新文件夹"}'

# 在指定文件夹创建
lark-cli drive files create_folder \
  --params '{"folder_token":"fld_xxxxx"}' \
  --data '{"name":"子文件夹"}'
```

**返回值示例**：
```json
{
  "code": 0,
  "data": {
    "folder": {
      "token": "fld_xxxxx",
      "name": "新文件夹"
    }
  }
}
```

### 上传文件

```bash
# 上传到根目录
lark-cli drive +upload \
  --file "/path/to/document.pdf" \
  --parent-token "0"

# 上传到指定文件夹
lark-cli drive +upload \
  --file "/path/to/image.png" \
  --parent-token "fld_xxxxx"

# 覆盖已有文件
lark-cli drive +upload \
  --file "/path/to/file.pdf" \
  --parent-token "fld_xxxxx" \
  --file-name "newname.pdf"
```

**参数说明**：
- `--file`：本地文件路径
- `--parent-token`：目标文件夹 token（`0` 表示根目录）
- `--file-name`：上传后的文件名（可选）

### 下载文件

```bash
# 下载到当前目录
lark-cli drive +download \
  --file-token "box_xxxxx" \
  --output "./downloaded.pdf"

# 下载到指定目录
lark-cli drive +download \
  --file-token "box_xxxxx" \
  --output "./downloads/file.pdf"
```

### 移动/复制文件

```bash
# 移动文件
lark-cli drive +move \
  --file-token "box_xxxxx" \
  --target-folder-token "fld_xxxxx"

# 复制文件
lark-cli drive files copy \
  --params '{"file_token":"box_xxxxx"}' \
  --data '{"name":"副本文件","type":"file","folder_token":"fld_xxxxx"}'
```

### 删除文件

```bash
# 删除文件（移动到回收站）
lark-cli drive files delete \
  --params '{"file_token":"box_xxxxx"}'

# ⚠️ 永久删除需要额外权限
lark-cli drive files delete \
  --params '{"file_token":"box_xxxxx","type":"file"}'
```

### 权限管理

#### 添加协作者

```bash
# 添加用户为编辑者
lark-cli drive permission.members create \
  --params '{"file_token":"dox_xxxxx","type":"docx"}' \
  --data '{
    "member_type": "openid",
    "member_id": "ou_xxxxx",
    "perm": "full_access"
  }'
```

**权限级别说明**：
- `view`：查看
- `edit`：编辑
- `full_access`：管理（包含编辑、分享、删除）

#### 移除协作者

```bash
lark-cli drive permission.members delete \
  --params '{"file_token":"dox_xxxxx","type":"docx","member_id":"ou_xxxxx","member_type":"openid"}'
```

### 文件导入导出

#### 导出文件

```bash
# 导出为 PDF
lark-cli drive +export \
  --file-token "dox_xxxxx" \
  --file-type "pdf"

# 导出为 Markdown
lark-cli drive +export \
  --file-token "dox_xxxxx" \
  --file-type "markdown"

# 导出为 DOCX
lark-cli drive +export \
  --file-token "dox_xxxxx" \
  --file-type "docx"
```

#### 导入文件

```bash
# 导入本地文件
lark-cli drive +import \
  --file "/path/to/document.docx" \
  --parent-token "0" \
  --type "docx"
```

**支持的导入类型**：
- `docx`：飞书文档
- `sheet`：飞书表格
- `bitable`：飞书多维表格

### 批量文件同步脚本

```bash
#!/bin/bash
# feishu_sync.sh - 飞书云空间批量同步脚本

# 配置
FEISHU_FOLDER="fld_xxxxx"  # 目标文件夹
LOCAL_DIR="./sync_folder"   # 本地文件夹
LOG_FILE="sync_log.txt"

# 同步函数
sync_to_feishu() {
  local local_file="$1"
  local feishu_folder="$2"
  
  # 获取文件名
  local filename=$(basename "$local_file")
  
  echo "[$(date)] 正在上传: $filename" >> "$LOG_FILE"
  
  # 上传文件
  lark-cli drive +upload \
    --file "$local_file" \
    --parent-token "$feishu_folder" \
    --file-name "$filename"
  
  if [ $? -eq 0 ]; then
    echo "[$(date)] 上传成功: $filename" >> "$LOG_FILE"
  else
    echo "[$(date)] 上传失败: $filename" >> "$LOG_FILE"
  fi
}

# 遍历本地文件夹
for file in "$LOCAL_DIR"/*; do
  if [ -f "$file" ]; then
    sync_to_feishu "$file" "$FEISHU_FOLDER"
  fi
done

echo "同步完成，详见 $LOG_FILE"
```

---

## 4.4 知识库（Wiki）

### 创建知识空间

```bash
# 创建知识空间
lark-cli wiki nodes create \
  --params '{"space_id":"space_xxxxx"}' \
  --data '{
    "obj_type": "wiki",
    "parent_node_token": "",
    "node_type": "origin",
    "origin": {
      "title": "新知识空间"
    }
  }'
```

### 创建节点

```bash
# 创建文档节点
lark-cli wiki nodes create \
  --params '{"space_id":"space_xxxxx"}' \
  --data '{
    "obj_type": "docx",
    "parent_node_token": "parent_xxxxx",
    "node_type": "origin",
    "origin": {
      "title": "新文档节点"
    }
  }'
```

**obj_type 选项**：
- `docx`：新版云文档
- `doc`：旧版云文档
- `sheet`：电子表格
- `bitable`：多维表格
- `file`：文件

### 节点层级管理

```bash
# 获取节点列表
lark-cli wiki nodes list \
  --params '{"space_id":"space_xxxxx","parent_node_token":"node_xxxxx"}'

# 移动节点
lark-cli wiki nodes move \
  --params '{"space_id":"space_xxxxx"}' \
  --data '{
    "node_token": "node_xxxxx",
    "parent_node_token": "new_parent_xxxxx"
  }'
```

### Wiki 链接解析

⚠️ **重要**：Wiki 链接中的 token 不能直接使用，必须先解析。

```bash
# 查询节点信息
lark-cli wiki spaces get_node \
  --params '{"token":"wikn_xxxxx"}'

# 返回结果
{
  "node": {
    "obj_type": "docx",           # 真实文档类型
    "obj_token": "dox_xxxxx",     # 真实文档 token
    "title": "文档标题",
    "node_type": "origin",
    "space_id": "space_xxxxx"
  }
}
```

**不同 obj_type 的处理**：

| obj_type | 说明 | 后续操作 |
|----------|------|----------|
| `docx` | 新版文档 | `docs +fetch`、`docs +update` |
| `doc` | 旧版文档 | `docs +fetch` |
| `sheet` | 电子表格 | `sheets +read`、`sheets +write` |
| `bitable` | 多维表格 | `base +table-list`、`base +record-list` |

---

## 4.5 多维表格（Bitable）

### 创建多维表格

```bash
# 创建多维表格
lark-cli base +base-create \
  --name "项目管理表"

# 在指定文件夹创建
lark-cli base +base-create \
  --name "团队任务表" \
  --folder-token "fld_xxxxx"
```

**返回值示例**：
```json
{
  "code": 0,
  "data": {
    "app": {
      "app_token": "bascnxxxxx",
      "name": "项目管理表",
      "url": "https://xxx.feishu.cn/base/bascnxxxxx"
    }
  }
}
```

⚠️ **重要**：创建后系统会自动生成一个默认数据表（Table1），请按照以下流程处理：

1. 创建自定义数据表
2. 在自定义表中创建字段、写入数据
3. 删除默认的 Table1

### 数据表管理

#### 创建数据表

```bash
# 在多维表格中创建数据表
lark-cli base +table-create \
  --base-token "bascnxxxxx" \
  --table-name "任务列表"
```

#### 删除数据表

```bash
# 删除数据表
lark-cli base +table-delete \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx" \
  --yes
```

### 字段管理

#### 创建字段

```bash
# 创建文本字段
lark-cli base +field-create \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx" \
  --field-name "任务名称" \
  --field-type "Text"

# 创建数字字段
lark-cli base +field-create \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx" \
  --field-name "优先级" \
  --field-type "Number" \
  --json '{"formatter":"0,0"}'

# 创建单选字段
lark-cli base +field-create \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx" \
  --field-name "状态" \
  --field-type "SingleSelect" \
  --json '{"options":[{"name":"待处理"},{"name":"进行中"},{"name":"已完成"}]}'
```

**字段类型说明**：

| 类型 | CLI 值 | 说明 |
|------|--------|------|
| 文本 | `Text` | 纯文本 |
| 数字 | `Number` | 数字，支持格式 |
| 单选 | `SingleSelect` | 单选下拉 |
| 多选 | `MultiSelect` | 多选标签 |
| 日期 | `Date` | 日期时间 |
| 人员 | `User` | 用户选择 |
| 复选框 | `Checkbox` | true/false |
| 公式 | `Formula` | 计算字段 |
| 查找引用 | `LookUp` | 跨表关联 |
| 自动编号 | `AutoNumber` | 流水号 |
| 创建时间 | `CreatedTime` | 自动填充 |
| 最后修改时间 | `LastModifiedTime` | 自动填充 |
| 创建人 | `CreatedBy` | 自动填充 |
| 修改人 | `LastModifiedBy` | 自动填充 |
| 附件 | `Attachment` | 文件上传 |

#### 读取字段列表

```bash
lark-cli base +field-list \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx"
```

### 记录操作

#### 写入记录

```bash
# 单条写入（Upsert 模式）
lark-cli base +record-upsert \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx" \
  --json '{
    "fields": {
      "任务名称": "完成项目报告",
      "优先级": 1,
      "状态": "待处理",
      "截止日期": 1707123456789
    }
  }'

# 批量写入（每批最多 500 条）
lark-cli base +record-upsert \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx" \
  --json '{
    "records": [
      {"fields": {"任务名称": "任务1", "优先级": 1}},
      {"fields": {"任务名称": "任务2", "优先级": 2}},
      {"fields": {"任务名称": "任务3", "优先级": 3}}
    ]
  }'
```

#### 读取记录

```bash
# 获取所有记录
lark-cli base +record-list \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx"

# 按视图筛选
lark-cli base +record-list \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx" \
  --view-id "viw_xxxxx"

# 带过滤条件
lark-cli base +view-set-filter \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx" \
  --view-id "viw_xxxxx" \
  --json '{
    "conjunction": "and",
    "conditions": [
      {"field_name": "状态", "operator": "is", "value": ["已完成"]}
    ]
  }'

# 然后获取过滤后的记录
lark-cli base +record-list \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx" \
  --view-id "viw_xxxxx"
```

#### 删除记录

```bash
# 删除单条记录
lark-cli base +record-delete \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx" \
  --record-id "rec_xxxxx"

# ⚠️ 删除时必须加 --yes
lark-cli base +record-delete \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx" \
  --record-id "rec_xxxxx" \
  --yes
```

### 视图管理

```bash
# 创建视图
lark-cli base +view-create \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx" \
  --view-name "我的视图" \
  --view-type "grid"

# 重命名视图
lark-cli base +view-rename \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx" \
  --view-id "viw_xxxxx" \
  --new-name "新视图名"
```

**视图类型**：
- `grid`：表格视图
- `kanban`：看板视图
- `gallery`：相册视图
- `gantt`：甘特图
- `mindnote`：思维导图

### 数据查询和聚合

```bash
# 聚合查询（推荐用于统计分析）
lark-cli base +data-query \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx" \
  --json '{
    "filter": {
      "conjunction": "and",
      "conditions": [
        {"field_name": "状态", "operator": "is", "value": ["已完成"]}
      ]
    },
    "aggregations": [
      {"field_name": "优先级", "agg_func": "COUNT"},
      {"field_name": "优先级", "agg_func": "SUM"}
    ],
    "group_by": ["状态"]
  }'
```

**聚合函数**：
- `COUNT`：计数
- `SUM`：求和
- `AVERAGE`：平均值
- `MAX`：最大值
- `MIN`：最小值
- `COUNTA`：非空计数

---

## 4.6 电子表格（Sheets）

### 创建表格

```bash
# 创建电子表格
lark-cli sheets +create \
  --title "销售数据表"

# 指定表头
lark-cli sheets +create \
  --title "员工信息表" \
  --header '["姓名","部门","职位","入职日期"]'
```

### 读写单元格

```bash
# 读取单元格
lark-cli sheets +read \
  --spreadsheet-token "shtcnxxxxx" \
  --range "Sheet1!A1:D10"

# 写入单元格
lark-cli sheets +write \
  --spreadsheet-token "shtcnxxxxx" \
  --range "Sheet1!A1" \
  --values '[["姓名","年龄","城市"]]'

# 多行写入
lark-cli sheets +write \
  --spreadsheet-token "shtcnxxxxx" \
  --range "Sheet1!A2" \
  --values '[["张三",25,"北京"],["李四",30,"上海"],["王五",28,"广州"]]'
```

### 批量追加数据

```bash
# 在表格末尾追加行
lark-cli sheets +append \
  --spreadsheet-token "shtcnxxxxx" \
  --range "Sheet1" \
  --values '[["赵六",35,"深圳"]]'
```

### 查找替换

```bash
# 在表格中查找
lark-cli sheets +find \
  --spreadsheet-token "shtcnxxxxx" \
  --sheet-id "0" \
  --value "关键词"

# ⚠️ 替换功能需要使用原生 API
lark-cli sheets spreadsheet.sheet.find \
  --params '{"spreadsheet_token":"shtcnxxxxx","sheet_id":"0"}' \
  --data '{"value":"旧文本","replace_value":"新文本"}'
```

### 导出下载

```bash
# 导出为 Excel
lark-cli sheets +export \
  --spreadsheet-token "shtcnxxxxx" \
  --file-type "xlsx"

# 下载导出的文件
lark-cli drive +export-download \
  --file-token "export_token_xxxxx" \
  --output "./sales_data.xlsx"
```

---

## 4.7 日历（Calendar）

### 查看日程

```bash
# 查看今日日程
lark-cli calendar +agenda

# 查看指定日期日程
lark-cli calendar +agenda --date "2026-05-15"
```

### 创建日程

```bash
# 创建简单日程
lark-cli calendar +create \
  --summary "团队周会" \
  --start "2026-05-15T10:00:00+08:00" \
  --end "2026-05-15T11:00:00+08:00"

# 邀请参会人
lark-cli calendar +create \
  --summary "项目评审" \
  --start "2026-05-16T14:00:00+08:00" \
  --end "2026-05-16T15:00:00+08:00" \
  --attendee-ids "ou_xxxxx,ou_yyyyy"

# 全天日程
lark-cli calendar +create \
  --summary "团建活动" \
  --start "2026-05-20" \
  --end "2026-05-20" \
  --all-day true
```

### 查询忙闲

```bash
# 查询用户在指定时段的忙闲
lark-cli calendar +freebusy \
  --start "2026-05-15T00:00:00+08:00" \
  --end "2026-05-15T23:59:59+08:00" \
  --attendee-ids "ou_xxxxx,ou_yyyyy"
```

**返回值示例**：
```json
{
  "time_period_list": [
    {
      "email": "user@example.com",
      "busy_time_list": [
        {
          "start_time": "1707123456789",
          "end_time": "1707127056789"
        }
      ]
    }
  ]
}
```

### 时间建议

```bash
# 查询空闲时段
lark-cli calendar +suggestion \
  --start "2026-05-15T09:00:00+08:00" \
  --end "2026-05-15T18:00:00+08:00" \
  --duration-minutes 30 \
  --attendee-ids "ou_xxxxx"
```

### 回复日程邀请

```bash
# 接受邀请
lark-cli calendar +rsvp \
  --event-id "oc_xxxxx" \
  --action accept

# 拒绝邀请
lark-cli calendar +rsvp \
  --event-id "oc_xxxxx" \
  --action decline
```

---

## 4.8 任务（Task）

### 创建任务

```bash
# 创建简单任务
lark-cli task +create \
  --summary "完成项目报告"

# 带截止日期
lark-cli task +create \
  --summary "完成项目报告" \
  --due "2026-05-20T23:59:59+08:00"

# 指定负责人
lark-cli task +create \
  --summary "完成项目报告" \
  --due "2026-05-20T23:59:59+08:00" \
  --member-ids "ou_xxxxx"
```

### 查询任务

```bash
# 获取我的任务
lark-cli task +get-my-tasks

# 按关键词搜索
lark-cli task +get-my-tasks --query "报告"
```

### 更新任务状态

```bash
# 完成任务
lark-cli task +complete \
  --guid "task_xxxxx"

# 重新打开任务
lark-cli task +reopen \
  --guid "task_xxxxx"

# 更新任务标题
lark-cli task +update \
  --guid "task_xxxxx" \
  --summary "更新后的标题"
```

### 子任务管理

```bash
# 创建子任务
lark-cli task subtasks create \
  --params '{"task_guid":"task_xxxxx"}' \
  --data '{"summary":"子任务1"}'

# 获取子任务列表
lark-cli task subtasks list \
  --params '{"task_guid":"task_xxxxx"}'
```

### 任务清单管理

```bash
# 创建任务清单
lark-cli task +tasklist-create \
  --name "本周计划"

# 添加任务到清单
lark-cli task +tasklist-task-add \
  --tasklist-id "tasklist_xxxxx" \
  --task-guid "task_xxxxx"
```

---

## 4.9 邮箱（Mail）

### 查看收件箱

```bash
# 查看收件箱摘要
lark-cli mail +triage

# 带搜索条件
lark-cli mail +triage --query "项目"
```

### 读取邮件

```bash
# 读取单封邮件
lark-cli mail +message --message-id "msg_xxxxx"

# 跳过 HTML 正文（节省 token）
lark-cli mail +message --message-id "msg_xxxxx" --html=false
```

### 发送邮件

⚠️ **安全提示**：发送邮件前必须向用户确认收件人和内容，获得明确同意后再发送。

```bash
# 保存为草稿（推荐先预览）
lark-cli mail +send \
  --to "recipient@example.com" \
  --subject "邮件主题" \
  --body "<p>邮件正文内容</p>"

# 直接发送（需用户确认）
lark-cli mail +send \
  --to "recipient@example.com" \
  --subject "邮件主题" \
  --body "<p>邮件正文内容</p>" \
  --confirm-send
```

### 回复/转发邮件

```bash
# 回复邮件
lark-cli mail +reply \
  --message-id "msg_xxxxx" \
  --body "<p>回复内容</p>"

# 回复全部
lark-cli mail +reply-all \
  --message-id "msg_xxxxx" \
  --body "<p>回复内容</p>"

# 转发邮件
lark-cli mail +forward \
  --message-id "msg_xxxxx" \
  --to "forward@example.com"
```

⚠️ **重要**：
- 默认保存为草稿，需要添加 `--confirm-send` 才实际发送
- 发送后必须调用 `send_status` 确认投递状态

---

## 4.10 通讯录（Contact）

### 搜索用户

```bash
# 按姓名搜索
lark-cli contact +search-user --query "张三"

# 返回结果示例
{
  "code": 0,
  "data": {
    "users": [
      {
        "open_id": "ou_xxxxx",
        "name": "张三",
        "en_name": "San Zhang",
        "email": "zhangsan@example.com",
        "mobile": "+86-138****1234"
      }
    ]
  }
}
```

### 获取用户信息

```bash
# 获取当前用户信息
lark-cli contact +get-user

# 获取指定用户信息
lark-cli contact +get-user --user-id "ou_xxxxx"
```

### 查询部门

```bash
# 获取部门列表
lark-cli contact departments list \
  --params '{"user_id_type":"open_id"}'

# 获取部门详情
lark-cli contact departments get \
  --params '{"department_id":"dpt_xxxxx","user_id_type":"open_id"}'
```

---

## 4.11 审批（Approval）

### 查询审批任务

```bash
# 查询待我审批的任务
lark-cli approval tasks query \
  --params '{"user_id_type":"open_id"}' \
  --data '{"topic":0}'

# 获取审批实例详情
lark-cli approval instances get \
  --params '{"instance_id":"instance_xxxxx","user_id_type":"open_id"}'
```

### 处理审批任务

```bash
# 同意审批
lark-cli approval tasks approve \
  --params '{"task_id":"task_xxxxx"}' \
  --data '{"comment":"同意"}'

# 拒绝审批
lark-cli approval tasks reject \
  --params '{"task_id":"task_xxxxx"}' \
  --data '{"comment":"不符合条件"}'

# 转交审批
lark-cli approval tasks transfer \
  --params '{"task_id":"task_xxxxx"}' \
  --data '{"target_user_id":"ou_xxxxx","comment":"请帮忙审批"}'
```

---

## 4.12 视频会议（VC）

### 搜索会议

```bash
# 搜索会议记录
lark-cli vc +search \
  --start-time "2026-01-01T00:00:00+08:00" \
  --end-time "2026-05-01T00:00:00+08:00"

# 按组织者搜索
lark-cli vc +search \
  --start-time "2026-01-01T00:00:00+08:00" \
  --end-time "2026-05-01T00:00:00+08:00" \
  --user-id "ou_xxxxx"
```

### 获取会议纪要

```bash
# 获取会议纪要
lark-cli vc +notes --meeting-ids "meeting_xxxxx"

# 获取妙记内容
lark-cli vc +notes --minute-tokens "obcn_xxxxx"
```

---

## 4.13 妙记（Minutes）

### 获取妙记信息

```bash
# 获取妙记基础信息
lark-cli minutes minutes get \
  --params '{"minute_token":"obcn_xxxxx"}'

# 返回结果
{
  "code": 0,
  "data": {
    "minute": {
      "title": "产品评审会议",
      "duration": 3600000,
      "owner_id": "ou_xxxxx",
      "url": "https://xxx.feishu.cn/minutes/obcn_xxxxx"
    }
  }
}
```

### 下载录音

```bash
# 下载音视频文件
lark-cli minutes +download \
  --minute-tokens "obcn_xxxxx" \
  --output "./meeting.mp4"

# 仅获取下载链接
lark-cli minutes +download \
  --minute-tokens "obcn_xxxxx" \
  --url-only
```

---

## 4.14 白板（Whiteboard）

### 创建白板

```bash
# 在云文档中创建白板
lark-cli docs +update \
  --doc "dox_xxxxx" \
  --mode append \
  --markdown '<whiteboard type="blank"></whiteboard>'
```

### 用 DSL 更新白板

⚠️ **说明**：白板编辑需要使用 `@larksuite/whiteboard-cli` 工具。

```bash
# 安装白板 CLI
npm install -g @larksuite/whiteboard-cli@^0.1.0

# 生成白板 DSL JSON
cat > my-diagram.json << 'EOF'
{
  "nodes": [
    {
      "type": "rect",
      "text": "开始",
      "x": 100,
      "y": 100
    }
  ]
}
EOF

# 渲染为 PNG
npx -y @larksuite/whiteboard-cli@^0.1.0 \
  -i my-diagram.json \
  -o ./my-diagram.png

# 上传到飞书白板
cat my-diagram.json | lark-cli docs +whiteboard-update \
  --whiteboard-token "wst_xxxxx" \
  --yes --as user
```

---

# 第五部分：高级场景

## 5.1 客户调查问卷

### 方案概述

使用多维表格 + 表单实现问卷收集：

```
┌─────────────────────────────────────────────────────────────┐
│  多维表格（Bitable）                                        │
│  ├── 数据表：问卷题目定义                                   │
│  ├── 数据表：收集的答案                                     │
│  └── 仪表盘：数据分析视图                                   │
├─────────────────────────────────────────────────────────────┤
│  表单（Bitable Form）                                       │
│  └── 用户填写入口                                           │
└─────────────────────────────────────────────────────────────┘
```

### 实施步骤

#### 步骤 1：创建多维表格

```bash
# 创建问卷数据表
lark-cli base +base-create --name "客户问卷"

# 创建问题表
lark-cli base +table-create \
  --base-token "bascnxxxxx" \
  --table-name "问题配置"

# 添加字段
lark-cli base +field-create \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx" \
  --field-name "问题编号" \
  --field-type "AutoNumber"

lark-cli base +field-create \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx" \
  --field-name "问题内容" \
  --field-type "Text"

lark-cli base +field-create \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx" \
  --field-name "问题类型" \
  --field-type "SingleSelect" \
  --json '{"options":[{"name":"单选"},{"name":"多选"},{"name":"文本"}]}'

lark-cli base +field-create \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx" \
  --field-name "选项列表" \
  --field-type "Text"
```

#### 步骤 2：创建答案收集表

```bash
# 创建答案表
lark-cli base +table-create \
  --base-token "bascnxxxxx" \
  --table-name "用户答案"

# 添加字段
lark-cli base +field-create \
  --base-token "bascnxxxxx" \
  --table-id "tbl_yyyyy" \
  --field-name "提交时间" \
  --field-type "CreatedTime"

lark-cli base +field-create \
  --base-token "bascnxxxxx" \
  --table-id "tbl_yyyyy" \
  --field-name "提交人" \
  --field-type "CreatedBy"

lark-cli base +field-create \
  --base-token "bascnxxxxx" \
  --table-id "tbl_yyyyy" \
  --field-name "Q1答案" \
  --field-type "Text"

lark-cli base +field-create \
  --base-token "bascnxxxxx" \
  --table-id "tbl_yyyyy" \
  --field-name "Q2答案" \
  --field-type "Text"
```

#### 步骤 3：创建表单

```bash
# 获取表单列表（查看表单 ID）
lark-cli base +form-list \
  --base-token "bascnxxxxx"

# 创建表单
lark-cli base +form-create \
  --base-token "bascnxxxxx" \
  --table-id "tbl_yyyyy" \
  --name "客户问卷表单"

# 添加表单问题
lark-cli base +form-questions-create \
  --base-token "bascnxxxxx" \
  --form-id "form_xxxxx" \
  --field-id "fld_yyyyy" \
  --question-id "q1" \
  --question-name "您的姓名是？" \
  --required true
```

#### 步骤 4：数据分析

```bash
# 使用 data-query 聚合分析
lark-cli base +data-query \
  --base-token "bascnxxxxx" \
  --table-id "tbl_yyyyy" \
  --json '{
    "aggregations": [
      {"field_name": "Q1答案", "agg_func": "COUNT"}
    ],
    "group_by": ["Q1答案"]
  }'
```

## 5.2 线上游戏对外连接

### 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│  外部系统（游戏服务器）                                      │
│  ├── 发送 Webhook 到 Agent                                  │
│  └── 接收 Agent 的消息回调                                  │
├─────────────────────────────────────────────────────────────┤
│  Open Claw Agent                                            │
│  ├── 接收 Webhook 事件                                      │
│  ├── 处理游戏逻辑                                           │
│  └── 通过飞书发送通知/交互                                   │
├─────────────────────────────────────────────────────────────┤
│  飞书                                                      │
│  ├── 消息卡片：游戏交互界面                                  │
│  ├── 多维表格：游戏数据存储                                  │
│  └── Bot：游戏 NPC 对话                                     │
└─────────────────────────────────────────────────────────────┘
```

### 接收 Webhook 事件

```python
#!/usr/bin/env python3
# webhook_server.py - 简单的 Webhook 接收服务器

from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    
    # 解析事件类型
    event_type = data.get('event_type')
    
    if event_type == 'game.player_action':
        player_id = data['player_id']
        action = data['action']
        
        # 处理游戏逻辑
        result = process_game_action(player_id, action)
        
        # 返回结果
        return jsonify({'status': 'ok', 'result': result})
    
    return jsonify({'status': 'unknown_event'})

def process_game_action(player_id, action):
    # 游戏逻辑处理
    return {'score': 100, 'level': 2}

if __name__ == '__main__':
    app.run(port=8080)
```

### 用消息卡片做交互界面

```bash
# 发送交互式游戏卡片
lark-cli im +messages-send \
  --chat-id "oc_xxxxx" \
  --msg-type "interactive" \
  --content '{
    "config": {"wide_screen_mode": true},
    "header": {
      "title": {"tag": "plain_text", "text": "🎮 游戏大厅"},
      "template": "purple"
    },
    "elements": [
      {
        "tag": "markdown",
        "content": "**欢迎来到游戏大厅！**\n\n请选择操作："
      },
      {
        "tag": "div",
        "text": {
          "tag": "lark_md",
          "content": "当前积分：{score}\n当前等级：{level}"
        }
      },
      {
        "tag": "action",
        "actions": [
          {
            "tag": "button",
            "text": {"tag": "plain_text", "content": "🎯 开始挑战"},
            "type": "primary",
            "value": {"action": "start_challenge"}
          },
          {
            "tag": "button",
            "text": {"tag": "plain_text", "content": "📊 查看排名"},
            "type": "default",
            "value": {"action": "view_ranking"}
          }
        ]
      }
    ]
  }'
```

### 用多维表格做游戏数据存储

```bash
# 创建游戏数据表
lark-cli base +base-create --name "游戏数据"

# 创建玩家表
lark-cli base +table-create \
  --base-token "bascnxxxxx" \
  --table-name "玩家数据"

# 添加字段
lark-cli base +field-create \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx" \
  --field-name "玩家ID" \
  --field-type "Text"

lark-cli base +field-create \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx" \
  --field-name "积分" \
  --field-type "Number"

lark-cli base +field-create \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx" \
  --field-name "等级" \
  --field-type "Number"

# 写入玩家数据
lark-cli base +record-upsert \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx" \
  --json '{
    "fields": {
      "玩家ID": "player_001",
      "积分": 1000,
      "等级": 5
    }
  }'
```

## 5.3 批量文件同步

### 完整脚本模板

> **📌 相关资源**
> - GitHub仓库：https://github.com/larksuite/cli
> - CLI许愿池（功能反馈）：https://bytedance.larkoffice.com/base/Ebxvb6usfakMENs2GHIcL5Ern2f

以下是经过实战验证的完整批量文件同步脚本：

```bash
#!/bin/bash
#==============================================================================
# 飞书云空间批量同步脚本 - feishu_full_sync.sh
# 功能：递归同步本地文件夹到飞书云空间（支持文件夹结构）
# 依赖：lark-cli、jq
# 使用：bash feishu_full_sync.sh
#==============================================================================

# ============ 配置区域（修改这里）============
# 飞书目标文件夹token，0表示根目录
FEISHU_FOLDER_TOKEN="0"

# 本地要同步的文件夹路径（绝对路径或相对路径）
LOCAL_DIR="./sync_source"

# 日志文件路径
LOG_FILE="./feishu_sync_log.txt"

# 同步状态记录文件（用于增量同步）
SYNC_STATE_FILE="./feishu_sync_state.json"

# 每次API调用间隔（秒），防止触发限流
RATE_LIMIT_DELAY=0.5

# 最大重试次数
MAX_RETRIES=3

# 是否启用增量同步（只传新增/修改文件）
INCREMENTAL_SYNC=true

# ============ 全局变量 ============
# 文件名到飞书token的缓存（避免重复查询）
declare -A FOLDER_TOKEN_CACHE
declare -A FILE_TOKEN_CACHE

# ============ 工具函数 ============

# 日志记录函数
log_info() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [INFO] $1" | tee -a "$LOG_FILE"
}

log_error() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [ERROR] $1" | tee -a "$LOG_FILE"
}

log_warn() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [WARN] $1" | tee -a "$LOG_FILE"
}

# 限流延迟函数
rate_limit() {
    sleep "$RATE_LIMIT_DELAY"
}

# 计算文件MD5（兼容Linux和macOS）
calculate_md5() {
    local file_path="$1"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS系统
        md5 -q "$file_path"
    else
        # Linux系统
        md5sum "$file_path" | cut -d' ' -f1
    fi
}

# 带重试的API调用函数
retry_api_call() {
    local max_attempts=${1:-MAX_RETRIES}
    local cmd="$2"
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        # 执行命令并捕获退出码和输出
        local output
        local exit_code
        output=$(eval "$cmd" 2>&1)
        exit_code=$?
        
        if [ $exit_code -eq 0 ]; then
            # 检查输出中是否包含错误
            if echo "$output" | grep -q '"code":[0-9]*[^0]' || echo "$output" | grep -q '"code":999'; then
                log_warn "API返回错误: $output"
            else
                echo "$output"
                return 0
            fi
        fi
        
        log_warn "API调用失败，尝试 $attempt/$max_attempts: $cmd"
        attempt=$((attempt + 1))
        
        # 指数退避等待
        local wait_time=$((attempt * 2))
        sleep $wait_time
    done
    
    log_error "API调用最终失败: $cmd"
    return 1
}

# ============ 飞书API封装函数 ============

# 获取或创建文件夹，返回folder_token
get_or_create_folder() {
    local parent_token="$1"
    local folder_name="$2"
    
    # 检查缓存
    local cache_key="${parent_token}_${folder_name}"
    if [ -n "${FOLDER_TOKEN_CACHE[$cache_key]}" ]; then
        echo "${FOLDER_TOKEN_CACHE[$cache_key]}"
        return 0
    fi
    
    # 先尝试列出父文件夹下的内容，查找同名文件夹
    local list_result
    list_result=$(lark-cli drive files list \
        --params "{\"folder_token\":\"$parent_token\"}" 2>/dev/null)
    
    # 解析是否存在同名文件夹
    local existing_token
    existing_token=$(echo "$list_result" | jq -r ".data.files[]? | select(.name == \"$folder_name\" and .token != null) | .token" 2>/dev/null | head -1)
    
    if [ -n "$existing_token" ] && [ "$existing_token" != "null" ]; then
        # 缓存并返回已存在的文件夹token
        FOLDER_TOKEN_CACHE[$cache_key]="$existing_token"
        echo "$existing_token"
        return 0
    fi
    
    # 文件夹不存在，创建新文件夹
    local create_result
    create_result=$(retry_api_call 3 "lark-cli drive files create_folder \
        --params '{\"folder_token\":\"$parent_token\"}' \
        --data '{\"name\":\"$folder_name\"}'")
    
    if [ $? -eq 0 ]; then
        local new_token
        new_token=$(echo "$create_result" | jq -r '.data.folder.token' 2>/dev/null)
        
        if [ -n "$new_token" ] && [ "$new_token" != "null" ]; then
            # 缓存新创建的文件夹token
            FOLDER_TOKEN_CACHE[$cache_key]="$new_token"
            log_info "创建文件夹成功: $folder_name -> $new_token"
            echo "$new_token"
            return 0
        fi
    fi
    
    log_error "获取或创建文件夹失败: $folder_name"
    return 1
}

# 上传文件到指定文件夹
upload_file() {
    local local_file="$1"
    local parent_token="$2"
    
    # 获取文件名
    local filename
    filename=$(basename "$local_file")
    
    # 检查文件是否存在
    if [ ! -f "$local_file" ]; then
        log_error "文件不存在: $local_file"
        return 1
    fi
    
    # 计算MD5（用于增量同步）
    local file_md5
    file_md5=$(calculate_md5 "$local_file")
    
    # 增量同步检查
    if [ "$INCREMENTAL_SYNC" = true ] && [ -f "$SYNC_STATE_FILE" ]; then
        # 读取上次同步状态
        local last_md5
        last_md5=$(jq -r ".files[\"$filename\"].md5 // empty" "$SYNC_STATE_FILE" 2>/dev/null)
        
        if [ "$file_md5" = "$last_md5" ]; then
            log_info "跳过（未变更）: $filename"
            return 0
        fi
    fi
    
    # 检查是否已存在同名文件
    local list_result
    list_result=$(lark-cli drive files list \
        --params "{\"folder_token\":\"$parent_token\"}" 2>/dev/null)
    
    local existing_file_token
    existing_file_token=$(echo "$list_result" | jq -r ".data.files[]? | select(.name == \"$filename\" and .token != null) | .token" 2>/dev/null | head -1)
    
    if [ -n "$existing_file_token" ] && [ "$existing_file_token" != "null" ]; then
        # 文件已存在，可以选择覆盖或跳过
        log_info "文件已存在（将覆盖）: $filename"
    fi
    
    # 执行上传
    log_info "正在上传: $filename"
    rate_limit
    
    local upload_result
    upload_result=$(retry_api_call 3 "lark-cli drive +upload \
        --file '$local_file' \
        --parent-token '$parent_token'")
    
    if [ $? -eq 0 ]; then
        log_info "上传成功: $filename"
        
        # 更新同步状态
        update_sync_state "$filename" "$file_md5"
        return 0
    else
        log_error "上传失败: $filename"
        log_error "错误详情: $upload_result"
        return 1
    fi
}

# 更新同步状态记录
update_sync_state() {
    local filename="$1"
    local md5="$2"
    
    # 如果状态文件不存在，创建初始结构
    if [ ! -f "$SYNC_STATE_FILE" ]; then
        echo '{"files": {}, "last_sync": ""}' > "$SYNC_STATE_FILE"
    fi
    
    # 使用jq更新状态
    local temp_file
    temp_file=$(mktemp)
    
    # 获取当前时间ISO格式
    local sync_time
    sync_time=$(date -Iseconds)
    
    # 更新JSON文件
    jq --arg f "$filename" --arg m "$md5" --arg t "$sync_time" \
       '.files[$f] = {"md5": $m, "synced_at": $t} | .last_sync = $t' \
       "$SYNC_STATE_FILE" > "$temp_file"
    
    mv "$temp_file" "$SYNC_STATE_FILE"
}

# ============ 核心同步逻辑 ============

# 递归同步文件夹
sync_folder_recursive() {
    local local_path="$1"
    local feishu_parent_token="$2"
    local relative_path="${local_path#$LOCAL_DIR/}"  # 计算相对路径
    
    # 检查本地路径是否存在
    if [ ! -d "$local_path" ]; then
        log_error "本地路径不存在: $local_path"
        return 1
    fi
    
    # 获取当前目录下的所有项
    for item in "$local_path"/*; do
        # 如果目录为空，item会是字面量"*"
        if [ "$item" = "$local_path/*" ]; then
            break
        fi
        
        if [ -d "$item" ]; then
            # 处理子文件夹
            local folder_name
            folder_name=$(basename "$item")
            
            # 在飞书端创建或获取同名文件夹
            local new_feishu_token
            new_feishu_token=$(get_or_create_folder "$feishu_parent_token" "$folder_name")
            
            if [ $? -eq 0 ] && [ -n "$new_feishu_token" ]; then
                log_info "进入子文件夹: $folder_name"
                # 递归处理子文件夹
                sync_folder_recursive "$item" "$new_feishu_token"
            else
                log_error "无法创建文件夹: $folder_name"
            fi
            
        elif [ -f "$item" ]; then
            # 处理文件
            upload_file "$item" "$feishu_parent_token"
        fi
        
        rate_limit  # 每次处理完一个项目后限流
    done
}

# ============ 主流程 ============

main() {
    echo "=========================================="
    echo "飞书批量同步工具"
    echo "=========================================="
    log_info "=========================================="
    log_info "同步开始"
    log_info "本地目录: $LOCAL_DIR"
    log_info "飞书目标: $FEISHU_FOLDER_TOKEN"
    log_info "增量同步: $INCREMENTAL_SYNC"
    log_info "=========================================="
    
    # 检查依赖
    if ! command -v jq &> /dev/null; then
        log_error "缺少依赖: jq，请先安装 (apt install jq 或 brew install jq)"
        exit 1
    fi
    
    if ! command -v lark-cli &> /dev/null; then
        log_error "缺少依赖: lark-cli，请先安装 (npm install -g lark-cli)"
        exit 1
    fi
    
    # 检查本地目录
    if [ ! -d "$LOCAL_DIR" ]; then
        log_error "本地目录不存在: $LOCAL_DIR"
        exit 1
    fi
    
    # 确保日志目录存在
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # 初始化状态文件
    if [ ! -f "$SYNC_STATE_FILE" ]; then
        echo '{"files": {}, "last_sync": ""}' > "$SYNC_STATE_FILE"
    fi
    
    # 开始同步
    local start_time
    start_time=$(date +%s)
    
    sync_folder_recursive "$LOCAL_DIR" "$FEISHU_FOLDER_TOKEN"
    
    local end_time
    end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_info "=========================================="
    log_info "同步完成，耗时: ${duration}秒"
    log_info "=========================================="
    
    # 显示同步状态摘要
    if [ -f "$SYNC_STATE_FILE" ]; then
        local file_count
        file_count=$(jq '.files | length' "$SYNC_STATE_FILE")
        log_info "已同步文件总数: $file_count"
    fi
}

# 执行主函数
main "$@"
```

### 使用方法

```bash
# 1. 设置可执行权限
chmod +x feishu_full_sync.sh

# 2. 修改脚本中的配置（FEISHU_FOLDER_TOKEN, LOCAL_DIR等）

# 3. 运行脚本
./feishu_full_sync.sh

# 4. 查看同步日志
cat feishu_sync_log.txt

# 5. 查看同步状态
cat feishu_sync_state.json
```

### 脚本特性说明

| 特性 | 说明 |
|------|------|
| 递归同步 | 自动保持本地目录结构到飞书 |
| 增量同步 | 通过MD5对比，只传新增/修改的文件 |
| 文件缓存 | 缓存文件夹token，避免重复查询 |
| 限流保护 | 每次API调用间隔0.5秒 |
| 错误重试 | API失败自动重试最多3次 |
| 指数退避 | 重试间隔递增：2s, 4s, 6s... |
| 日志记录 | 详细记录每个操作和错误 |
| 状态持久化 | 保存同步状态到JSON文件 |

```bash
#!/bin/bash
# feishu_full_sync.sh - 飞书云空间批量同步脚本
# 功能：本地文件夹 ↔ 飞书云空间双向同步

set -e  # 遇到错误立即退出

# ============== 配置区域 ==============
FEISHU_FOLDER_TOKEN="${FEISHU_FOLDER_TOKEN:-0}"  # 飞书文件夹 token，0 表示根目录
LOCAL_DIR="${LOCAL_DIR:-./sync_folder}"          # 本地文件夹路径
LOG_FILE="${LOG_FILE:-./feishu_sync_log.txt}"     # 日志文件
SYNC_STATE_FILE="${SYNC_STATE_FILE:-./sync_state.json}"  # 同步状态文件

# 同步模式：upload(本地上传) / download(飞书下载) / both(双向)
SYNC_MODE="${SYNC_MODE:-upload}"

# 限速：每次请求间隔（秒）
RATE_LIMIT_DELAY="${RATE_LIMIT_DELAY:-0.5}"

# ============== 工具函数 ==============

log() {
    local level="$1"
    local message="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" | tee -a "$LOG_FILE"
}

error() {
    log "ERROR" "$1"
}

info() {
    log "INFO" "$1"
}

# 限速延迟
rate_limit() {
    sleep "$RATE_LIMIT_DELAY"
}

# ============== 核心功能 ==============

# 上传单个文件到飞书
upload_file() {
    local local_path="$1"
    local filename=$(basename "$local_path")
    
    # 检查文件是否存在
    if [ ! -f "$local_path" ]; then
        error "文件不存在: $local_path"
        return 1
    fi
    
    # 计算文件 MD5
    local md5=$(md5sum "$local_path" | cut -d' ' -f1)
    
    # 检查是否已同步（通过 MD5）
    local existing_md5=$(grep "\"$filename\"" "$SYNC_STATE_FILE" 2>/dev/null | jq -r ".files[\"$filename\"].md5 // empty")
    
    if [ "$md5" == "$existing_md5" ]; then
        info "跳过（未变更）: $filename"
        return 0
    fi
    
    info "上传: $filename"
    
    # 执行上传
    if lark-cli drive +upload \
        --file "$local_path" \
        --parent-token "$FEISHU_FOLDER_TOKEN" \
        --file-name "$filename"; then
        
        # 更新同步状态
        update_sync_state "$filename" "$md5"
        info "上传成功: $filename"
    else
        error "上传失败: $filename"
        return 1
    fi
}

# 下载单个文件
download_file() {
    local file_token="$1"
    local filename="$2"
    local output_path="$LOCAL_DIR/$filename"
    
    info "下载: $filename"
    
    # 确保目录存在
    mkdir -p "$LOCAL_DIR"
    
    if lark-cli drive +download \
        --file-token "$file_token" \
        --output "$output_path"; then
        info "下载成功: $filename"
    else
        error "下载失败: $filename"
        return 1
    fi
}

# 更新同步状态
update_sync_state() {
    local filename="$1"
    local md5="$2"
    
    # 如果状态文件不存在，创建初始结构
    if [ ! -f "$SYNC_STATE_FILE" ]; then
        echo '{"files": {}}' > "$SYNC_STATE_FILE"
    fi
    
    # 使用 jq 更新状态（如果可用）
    if command -v jq &> /dev/null; then
        local temp_file=$(mktemp)
        jq --arg f "$filename" --arg m "$md5" \
           '.files[$f] = {"md5": $m, "synced_at": now | todate}' \
           "$SYNC_STATE_FILE" > "$temp_file"
        mv "$temp_file" "$SYNC_STATE_FILE"
    fi
}

# 列出飞书文件夹内容
list_feishu_files() {
    lark-cli drive files list \
        --params "{\"folder_token\":\"$FEISHU_FOLDER_TOKEN\"}" \
        --format ndjson 2>/dev/null | \
        grep -o '"token":"[^"]*"' | \
        sed 's/"token":"//g; s/"//g'
}

# ============== 同步逻辑 ==============

# 上传模式
sync_upload() {
    info "开始上传同步模式"
    
    # 确保本地目录存在
    if [ ! -d "$LOCAL_DIR" ]; then
        mkdir -p "$LOCAL_DIR"
        info "创建本地目录: $LOCAL_DIR"
    fi
    
    # 遍历本地文件
    local count=0
    for file in "$LOCAL_DIR"/*; do
        if [ -f "$file" ]; then
            upload_file "$file"
            rate_limit
            ((count++))
        fi
    done
    
    info "上传同步完成，共处理 $count 个文件"
}

# 下载模式
sync_download() {
    info "开始下载同步模式"
    
    # 确保本地目录存在
    mkdir -p "$LOCAL_DIR"
    
    # 获取飞书文件列表
    local files=$(list_feishu_files)
    local count=0
    
    while IFS= read -r file_token; do
        if [ -n "$file_token" ]; then
            # 获取文件名（需要额外调用）
            local file_info=$(lark-cli drive files get \
                --params "{\"file_token\":\"$file_token\"}" 2>/dev/null)
            local filename=$(echo "$file_info" | jq -r '.name // empty')
            
            if [ -n "$filename" ]; then
                download_file "$file_token" "$filename"
                rate_limit
                ((count++))
            fi
        fi
    done <<< "$files"
    
    info "下载同步完成，共处理 $count 个文件"
}

# ============== 主流程 ==============

main() {
    info "========================================="
    info "飞书批量同步开始"
    info "模式: $SYNC_MODE"
    info "飞书目录: $FEISHU_FOLDER_TOKEN"
    info "本地目录: $LOCAL_DIR"
    info "========================================="
    
    case "$SYNC_MODE" in
        upload)
            sync_upload
            ;;
        download)
            sync_download
            ;;
        both)
            sync_upload
            sync_download
            ;;
        *)
            error "未知同步模式: $SYNC_MODE"
            echo "支持的模式: upload, download, both"
            exit 1
            ;;
    esac
    
    info "========================================="
    info "同步完成"
    info "========================================="
}

# 运行
main
```

### 使用示例

```bash
# 上传本地文件到飞书根目录
SYNC_MODE=upload LOCAL_DIR="./documents" ./feishu_full_sync.sh

# 从飞书下载文件到本地
SYNC_MODE=download FEISHU_FOLDER_TOKEN="fld_xxxxx" LOCAL_DIR="./downloads" ./feishu_full_sync.sh

# 双向同步
SYNC_MODE=both ./feishu_full_sync.sh
```

### 错误处理和重试

```bash
#!/bin/bash
# retry.sh - 带重试的同步函数

retry() {
    local max_attempts=$1
    local delay=$2
    shift 2
    local cmd="$@"
    
    local attempt=1
    while [ $attempt -le $max_attempts ]; do
        if eval "$cmd"; then
            return 0
        fi
        
        echo "尝试 $attempt/$max_attempts 失败，${delay}s 后重试..."
        sleep $delay
        
        # 指数退避
        delay=$((delay * 2))
        ((attempt++))
    done
    
    echo "达到最大重试次数 $max_attempts"
    return 1
}

# 使用示例
retry 3 2 lark-cli drive +upload --file "test.pdf" --parent-token "0"
```

## 5.4 自动化工作流

### 事件订阅

#### 使用 CLI 长连接订阅

```bash
# 订阅所有事件
lark-cli event +subscribe

# 输出为 NDJSON 格式
# 每条事件示例：
{
  "schema": "2.0",
  "header": {
    "event_id": "xxx",
    "event_type": "im.message.receive_v1",
    "create_time": "1707123456789"
  },
  "event": {
    "message": {
      "message_id": "om_xxx",
      "chat_id": "oc_xxx",
      "content": "{\"text\":\"Hello\"}"
    }
  }
}
```

#### 常见事件类型

| 事件 | 说明 | 用途 |
|------|------|------|
| `im.message.receive_v1` | 接收消息 | 处理用户消息 |
| `im.message.reaction_v1` | 表情回应 | 统计互动 |
| `calendar.event.create_v4` | 创建日程 | 日程通知 |
| `approval.comment_v4` | 审批评论 | 审批提醒 |
| `drive.file.revision_update_v1` | 文档更新 | 版本跟踪 |
| `bitable.app.record_changed_v1` | 记录变更 | 数据同步 |

### Webhook事件订阅HTTP服务器脚本

以下是完整的Webhook HTTP服务器示例，用于接收飞书事件推送：

```python
#!/usr/bin/env python3
#==============================================================================
# 飞书Webhook事件订阅服务器 - feishu_webhook_server.py
# 功能：接收并处理飞书事件（消息、审批、文档变更等）
# 依赖：flask, lark-oapi
# 安装：pip install flask lark-oapi
#==============================================================================

from flask import Flask, request, jsonify
import json
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)

# ============ 事件处理函数 ============

def handle_message_receive(event_data):
    """处理接收消息事件"""
    try:
        message = event_data.get('message', {})
        sender = event_data.get('sender', {})
        
        message_id = message.get('message_id', '')
        chat_id = message.get('chat_id', '')
        msg_type = message.get('msg_type', '')
        content = message.get('content', '')
        sender_id = sender.get('sender_id', {}).get('open_id', '')
        
        logger.info(f"[消息事件] sender={sender_id}, chat={chat_id}, type={msg_type}")
        
        # 解析消息内容
        if msg_type == 'text':
            content_obj = json.loads(content)
            text = content_obj.get('text', '')
            logger.info(f"[文本消息] {text}")
            
            # 示例：处理特定命令
            if text.startswith('/help'):
                return {
                    'msg_type': 'text',
                    'content': json.dumps({'text': '可用命令：/help, /status, /report'})
                }
            elif text.startswith('/status'):
                return {
                    'msg_type': 'text', 
                    'content': json.dumps({'text': '系统运行正常'})
                }
        
        return None
        
    except Exception as e:
        logger.error(f"处理消息事件失败: {e}")
        return None

def handle_approval_event(event_data):
    """处理审批事件"""
    try:
        event_type = event_data.get('event_type', '')
        instance = event_data.get('instance', {})
        
        approval_code = instance.get('approval_code', '')
        title = instance.get('title', '')
        status = instance.get('status', '')
        
        logger.info(f"[审批事件] type={event_type}, code={approval_code}, title={title}")
        
        # 可以在这里添加通知逻辑
        # 例如：发送消息通知管理员
        
        return {'action': 'logged', 'approval_code': approval_code}
        
    except Exception as e:
        logger.error(f"处理审批事件失败: {e}")
        return None

def handle_document_change(event_data):
    """处理文档变更事件"""
    try:
        file = event_data.get('file', {})
        operator = event_data.get('operator', {})
        
        file_token = file.get('file_token', '')
        file_type = file.get('file_type', '')
        operator_id = operator.get('operator_id', '')
        
        logger.info(f"[文档变更] token={file_token}, type={file_type}, operator={operator_id}")
        
        return {'action': 'logged', 'file_token': file_token}
        
    except Exception as e:
        logger.error(f"处理文档变更事件失败: {e}")
        return None

# ============ Flask路由 ============

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    接收飞书Webhook推送的主入口
    """
    try:
        # 获取原始请求数据
        data = request.get_json(force=True)
        
        # 记录原始数据（用于调试）
        logger.info(f"[Webhook收到] {json.dumps(data, ensure_ascii=False)}")
        
        # 处理加密事件（如果配置了加密）
        if 'encrypt' in data:
            # 需要使用Encrypt Key解密
            encrypted = data['encrypt']
            # 解密逻辑...
            logger.info("收到加密事件，需要解密处理")
            return jsonify({'code': 0})
        
        # 解析事件头
        header = data.get('header', {})
        event_type = header.get('event_type', '')
        event_id = header.get('event_id', '')
        
        logger.info(f"[事件处理] type={event_type}, id={event_id}")
        
        # 获取事件数据
        event = data.get('event', {})
        
        # 根据事件类型调用对应处理函数
        if event_type == 'im.message.receive_v1':
            # 接收消息事件
            response = handle_message_receive(event)
            if response:
                # 如果需要回复消息，返回回复内容
                # 注意：这只是示例，实际需要通过API发送消息
                pass
                
        elif 'approval' in event_type:
            # 审批相关事件
            handle_approval_event(event)
            
        elif 'document' in event_type or 'file' in event_type:
            # 文档相关事件
            handle_document_change(event)
        
        # 返回成功响应
        return jsonify({'code': 0, 'msg': 'success'})
        
    except Exception as e:
        logger.error(f"处理Webhook失败: {e}", exc_info=True)
        return jsonify({'code': 1, 'msg': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'service': 'feishu-webhook-server'
    })

@app.route('/', methods=['GET'])
def index():
    """首页"""
    return jsonify({
        'name': '飞书Webhook服务器',
        'version': '1.0.0',
        'endpoints': {
            'webhook': '/webhook',
            'health': '/health'
        }
    })

# ============ 主函数 ============

if __name__ == '__main__':
    # 配置服务器参数
    HOST = '0.0.0.0'  # 监听所有网络接口
    PORT = 8080        # 监听端口
    
    logger.info(f"启动飞书Webhook服务器，监听 {HOST}:{PORT}")
    logger.info("请确保此服务可通过公网访问，并配置到飞书开发者后台")
    
    # 启动Flask应用
    # 生产环境建议使用gunicorn: gunicorn -w 4 -b 0.0.0.0:8080 feishu_webhook_server:app
    app.run(
        host=HOST,
        port=PORT,
        debug=False,
        threaded=True
    )
```

### 使用方法

```bash
# 1. 安装依赖
pip install flask lark-oapi

# 2. 运行服务器
python feishu_webhook_server.py

# 3. 使用ngrok让本地服务可公网访问（开发环境）
ngrok http 8080

# 4. 在飞书开发者后台配置Webhook URL
# 开发者后台 -> 你的应用 -> 开发配置 -> 事件与回调 -> 事件配置
# 配置请求地址为：https://your-domain.com/webhook
```

### 在飞书开发者后台配置Webhook

1. 登录 [飞书开发者后台](https://open.feishu.cn/app)
2. 选择你的应用
3. 进入「开发配置」→「事件与回调」
4. 点击「事件配置」
5. 订阅方式选择「将事件发送至开发者服务器」
6. 输入你的公网可访问地址（如 `https://your-server.com/webhook`）
7. 添加需要订阅的事件
8. 保存配置

### 常见事件类型配置

| 事件类型 | 订阅说明 |
|----------|----------|
| `im.message.receive_v1` | 接收消息，需要开通 `im:message:receive` 权限 |
| `im.message.reaction_v1` | 消息表情回应 |
| `calendar.event.create_v4` | 日程创建 |
| `approval.approval.create_v4` | 审批创建 |
| `approval.task.create_v4` | 审批任务创建 |
| `drive.file.revision_update_v1` | 文档版本更新 |
| `bitable.app.record_changed_v1` | 多维表格记录变更 |

### 安全配置

```python
# 可选：验证请求签名
@app.before_request
def verify_signature():
    """验证飞书请求签名"""
    from functools import wraps
    
    # 获取签名
    timestamp = request.headers.get('X-Lark-Request-Timestamp', '')
    signature = request.headers.get('X-Lark-Request-Signature', '')
    
    # 验证逻辑
    # 使用你的 Encrypt Key 和 Verification Token
    # ...

# 可选：配置加密策略
# 在开发者后台「加密策略」页面配置 Encrypt Key
# 事件会以加密形式推送，需要解密处理
```

### 生产环境部署建议

```bash
# 使用gunicorn运行（推荐）
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 --timeout 30 feishu_webhook_server:app

# 使用supervisor管理进程
# /etc/supervisor/conf.d/feishu-webhook.conf
[program:feishu-webhook]
command=gunicorn -w 4 -b 0.0.0.0:8080 feishu_webhook_server:app
directory=/path/to/project
autostart=true
autorestart=true
stderr_logfile=/var/log/feishu-webhook.err.log
stdout_logfile=/var/log/feishu-webhook.out.log
```

### 定时任务与飞书集成

```bash
#!/bin/bash
# daily_report.sh - 每日报告脚本

# 配置
CHAT_ID="oc_xxxxx"  # 发送到的群
REPORT_TIME="09:00" # 报告时间

while true; do
    # 获取当前时间
    CURRENT_TIME=$(date +%H:%M)
    
    if [ "$CURRENT_TIME" == "$REPORT_TIME" ]; then
        # 生成报告
        REPORT=$(generate_daily_report)
        
        # 发送报告
        lark-cli im +messages-send \
            --chat-id "$CHAT_ID" \
            --text "$REPORT"
        
        # 等待 1 分钟避免重复发送
        sleep 60
    fi
    
    # 每分钟检查一次
    sleep 60
done

generate_daily_report() {
    # 这里添加报告生成逻辑
    echo "📊 每日报告\n\n"
    echo "• 待办任务: 5\n"
    echo "• 今日日程: 3\n"
    echo "• 待审批: 2"
}
```

### 多 Agent 协作场景

```
┌─────────────────────────────────────────────────────────────┐
│  协调 Agent（Coordinator）                                   │
│  ├── 接收用户请求                                           │
│  ├── 分解任务                                               │
│  └── 调度执行 Agent                                         │
├─────────────────────────────────────────────────────────────┤
│  执行 Agent A（Calendar Agent）                              │
│  └── 日历管理：创建日程、查询忙闲                            │
├─────────────────────────────────────────────────────────────┤
│  执行 Agent B（Docs Agent）                                  │
│  └── 文档管理：创建文档、写入内容                            │
├─────────────────────────────────────────────────────────────┤
│  执行 Agent C（IM Agent）                                    │
│  └── 消息通知：发送群消息、私聊提醒                          │
└─────────────────────────────────────────────────────────────┘
```

## 5.5 人机共创文档

### AI 起草 → 用户评论 → AI 修改

```bash
#!/bin/bash
# collaborative_doc.sh - 人机共创流程

# 步骤 1：AI 起草文档
echo "步骤 1：AI 生成文档初稿..."

lark-cli docs +create \
  --title "产品需求文档 - 智能助手" \
  --markdown "# 产品需求文档

## 概述
[AI 生成的概述内容...]

## 功能需求
[AI 生成的功能需求...]

## 非功能需求
[AI 生成的非功能需求...]

## 风险评估
[AI 生成的风险评估...]
"

DOC_URL=$(echo $? | lark-cli docs +create ... | jq -r '.data.url')

echo "文档已创建: $DOC_URL"

# 步骤 2：通知用户审阅
echo "步骤 2：通知用户审阅..."

lark-cli im +messages-send \
  --chat-id "oc_xxxxx" \
  --text "📝 文档初稿已生成，请审阅并评论：[点击查看]($DOC_URL)"

# 步骤 3：获取用户评论
echo "步骤 3：等待用户评论（建议等待一段时间）..."

sleep 3600  # 等待 1 小时

# 获取评论
lark-cli drive file.comments list \
  --params "{\"file_token\":\"$DOC_TOKEN\"}"

# 步骤 4：AI 根据评论修改
echo "步骤 4：AI 根据评论修改文档..."

COMMENTS=$(lark-cli drive file.comments list ...)
MODIFIED_CONTENT=$(ai_revise "$COMMENTS")

lark-cli docs +update \
  --doc "$DOC_TOKEN" \
  --mode append \
  --markdown "## 修改记录

$MODIFIED_CONTENT"
```

### AI 评审用户文档

```bash
#!/bin/bash
# doc_review.sh - AI 评审文档

# 参数
DOC_TOKEN="dox_xxxxx"

# 获取文档内容
echo "获取文档内容..."
CONTENT=$(lark-cli docs +fetch --doc "$DOC_TOKEN")

# AI 评审
echo "AI 正在评审文档..."

REVIEW_RESULT=$(ai_analyze << 'EOF'
请评审以下文档的问题：
1. 逻辑完整性
2. 表述清晰度
3. 格式规范性
4. 潜在风险

文档内容：
$CONTENT
EOF
)

# 添加评审意见到文档
lark-cli drive +add-comment \
  --file-token "$DOC_TOKEN" \
  --content "[{\"type\":\"text\",\"text\":\"$REVIEW_RESULT\"}]"

echo "评审完成，已添加评论"
```

### Markdown ↔ 飞书文档双向转换

```bash
#!/bin/bash
# md_feishu_convert.sh - Markdown 与飞书文档互转

# Markdown → 飞书文档
md_to_feishu() {
    local md_file="$1"
    local title=$(head -1 "$md_file" | sed 's/^# //')
    
    lark-cli docs +create \
        --title "$title" \
        --markdown "$(cat "$md_file")"
}

# 飞书文档 → Markdown
feishu_to_md() {
    local doc_token="$1"
    local output_file="$2"
    
    lark-cli docs +fetch --doc "$doc_token" > "$output_file"
}

# 高级转换：处理飞书特有元素
advanced_convert() {
    local md_content="$1"
    
    # 处理飞书特有标签
    md_content=${md_content//<whiteboard /<img src="whiteboard_}
    md_content=${md_content//<\/whiteboard>/.png"/>}
    md_content=${md_content//<at /@}
    md_content=${md_content//<\/at>/}
    
    echo "$md_content"
}
```

---

# 第六部分：最佳实践和避坑指南

## 6.1 Token 安全

### 禁止事项

```
⚠️ 绝对禁止：
1. 在代码中硬编码 token
2. 将 token 提交到 Git
3. 在日志中输出 token
4. 将 token 通过不加密的渠道传输
5. 在前端代码中暴露 token
```

### 正确做法

```bash
# ✅ 使用环境变量
export LARK_APP_ID="cli_xxxxx"
export LARK_APP_SECRET="xxxxx"

# ✅ 使用配置文件（确保 .feishu-cli 在 .gitignore 中）
echo ".feishu-cli/" >> .gitignore

# ✅ 定期轮换 token
# 在开发者后台重新生成 App Secret
```

### 凭证存储最佳实践

```bash
# 创建 .env 文件（仅示例，不要真的这样做）
cat > .env.example << 'EOF'
# 复制此文件为 .env 并填入真实值
LARK_APP_ID=your_app_id
LARK_APP_SECRET=your_app_secret
EOF

# 使用 dotenv 加载
source .env 2>/dev/null || true
```

## 6.2 Rate Limit 应对策略

### 飞书 API 限制

| 场景 | 限制 | 说明 |
|------|------|------|
| 普通 API | 60 次/分钟 | 应用级别 |
| 发送消息 | 100 次/分钟 | Bot 发送 |
| 读取数据 | 无明确限制 | 建议控制频率 |
| 写入数据 | 10 次/秒 | 并发限制 |

### 限流保护代码

```bash
#!/bin/bash
# rate_limit.sh - 限流保护脚本

# 令牌桶算法实现
RATE_LIMIT_FILE="/tmp/rate_limit_tokens"

init_token_bucket() {
    local max_tokens=60
    local refill_rate=1  # 每秒补充 1 个
    echo "$max_tokens,$refill_rate,$(date +%s)" > "$RATE_LIMIT_FILE"
}

get_token() {
    if [ ! -f "$RATE_LIMIT_FILE" ]; then
        init_token_bucket
    fi
    
    local data=$(cat "$RATE_LIMIT_FILE")
    local max_tokens=$(echo "$data" | cut -d',' -f1)
    local refill_rate=$(echo "$data" | cut -d',' -f2)
    local last_refill=$(echo "$data" | cut -d',' -f3)
    local current_time=$(date +%s)
    
    # 计算补充的 token
    local elapsed=$((current_time - last_refill))
    local new_tokens=$((elapsed * refill_rate))
    local available=$((max_tokens + new_tokens))
    
    if [ $available -gt $max_tokens ]; then
        available=$max_tokens
    fi
    
    if [ $available -gt 0 ]; then
        # 消耗一个 token
        echo "$max_tokens,$refill_rate,$current_time" > "$RATE_LIMIT_FILE"
        return 0
    else
        # 需要等待
        sleep 1
        return 1
    fi
}

# 带限流的 API 调用
api_call_with_limit() {
    local cmd="$@"
    
    while true; do
        if get_token; then
            eval "$cmd"
            return $?
        fi
    done
}

# 使用示例
api_call_with_limit "lark-cli im +messages-send --chat-id oc_xxx --text hello"
```

### 指数退避重试

```bash
#!/bin/bash
# exponential_backoff.sh - 指数退避重试

exponential_backoff() {
    local max_attempts=5
    local base_delay=1
    local max_delay=60
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo "尝试 $attempt/$max_attempts..."
        
        if eval "$@"; then
            echo "成功"
            return 0
        fi
        
        local delay=$base_delay
        for i in $(seq 1 $((attempt - 1))); do
            delay=$((delay * 2))
        done
        
        if [ $delay -gt $max_delay ]; then
            delay=$max_delay
        fi
        
        echo "等待 ${delay}s 后重试..."
        sleep $delay
        
        ((attempt++))
    done
    
    echo "达到最大重试次数"
    return 1
}

# 使用示例
exponential_backoff lark-cli im +messages-send --chat-id oc_xxx --text hello
```

## 6.3 大文件处理

### 文件大小限制

| 操作 | 限制 | 说明 |
|------|------|------|
| 上传文件 | 10 GB | 单个文件 |
| 下载文件 | 10 GB | 单个文件 |
| 导入文件 | 50 MB | 需转换格式 |
| 导出文件 | 依赖格式 | PDF 等有页数限制 |

### 分片上传

```bash
#!/bin/bash
# chunk_upload.sh - 分片上传大文件

CHUNK_SIZE=5242880  # 5MB 每片

chunk_upload() {
    local file="$1"
    local folder_token="$2"
    
    local filename=$(basename "$file")
    local filesize=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file")
    local chunks=$(( (filesize + CHUNK_SIZE - 1) / CHUNK_SIZE ))
    
    echo "文件大小: $filesize 字节"
    echo "分片数量: $chunks"
    
    # 创建上传任务
    local upload_id=$(lark-cli drive files create_upload_task \
        --file-name "$filename" \
        --parent-token "$folder_token" \
        --file-size "$filesize" | jq -r '.data.upload_id')
    
    # 分片上传
    for i in $(seq 0 $((chunks - 1))); do
        local offset=$((i * CHUNK_SIZE))
        local remaining=$((filesize - offset))
        local this_chunk=$((remaining < CHUNK_SIZE ? remaining : CHUNK_SIZE))
        
        echo "上传分片 $((i+1))/$chunks..."
        
        # 提取分片
        dd if="$file" bs=1 skip=$offset count=$this_chunk of="/tmp/chunk_$i" 2>/dev/null
        
        # 上传分片
        lark-cli drive files upload_chunk \
            --upload-id "$upload_id" \
            --part-number $i \
            --data "@/tmp/chunk_$i"
        
        rm -f "/tmp/chunk_$i"
    done
    
    # 完成上传
    lark-cli drive files complete_upload \
        --upload-id "$upload_id"
}
```

## 6.4 并发控制

### 串行执行原则

```bash
#!/bin/bash
# serial_execution.sh - 串行执行批量任务

# 对于写操作，必须串行执行
for record in $(cat records.json | jq -r '.[] | @base64'); do
    # 解码
    data=$(echo "$record" | base64 -d)
    
    # 串行写入
    lark-cli base +record-upsert \
        --base-token "bascnxxxxx" \
        --table-id "tbl_xxxxx" \
        --json "$data"
    
    # 批次间延迟
    sleep 0.5
done
```

### 并发控制示例

```bash
#!/bin/bash
# concurrent_control.sh - 并发控制

MAX_CONCURRENT=5
TEMP_DIR="/tmp/concurrent_control"

init_semaphore() {
    rm -rf "$TEMP_DIR"
    mkdir -p "$TEMP_DIR"
    for i in $(seq 1 $MAX_CONCURRENT); do
        touch "$TEMP_DIR/slot_$i"
    done
}

acquire_slot() {
    while true; do
        for i in $(seq 1 $MAX_CONCURRENT); do
            if [ -f "$TEMP_DIR/slot_$i" ]; then
                rm "$TEMP_DIR/slot_$i"
                echo "slot_$i"
                return 0
            fi
        done
        sleep 0.1
    done
}

release_slot() {
    local slot="$1"
    touch "$TEMP_DIR/$slot"
}

concurrent_task() {
    local task_id="$1"
    local slot=$(acquire_slot)
    
    echo "任务 $task_id 开始 (使用 slot: $slot)"
    
    # 执行任务
    sleep 2
    
    echo "任务 $task_id 完成"
    
    release_slot "$slot"
}

# 使用示例
init_semaphore
for i in $(seq 1 10); do
    concurrent_task "$i" &
done
wait
```

## 6.5 错误码速查表

### 认证错误

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 99991681 | App ID 无效 | 检查 App ID 是否正确 |
| 99991682 | App Secret 无效 | 重新获取 App Secret |
| 99991663 | 权限不足 | 开通对应权限 |
| 99991664 | Token 过期 | 刷新 token |
| 99991665 | Token 无效 | 重新获取 token |

### 业务错误

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 230001 | 用户不存在 | 检查 user_id |
| 230002 | 群聊不存在 | 检查 chat_id |
| 230003 | 消息不存在 | 检查 message_id |
| 230004 | 文档不存在 | 检查 doc_token |
| 230005 | 权限不足 | 检查操作权限 |
| 230006 | 参数错误 | 检查请求参数 |

### 限流错误

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 429 | 请求过于频繁 | 降低请求频率 |
| 500 | 服务器错误 | 重试请求 |

## 6.6 调试技巧

### 查看 CLI 详细日志

```bash
# 启用调试模式
lark-cli --debug im +messages-send --chat-id oc_xxx --text hello

# 查看完整请求/响应
lark-cli --verbose im +messages-send --chat-id oc_xxx --text hello
```

### 使用 --dry-run 预览

```bash
# 预览操作但不实际执行
lark-cli base +record-upsert \
  --base-token "bascnxxxxx" \
  --table-id "tbl_xxxxx" \
  --json '{}' \
  --dry-run
```

### 检查 API 规范

```bash
# 查看命令参数
lark-cli im +messages-send --help

# 查看 API schema
lark-cli schema im.message.send

# 查看可用模块
lark-cli --help
```

### 常见调试场景

```bash
# 1. 检查认证状态
lark-cli auth status

# 2. 测试 API 连通性
lark-cli api GET /open-apis/health

# 3. 检查权限
lark-cli auth login --domain all
lark-cli auth status

# 4. 查看最近操作日志
tail -100 ~/.lark-cli/logs/*.log
```

## 6.7 与 Coze 体系内 Agent 的差异

### 关键差异点

| 维度 | Coze 内置飞书 | Open Claw + lark-cli |
|------|---------------|---------------------|
| 消息发送 | 飞书渠道直接发送 | 使用 lark-cli |
| 授权方式 | Coze 平台管理 | 手动 OAuth |
| 事件接收 | Coze Webhook | CLI 长连接 |
| 配置文件 | Coze 管理 | 本地 .feishu-cli/ |
| 身份切换 | 平台自动 | CLI --as 参数 |

### Open Claw 特有注意事项

```
⚠️ Open Claw 必须注意：

1. 【消息发送】
   ❌ 不要使用 lark-cli 发送消息给用户
   ✅ 通过 Coze 平台飞书渠道发送
   
2. 【授权管理】
   ❌ 不要在 Coze 内部使用 lark-cli auth
   ✅ 通过 feishu_auth_and_create 工具
   
3. 【配置文件】
   ❌ 不要直接编辑 .feishu-cli/ 下的文件
   ✅ 使用 lark-cli config 命令
   
4. 【身份选择】
   ❌ 不要假设默认身份
   ✅ 明确指定 --as user 或 --as bot
```

---

# 第七部分：快速参考

## 7.1 CLI 命令速查表

### 身份认证

```bash
# 查看认证状态
lark-cli auth status

# 用户授权
lark-cli auth login --no-wait --domain all
lark-cli auth login --device-code

# 刷新 token
lark-cli auth refresh
```

### 即时通讯（IM）

```bash
# 发送消息
lark-cli im +messages-send --chat-id OC_xxx --text "Hello"
lark-cli im +messages-reply --message-id OM_xxx --text "Reply"

# 搜索消息
lark-cli im +messages-search --query "关键词"

# 群管理
lark-cli im +chat-create --name "新群"
lark-cli im +chat-messages-list --chat-id OC_xxx
lark-cli im +chat-members-list --chat-id OC_xxx
```

### 云文档（Docs）

```bash
# 创建和读取
lark-cli docs +create --title "标题" --markdown "# 内容"
lark-cli docs +fetch --doc DOC_xxx
lark-cli docs +search --query "关键词"

# 更新文档
lark-cli docs +update --doc DOC_xxx --mode append --markdown "新内容"
```

### 多维表格（Base）

```bash
# 表结构操作
lark-cli base +base-create --name "表格名"
lark-cli base +table-list --base-token BASC_xxx
lark-cli base +field-list --base-token BASC_xxx --table-id TBL_xxx

# 记录操作
lark-cli base +record-list --base-token BASC_xxx --table-id TBL_xxx
lark-cli base +record-upsert --base-token BASC_xxx --table-id TBL_xxx --json '{}'
```

### 日历（Calendar）

```bash
# 日程管理
lark-cli calendar +agenda
lark-cli calendar +create --summary "会议" --start "2026-05-01T10:00:00+08:00" --end "2026-05-01T11:00:00+08:00"
lark-cli calendar +freebusy --start "2026-05-01T00:00:00+08:00" --end "2026-05-01T23:59:59+08:00"
```

### 云空间（Drive）

```bash
# 文件操作
lark-cli drive +upload --file "/path" --parent-token FLD_xxx
lark-cli drive +download --file-token BOX_xxx --output "./file"
lark-cli drive +move --file-token BOX_xxx --target-folder-token FLD_xxx
lark-cli drive files create_folder --params '{"folder_token":"0"}' --data '{"name":"新文件夹"}'
```

### 任务（Task）

```bash
lark-cli task +create --summary "任务标题"
lark-cli task +get-my-tasks
lark-cli task +complete --guid GUID_xxx
```

### 邮箱（Mail）

```bash
lark-cli mail +triage
lark-cli mail +message --message-id MSG_xxx
lark-cli mail +send --to "xxx@example.com" --subject "主题" --body "<p>内容</p>"
```

### 通讯录（Contact）

```bash
lark-cli contact +search-user --query "姓名"
lark-cli contact +get-user
```

### 知识库（Wiki）

```bash
# Wiki 链接必须先解析
lark-cli wiki spaces get_node --params '{"token":"WIK_xxx"}'
```

## 7.2 API 端点速查表

### 基础信息

```
Base URL: https://open.feishu.cn/open-apis
Auth: Bearer {token}
Content-Type: application/json
```

### 常用端点

| 功能 | 方法 | 端点 |
|------|------|------|
| 获取 tenant_token | POST | /auth/v3/tenant_access_token/internal |
| 获取 user_token | POST | /authen/v1/oidc/access_token |
| 发送消息 | POST | /im/v1/messages |
| 创建群 | POST | /im/v1/chats |
| 发送消息卡片 | POST | /im/v1/messages |
| 创建文档 | POST | /docx/v1/documents |
| 读取文档 | GET | /docx/v1/documents/{document_id} |
| 创建多维表格 | POST | /bitable/v1/apps |
| 创建日程 | POST | /calendar/v4/calendars/primary/events |

## 7.3 权限 Scope 速查表

### IM 权限

| Scope | 说明 |
|-------|------|
| `im:message:send` | 发送消息 |
| `im:message:receive` | 接收消息 |
| `im:chat:readonly` | 读取群聊 |
| `im:chat:create` | 创建群聊 |
| `im:chat.members:read` | 读取群成员 |

### Calendar 权限

| Scope | 说明 |
|-------|------|
| `calendar:calendar:read` | 读取日历 |
| `calendar:calendar:write` | 写入日历 |
| `calendar:event:create` | 创建日程 |
| `calendar:free_busy:read` | 查询忙闲 |

### Docs 权限

| Scope | 说明 |
|-------|------|
| `docs:doc:readonly` | 只读文档 |
| `docs:doc:write` | 读写文档 |
| `docs:search:read` | 搜索文档 |

### Base 权限

| Scope | 说明 |
|-------|------|
| `base:app:readonly` | 读取多维表格 |
| `base:app:write` | 读写多维表格 |
| `base:record:write` | 写入记录 |

### Drive 权限

| Scope | 说明 |
|-------|------|
| `drive:drive:read` | 读取云空间 |
| `drive:drive:write` | 写入云空间 |
| `drive:file:upload` | 上传文件 |
| `drive:file:download` | 下载文件 |

### Mail 权限

| Scope | 说明 |
|-------|------|
| `mail:mail:readonly` | 读取邮件 |
| `mail:mail:write` | 发送邮件 |

## 7.4 常用脚本模板合集

### 批量发送消息

```bash
#!/bin/bash
# batch_send.sh - 批量发送消息

CHAT_IDS=("oc_xxx1" "oc_xxx2" "oc_xxx3")
MESSAGE="这是一条批量消息"

for chat_id in "${CHAT_IDS[@]}"; do
    echo "发送至: $chat_id"
    lark-cli im +messages-send --chat-id "$chat_id" --text "$MESSAGE"
    sleep 1  # 避免限流
done
```

### 批量创建记录

```bash
#!/bin/bash
# batch_insert.sh - 批量插入记录

BASE_TOKEN="bascnxxxxx"
TABLE_ID="tblxxxxx"

# JSON 数据文件
DATA_FILE="records.json"

# 读取并批量插入
cat "$DATA_FILE" | jq -c '.[]' | while read record; do
    lark-cli base +record-upsert \
        --base-token "$BASE_TOKEN" \
        --table-id "$TABLE_ID" \
        --json "$record"
    sleep 0.5
done
```

### 定时报告

```bash
#!/bin/bash
# daily_report.sh - 每日报告

REPORT_TIME="09:00"
CHAT_ID="oc_xxxxx"

while true; do
    current=$(date +%H:%M)
    if [ "$current" == "$REPORT_TIME" ]; then
        # 生成报告
        TASK_COUNT=$(lark-cli task +get-my-tasks | jq length)
        CALENDAR=$(lark-cli calendar +agenda | jq -r '.data.items[] | .summary' | head -5)
        
        MESSAGE="📊 每日简报

📋 待办任务: $TASK_COUNT 项
📅 今日日程:
$CALENDAR"

        lark-cli im +messages-send --chat-id "$CHAT_ID" --text "$MESSAGE"
        sleep 60
    fi
    sleep 60
done
```

### 数据导出

```bash
#!/bin/bash
# export_data.sh - 导出多维表格数据

BASE_TOKEN="bascnxxxxx"
TABLE_ID="tblxxxxx"
OUTPUT_FILE="export.json"

# 获取所有记录
lark-cli base +record-list \
    --base-token "$BASE_TOKEN" \
    --table-id "$TABLE_ID" \
    --limit 200 > "$OUTPUT_FILE"

echo "已导出至: $OUTPUT_FILE"
```

---

# 第八部分：Skill与MCP工具生态

> **📌 关键资源**
> - 飞书CLI GitHub仓库：https://github.com/larksuite/cli
> - 飞书CLI安装指南：https://open.feishu.cn/document/no_class/mcp-archive/feishu-cli-installation-guide.md
> - 飞书CLI许愿池：https://bytedance.larkoffice.com/base/Ebxvb6usfakMENs2GHIcL5Ern2f

## 8.1 飞书CLI Skill（Coze平台）

在Coze平台中，lark_cli是一个封装好的Skill，提供对飞书CLI的便捷调用能力。

### Skill结构说明

```
lark_cli/
├── SKILL.md              # 主技能说明文件
├── lark-shared/         # 共享规则（认证、授权、身份）
│   ├── SUB_SKILL.md     # 共享基础规则
│   └── scripts/
│       └── bind_credentials.py  # 凭证绑定脚本
├── lark-calendar/       # 日历模块
├── lark-im/             # 即时通讯模块
├── lark-doc/             # 云文档模块
├── lark-base/            # 多维表格模块
├── lark-sheets/          # 电子表格模块
├── lark-task/            # 任务模块
├── lark-mail/            # 邮箱模块
├── lark-contact/          # 通讯录模块
├── lark-drive/           # 云空间模块
├── lark-wiki/             # 知识库模块
├── lark-approval/         # 审批模块
├── lark-vc/              # 视频会议模块
├── lark-minutes/         # 妙记模块
├── lark-whiteboard/       # 白板模块
├── lark-event/            # 事件订阅模块
├── lark-openapi-explorer/ # API探索器
└── lark-skill-maker/      # 技能创建工具
```

### Coze中调用lark_cli的方式

```bash
# 使用skill_load加载技能
skill_load("lark_cli")

# 然后可以使用lark-cli命令
lark-cli auth status
lark-cli calendar +agenda
lark-cli docs +create --title "文档标题"
```

### Skill的优势

| 特性 | 说明 |
|------|------|
| 开箱即用 | 预配置了认证信息 |
| 子技能分离 | 每个模块独立，按需加载 |
| 详细文档 | 包含完整的命令参数说明 |
| 示例代码 | 提供真实可运行的示例 |

## 8.2 MCP与飞书CLI的关系

### MCP（Model Context Protocol）

MCP是一种标准化协议，允许AI模型与外部工具和数据源交互。飞书CLI可以作为MCP服务器使用。

### 飞书MCP配置示例

```json
// Claude Desktop 或其他MCP客户端配置
{
  "mcpServers": {
    "feishu": {
      "command": "npx",
      "args": ["-y", "@larksuite/mcp-cli"]
    }
  }
}
```

### MCP vs CLI对比

| 维度 | MCP | CLI |
|------|-----|-----|
| 交互方式 | 标准化协议 | 命令行 |
| 适用场景 | AI工具集成 | 脚本自动化 |
| 配置复杂度 | 中等 | 低 |
| 功能覆盖 | 基础操作 | 完整功能 |
| 实时性 | 需要MCP客户端 | 直接执行 |

## 8.3 在AI工具中集成飞书CLI

### TRAE IDE集成

1. 安装TRAE（https://trae.ai/）
2. 在TRAE终端中安装lark-cli：`npm install -g lark-cli`
3. 配置飞书应用凭证
4. 在TRAE的Terminal中直接使用lark-cli命令

### Cursor编辑器集成

1. 安装Cursor（https://cursor.sh/）
2. 在Cursor的终端（Terminal）中安装lark-cli
3. 可以通过Agent或Composer使用飞书API

### Claude Code集成

Claude Code是Anthropic的CLI工具，可以通过以下方式集成：

```bash
# 1. 安装Claude Code
npm install -g @anthropic/claude-code

# 2. 在项目中使用lark-cli
# 创建Makefile或脚本调用飞书功能

# 3. 在claude_desktop_config.json中配置MCP
```

### Claude Desktop MCP配置

```json
{
  "mcpServers": {
    "feishu": {
      "command": "npx",
      "args": ["-y", "@larksuite/mcp-cli"],
      "env": {
        "FEISHU_APP_ID": "your_app_id",
        "FEISHU_APP_SECRET": "your_app_secret"
      }
    }
  }
}
```

## 8.4 飞书官方Open Claw插件

飞书官方提供了基于CLI的Open Claw插件，可以在Open Claw环境中直接使用飞书功能。

### 插件特点

- 底层基于lark-cli实现
- 提供AI Agent友好的交互接口
- 支持自然语言调用飞书API
- 内置错误处理和重试机制

### 使用方式

```
用户: "帮我创建一个项目文档"
Agent:  调用 lark-cli docs +create
       返回文档链接给用户
```

---

# 第九部分：学习资源

> **📌 关键资源**
> - 飞书开发者社区：https://open.feishu.cn/document/home
> - 飞书开放平台文档：https://open.feishu.cn/document/server-docs
> - GitHub仓库：https://github.com/larksuite/cli

## 9.1 官方学习路径

### 新手入门

1. **阅读官方文档**
   - 飞书开放平台概览：https://open.feishu.cn/document/home/introduction-to-skywalking
   - 快速开始指南：https://open.feishu.cn/document/server-docs/quickstart

2. **安装配置CLI**
   - 安装指南：https://open.feishu.cn/document/no_class/mcp-archive/feishu-cli-installation-guide.md
   - GitHub仓库：https://github.com/larksuite/cli

3. **创建第一个应用**
   - 开发者后台：https://open.feishu.cn/app
   - 按照引导创建自建应用

### 进阶学习

1. **API深入学习**
   - 服务端API文档：https://open.feishu.cn/document/server-docs
   - API Explorer：https://open.feishu.cn/document/server-docs/api-explorer

2. **CLI高级用法**
   - 查看CLI帮助：`lark-cli --help`
   - 查看模块帮助：`lark-cli <module> --help`

3. **事件订阅**
   - WebSocket长连接：`lark-cli event +subscribe`
   - Webhook配置：在开发者后台配置

## 9.2 GitHub资源

### 官方仓库

| 仓库 | 地址 | 说明 |
|------|------|------|
| lark-cli | https://github.com/larksuite/cli | CLI主仓库 |
| lark-oapi | https://github.com/larksuite/oapi-sdk | Python/Go SDK |
| lark-nodejs | https://github.com/larksuite/oapi-sdk-nodejs | Node.js SDK |

### 示例代码

GitHub仓库中的examples目录包含：
- 消息发送示例
- 文档操作示例
- 日历管理示例
- 事件订阅示例

### Issue和讨论

- 功能反馈：https://github.com/larksuite/cli/issues
- 功能请求（许愿池）：https://bytedance.larkoffice.com/base/Ebxvb6usfakMENs2GHIcL5Ern2f

## 9.3 社区资源

### 飞书开发者社区

- 首页：https://open.feishu.cn/document/home
- 教程中心：https://open.feishu.cn/document/home/tutorial
- 最佳实践：https://open.feishu.cn/document/home/best-practice

### 常见问题解答

1. **Q: 如何获取App ID和App Secret？**
   A: 登录开发者后台(https://open.feishu.cn/app)，创建应用后在凭证页面获取

2. **Q: Bot身份和User身份有什么区别？**
   A: Bot以应用身份操作，User以用户身份操作。Bot无需授权，User需要OAuth授权

3. **Q: 为什么API调用返回permission denied？**
   A: 需要在开发者后台开通对应权限，并通过审核

4. **Q: 如何避免API限流？**
   A: 控制请求频率，使用指数退避重试，合理使用缓存

### 互助交流群

在飞书开发者社区可以找到官方互助交流群二维码，可以与其他开发者交流经验。

## 9.4 推荐学习顺序

```
1. 环境搭建
   └── 安装Node.js → 安装lark-cli → 配置应用

2. 基础操作
   └── 发送消息 → 读写文档 → 基础CRUD

3. 进阶功能
   └── 权限管理 → 事件订阅 → 批量操作

4. 最佳实践
   └── 错误处理 → 性能优化 → 安全加固
```

## 9.5 实战项目推荐

### 项目1：自动化周报机器人
- 定时收集任务数据
- 生成周报文档
- 发送到群聊

### 项目2：知识库同步工具
- 本地Markdown批量导入
- 知识库结构同步
- 增量更新机制

### 项目3：会议助手
- 日程冲突检测
- 会议室预订
- 会议纪要生成

### 项目4：数据收集系统
- 多维表格创建
- 表单生成
- 数据分析和可视化

---

## 附录：词汇表

| 术语 | 说明 |
|------|------|
| Token | 访问凭证，用于 API 认证 |
| Scope | 权限范围，定义 API 访问能力 |
| App ID | 应用唯一标识符 |
| App Secret | 应用密钥，用于获取 token |
| Chat ID | 群聊/会话 ID，格式为 oc_xxx |
| Message ID | 消息 ID，格式为 om_xxx |
| Doc Token | 文档标识符，格式为 dox_xxx |
| Base Token | 多维表格标识符，格式为 bascn_xxx |
| Spreadsheet Token | 电子表格标识符，格式为 shtcn_xxx |
| Folder Token | 文件夹标识符，格式为 fld_xxx |
| Open ID | 用户开放 ID，格式为 ou_xxx |
| Wiki Token | 知识库节点 ID，格式为 wikn_xxx |

---

> **文档结束**
> 
> 本文档由满意扣子 AI 基于 2026 年 5 月实战经验编写
> 如有问题，请查阅 [飞书开放平台文档](https://open.feishu.cn/document)

---

## 第十部分：批量同步实战经验与避坑（2026-05-07新增）

> 本章节基于满意扣子2026年5月7日真实踩坑经验，从"差点翻车"到"找到正确路径"的完整复盘。

### 10.1 核心教训：永远不要逐个手动上传

**踩坑场景**：10450个文件需要同步到飞书，一开始用lark-cli逐个执行`drive +upload`命令，每次调用消耗大量token，而且因为sub-agent并行执行导致同一文件夹被重复创建多次。

**后果**：
- 根目录出现3个"基础设定"、2个"用户上传"、2个"系统"、2个"EntroCamp学习笔记"、2个"00_核心文档"
- MEMORY.md重复7次，SECRET.md重复4次
- 满意解研究所下4个"03_运营体系"、4个"01_产品体系"
- skills目录下16个子目录全部重复
- 总计58个重复项需要清理

**正确做法**：先写批量脚本，脚本内含去重逻辑，一次执行完成。

### 10.2 批量同步正确流程

```
Step 1: 在飞书创建根文件夹和一级子目录
Step 2: 建立本地目录→飞书token的映射表（保存到文件）
Step 3: 对每个目标文件夹，先列出已有文件名
Step 4: 对比本地文件，只上传缺失的
Step 5: 更新映射表，记录上传结果
```

**关键原则**：
1. **先查再传**——每次上传前必须检查目标文件夹是否已有同名文件
2. **映射表持久化**——token映射表保存到MD文件，后续增量同步复用
3. **单一执行者**——同一时间只有一个进程操作飞书，避免并行创建重复文件夹

### 10.3 Token映射表设计

```markdown
# 飞书文件夹Token映射表

## 根目录
- 根文件夹: TIo8fDD8pl1AWOd56E4cGY6InMb

## 一级目录
| 本地路径 | 飞书文件夹名 | Token |
|---------|-------------|-------|
| ./基础设定/ | 基础设定 | Myrwf5p3KlmpyOdCrk6cAWIenHc |
| ./skills/ | skills | XpQDfsKvvl3hHIdXS2EcH7ZYnQJ |
| ./五维决策测评系统/ | 五维决策测评系统 | QZ0RfKyb3lse0tdMlW4ctf0pn6f |
| ... | ... | ... |

## 二级目录
| 本地路径 | 飞书父文件夹Token | 飞书文件夹名 | Token |
|---------|-----------------|-------------|-------|
| ./满意解研究所/01_产品体系/ | Wk6uf26N1lt2xWd19dzcFMo5nog | 01_产品体系 | NvYPfX3Qglahlmd2plKcZAQqnrh |
| ... | ... | ... | ... |
```

### 10.4 去重清理脚本

当重复已经发生后，用以下脚本清理：

```bash
#!/bin/bash
# feishu_dedup.sh - 飞书云空间去重清理脚本
# 用法: bash feishu_dedup.sh <根文件夹token>

ROOT_TOKEN="${1:?请提供根文件夹token}"
AS="user"

echo "=== 开始去重清理 ==="
echo "根文件夹: $ROOT_TOKEN"

# 获取根目录下所有文件/文件夹
items=$(lark-cli drive files list \
  --params "{\"folder_token\":\"$ROOT_TOKEN\"}" \
  --as $AS \
  -q '.data.files[]|"\(.name)|\(.token)|\(.type)"' 2>/dev/null)

# 按名称分组，找出重复
declare -A name_count
declare -A name_tokens

while IFS='|' read -r name token type; do
  name_count[$name]=$(( ${name_count[$name]:-0} + 1 ))
  name_tokens[$name]="${name_tokens[$name]:-} $token"
done <<< "$items"

# 对重复项，保留第一个token，删除其余
for name in "${!name_count[@]}"; do
  if [ ${name_count[$name]} -gt 1 ]; then
    echo "发现重复: $name (${name_count[$name]}个)"
    tokens=(${name_tokens[$name]})
    keep_token=${tokens[0]}
    echo "  保留: $keep_token"
    
    # 删除其余
    for ((i=1; i<${#tokens[@]}; i++)); do
      del_token=${tokens[$i]}
      echo "  删除: $del_token"
      lark-cli drive +delete --token "$del_token" --as $AS 2>/dev/null
      sleep 0.3
    done
  fi
done

echo "=== 去重完成 ==="
```

### 10.5 增量同步脚本（正确版）

```bash
#!/bin/bash
# feishu_incremental_sync.sh - 增量同步脚本
# 核心逻辑：先查飞书已有文件，只上传缺失的

ROOT_TOKEN="TIo8fDD8pl1AWOd56E4cGY6InMb"
AS="user"
TOKEN_MAP_FILE="./飞书文件夹token映射表.md"
SYNC_LOG="./feishu_incremental_log.txt"

# 从映射表读取token（简化版，实际应解析MD文件）
get_folder_token() {
  local folder_name="$1"
  # 列出根目录文件，按名称匹配
  lark-cli drive files list \
    --params "{\"folder_token\":\"$ROOT_TOKEN\"}" \
    --as $AS \
    -q ".data.files[]|select(.name==\"$folder_name\")|.token" 2>/dev/null | head -1
}

# 获取飞书文件夹中已有的文件名列表
get_existing_files() {
  local folder_token="$1"
  lark-cli drive files list \
    --params "{\"folder_token\":\"$folder_token\"}" \
    --as $AS \
    -q '.data.files[]|.name' 2>/dev/null
}

# 上传单个文件（如飞书中不存在）
upload_if_missing() {
  local local_file="$1"
  local folder_token="$2"
  local filename=$(basename "$local_file")
  
  # 检查是否已存在
  existing=$(get_existing_files "$folder_token")
  if echo "$existing" | grep -qF "$filename"; then
    echo "[SKIP] $filename (已存在)" | tee -a "$SYNC_LOG"
    return 0
  fi
  
  # 上传
  echo "[UPLOAD] $filename" | tee -a "$SYNC_LOG"
  lark-cli drive +upload \
    --file "$local_file" \
    --folder-token "$folder_token" \
    --name "$filename" \
    --as $AS 2>/dev/null
  
  sleep 0.3
}

# 递归同步目录
sync_directory() {
  local local_dir="$1"
  local remote_token="$2"
  local dir_name=$(basename "$local_dir")
  
  echo "同步目录: $dir_name -> $remote_token"
  
  # 遍历本地文件
  for file in "$local_dir"/*; do
    [ -e "$file" ] || continue
    local name=$(basename "$file")
    
    if [ -d "$file" ]; then
      # 子目录：检查飞书是否已有，没有则创建
      sub_token=$(lark-cli drive files list \
        --params "{\"folder_token\":\"$remote_token\"}" \
        --as $AS \
        -q ".data.files[]|select(.name==\"$name\")|.token" 2>/dev/null | head -1)
      
      if [ -z "$sub_token" ]; then
        echo "[CREATE] 文件夹: $name" | tee -a "$SYNC_LOG"
        sub_token=$(lark-cli drive +create-folder \
          --name "$name" \
          --folder-token "$remote_token" \
          --as $AS -q '.data.folder_token' 2>/dev/null | tail -1)
        sleep 0.5
      fi
      
      # 递归处理
      sync_directory "$file" "$sub_token"
      
    elif [ -f "$file" ]; then
      # 文件：检查是否已有，没有则上传
      upload_if_missing "$file" "$remote_token"
    fi
  done
}

# 执行同步
echo "=== 增量同步开始 $(date) ===" | tee "$SYNC_LOG"
sync_directory "./基础设定" "$(get_folder_token '基础设定')"
sync_directory "./skills" "$(get_folder_token 'skills')"
# ... 添加更多目录
echo "=== 增量同步完成 $(date) ===" | tee -a "$SYNC_LOG"
```

### 10.6 双经济原则在飞书操作中的体现

| 场景 | 浪费做法（反面） | 经济做法（正面） |
|------|-----------------|-----------------|
| 文件上传 | 逐个执行lark-cli命令 | 写bash脚本批量执行 |
| 文件夹创建 | 每次都新建 | 先查已有，映射表复用 |
| 全量同步 | 每次都传所有文件 | 先查飞书已有，只传缺失的 |
| 并行操作 | 多个sub-agent同时操作同一目录 | 单一执行者，避免重复 |
| 去重 | 手动逐个检查删除 | 写去重脚本按名称分组清理 |

### 10.7 飞书同步的推荐架构

```
本地workspace
    │
    ├── 飞书文件夹token映射表.md  ← 持久化的token映射
    ├── feishu_incremental_sync.sh ← 增量同步脚本
    └── feishu_dedup.sh            ← 去重清理脚本
    
飞书云空间
    │
    └── 满意扣子项目同步/  ← 根文件夹
        ├── 基础设定/
        ├── skills/
        ├── 对话/
        ├── 满天星光行动/
        ├── 满意解研究所/
        ├── EntroCamp学习笔记/
        ├── 交接/
        ├── 五维决策测评系统/
        ├── 系统/
        ├── 00_核心文档/
        ├── 用户上传/
        ├── MEMORY.md
        ├── SECRET.md
        └── USER.md
```

### 10.8 给后来者的Checklist

批量同步飞书前，按这个清单检查：

- [ ] 是否已写好批量脚本（禁止手动逐个操作）
- [ ] 脚本是否包含"先查再传"逻辑（避免重复）
- [ ] 是否建立了token映射表并持久化
- [ ] 是否只有一个执行者在操作飞书（禁止并行）
- [ ] 是否有Rate Limit保护（sleep间隔）
- [ ] 是否有跳过规则（node_modules等垃圾目录）
- [ ] 是否有错误处理和日志记录
- [ ] 同步完成后是否验证了无重复