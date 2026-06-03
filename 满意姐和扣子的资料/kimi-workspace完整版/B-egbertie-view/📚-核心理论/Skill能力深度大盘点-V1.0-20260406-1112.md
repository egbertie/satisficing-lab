---
kia-version: 1.0
tier: T1
title: Skill能力深度大盘点报告
source: B-egbertie-view/📚-核心理论/Skill能力深度大盘点-V1.0-20260406-1112.md
ingested: 2026-04-16
tags: [auto-kia, b-view-research, BatchE]
---

> 生成时间: 2026-04-03 09:17+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# Skill能力深度大盘点报告

> 盘点时间: 2026-04-03  
> 盘点目的: 避免重复造轮子，建立Skill使用规范，节省Token消耗

---

## 一、已安装的Skill总览

### 1. 飞书生态 Skill (10个)

| Skill名称 | 核心功能 | 触发条件 | 工具函数 |
|-----------|----------|----------|----------|
| **feishu-fetch-doc** | 读取飞书云文档内容，返回Markdown | 需要获取飞书文档内容时 | `feishu_fetch_doc` |
| **feishu-create-doc** | 创建飞书云文档，支持丰富格式 | 需要创建新文档时 | `feishu_create_doc` |
| **feishu-update-doc** | 更新现有飞书文档(追加/覆盖/替换) | 需要修改已有文档时 | `feishu_update_doc` |
| **feishu-bitable** | 操作飞书多维表格(增删改查记录) | 涉及"多维表格"、"bitable"、"数据表" | `feishu_bitable_app_table_record` 等 |
| **feishu-calendar** | 飞书日历与日程管理 | 查看日程、创建会议、约会议 | `feishu_calendar_event` 等 |
| **feishu-task** | 飞书任务管理(创建、查询、更新) | 提到"任务"、"待办"、"to-do"、"清单" | `feishu_task_task` 等 |
| **feishu-im-read** | 飞书IM消息读取(历史消息、搜索) | 需要获取聊天记录、搜索消息 | `feishu_im_user_get_messages` 等 |
| **feishu-channel-rules** | 飞书通道输出规则 | 始终在飞书对话中激活 | - |
| **feishu-troubleshoot** | 飞书插件问题排查 | 遇到授权/连接问题 | `feishu_oauth` 等 |
| **feishu-create-doc/wiki相关** | 知识库节点管理 | 操作Wiki文档 | `feishu_wiki_space_node` |

### 2. 本地文件处理 Skill (7个)

| Skill名称 | 核心功能 | 触发条件 | 使用方式 |
|-----------|----------|----------|----------|
| **file-gateway** | 统一网关上传文件到多渠道 | 需要将本地文件分享到飞书/Notion等 | `file-gateway upload` |
| **md-to-pdf** | Markdown转PDF | 需要生成PDF报告 | `pandoc` 或 Python脚本 |
| **markdown-converter** | 多格式转Markdown(HTML/DOCX) | 需要解析文档内容 | `pandoc` |
| **markdown-exporter** | Markdown导出到多格式 | 需要导出文档 | - |
| **csvtoexcel** | CSV转Excel | 表格格式转换 | - |
| **automate-excel** | Excel自动化操作 | 处理Excel文件 | - |
| **file-integrity** | 文件完整性校验 | 验证文件未被篡改 | - |

### 3. 内容创作 Skill (6个)

| Skill名称 | 核心功能 | 触发条件 |
|-----------|----------|----------|
| **xhs-note-creator** | 小红书笔记素材创作 | 需要创建小红书内容 |
| **copywriting** | 文案创作辅助 | 需要撰写营销文案 |
| **react-email** | 创建HTML邮件模板 | 需要发送邮件 |
| **mermaid-diagrams** | 生成Mermaid图表 | 需要流程图/架构图 |
| **notion-enhanced** | Notion增强操作 | 使用Notion作为知识库 |
| **daily-report** | 生成专业日报PDF | 需要生成日报 |

### 4. 数据与搜索 Skill (6个)

| Skill名称 | 核心功能 | 触发条件 |
|-----------|----------|----------|
| **brave-search** | 网页搜索(Brave API) | 需要搜索网络信息 |
| **tavily-search** | 网页搜索(Tavily API) | Brave不可用时替代 |
| **kimi-search** | 联网搜索(内置) | 实时信息检索 |
| **duckdb-cli-ai-skills** | DuckDB数据库操作 | 数据分析 |
| **rss-ai-reader** | RSS订阅与AI摘要 | 订阅博客/新闻 |
| **stock-assistant** | 股票监控与分析 | 股票相关需求 |

### 5. 系统与自动化 Skill (8个)

| Skill名称 | 核心功能 | 触发条件 |
|-----------|----------|----------|
| **cron-scheduling** | Cron任务调度 | 需要定时任务 |
| **task-manager** | 任务队列管理 | 批量任务处理 |
| **task-queue** | 任务队列系统 | 异步任务处理 |
| **sync-manager** | 文件同步管理 | 多位置同步 |
| **error-handler** | 错误处理机制 | 系统异常处理 |
| **conversation-continuity** | 对话连续性保障 | 长对话管理 |
| **openclaw-token-optimizer** | Token优化 | 节省Token消耗 |
| **token-saver** | Token自动优化 | Token管理 |

### 6. 企业微信 Skill (13个)

| Skill名称 | 核心功能 |
|-----------|----------|
| **wecom-contact-lookup** | 通讯录成员查询 |
| **wecom-doc-manager** | 企业微信文档管理(创建/读取/编辑) |
| **wecom-get-todo-list** | 待办列表查询 |
| **wecom-get-todo-detail** | 待办详情查询 |
| **wecom-edit-todo** | 待办编辑(创建/更新/删除) |
| **wecom-meeting-query** | 会议查询 |
| **wecom-meeting-create** | 会议创建 |
| **wecom-meeting-manage** | 会议管理(取消/更新) |
| **wecom-schedule** | 日程管理 |
| **wecom-msg** | 消息记录拉取与发送 |
| **wecom-send-media** | 发送媒体文件 |
| **wecom-smartsheet-schema** | 智能表格结构管理 |
| **wecom-smartsheet-data** | 智能表格数据管理 |

### 7. 微博 Skill (4个)

| Skill名称 | 核心功能 |
|-----------|----------|
| **weibo-token** | API访问令牌管理 |
| **weibo-hot-search** | 微博热搜榜 |
| **weibo-search** | 微博智搜 |
| **weibo-crowd** | 超话发帖 |

---

## 二、关键Skill使用规范

### 【规范1】读取飞书文档 → 必须使用 feishu-fetch-doc

**❌ 错误做法**: 用Python下载解析docx文件  
**✅ 正确做法**: 直接调用 `feishu_fetch_doc`

```json
{
  "doc_id": "https://xxx.feishu.cn/docx/Z1Fjxxx"  // 支持URL或token
}
```

**返回**: Markdown格式内容，可直接使用

---

### 【规范2】创建飞书文档 → 必须使用 feishu-create-doc

**支持丰富格式**:
- 高亮块(Callout): `<callout emoji="💡" background-color="light-blue">`
- 分栏(Grid): `<grid cols="2">`
- 表格: `<lark-table>`
- Mermaid图表: 自动渲染为画板
- 图片: `<image url="..."/>`

**创建位置选择**:
- `folder_token` → 创建到指定文件夹
- `wiki_node` → 创建到知识库节点
- `wiki_space` → 创建到知识空间根目录

---

### 【规范3】操作多维表格 → 必须使用 feishu-bitable

**标准流程**:
1. 先调用 `feishu_bitable_app_table_field.list` 获取字段类型
2. 根据字段类型构造正确的值格式
3. 调用 `feishu_bitable_app_table_record.batch_create` 批量写入

**关键约束**:
- 人员字段: `[{id: "ou_xxx"}]` (数组对象)
- 日期字段: 毫秒时间戳 (如 `1674206443000`)
- 单选字段: 字符串 `"选项名"`
- 多选字段: 字符串数组 `["选项1", "选项2"]`
- 批量上限: 500条/次

---

### 【规范4】文件上传 → 使用 file-gateway

**一键上传到多渠道**:
```bash
file-gateway upload /path/to/file.md
```

支持渠道: 飞书、Notion、Telegram、邮件

---

### 【规范5】Markdown转PDF → 使用 md-to-pdf

**推荐方式** (支持中文):
```bash
pandoc input.md -o output.pdf --pdf-engine=xelatex -V CJKmainfont="Noto Sans CJK SC"
```

**快速方式** (无需LaTeX):
```bash
python scripts/md2pdf.py input.md output.pdf
```

---

### 【规范6】读取本地文件 → 使用 read 工具

**标准做法**:
```json
{
  "file_path": "/path/to/file.txt",
  "limit": 100,    // 可选，限制行数
  "offset": 1      // 可选，起始行号
}
```

支持: 文本文件、图片(jpg/png/gif/webp)

---

## 三、常见错误避免清单

| 场景 | ❌ 错误做法 | ✅ 正确做法 | 节省Token |
|------|------------|------------|----------|
| 读取飞书文档 | Python下载+解析docx | `feishu_fetch_doc` | ~500 tokens |
| 创建飞书文档 | Python生成后上传 | `feishu_create_doc` | ~800 tokens |
| 批量导入表格 | 逐条调用API | `batch_create` (≤500条/次) | ~70% |
| 文件上传 | 自己实现上传逻辑 | `file-gateway upload` | ~300 tokens |
| PDF生成 | 手动排版 | `pandoc` 或 `md2pdf.py` | ~400 tokens |
| 搜索信息 | 反复浏览网页 | `kimi_search` 或 `web_search` | ~60% |
| 日历操作 | 手动查询 | `feishu_calendar_event` | ~200 tokens |
| 任务管理 | 外部工具 | `feishu_task_task` | ~200 tokens |

---

## 四、Skill快速选择决策树

```
用户需要...
│
├─ 读取飞书文档内容 ──→ feishu-fetch-doc
│
├─ 创建/更新飞书文档 ──→ feishu-create-doc / feishu-update-doc
│
├─ 操作表格数据 ──→ feishu-bitable (多维表格) / feishu_sheet (电子表格)
│
├─ 管理日程会议 ──→ feishu-calendar
│
├─ 管理任务待办 ──→ feishu-task
│
├─ 读取聊天记录 ──→ feishu-im-read
│
├─ 上传文件到多渠道 ──→ file-gateway
│
├─ Markdown转PDF ──→ md-to-pdf
│
├─ 格式转换 ──→ markdown-converter
│
├─ 搜索网络信息 ──→ kimi-search / brave-search
│
├─ 股票数据 ──→ stock-assistant
│
├─ 定时任务 ──→ cron-scheduling
│
└─ 其他 ──→ 查看本报告或询问用户
```

---

## 五、Token节省执行纪律

### 红线规则

1. **先查Skill，后用通用方法**
   - 执行任何任务前，先查看本报告确认是否有对应Skill
   - 有Skill → 必须使用Skill
   - 无Skill → 才考虑Python/Shell等通用方法

2. **批量操作优先**
   - 有 `batch_create` 不用 `create` 循环
   - 有 `batch_update` 不用 `update` 循环
   - 单次上限500条，大数据分批次

3. **避免重复搜索**
   - 同一话题搜索结果缓存到 memory/YYYY-MM-DD.md
   - 引用已有结果，不重复搜索

4. **文档处理标准化**
   - 飞书文档: 用 `feishu_fetch_doc` 读取，用 `feishu_create_doc` 创建
   - 本地文件: 用 `read` 工具读取，用 `write`/`edit` 修改
   - PDF生成: 用 `md-to-pdf` Skill

---

## 六、后续优化建议

1. **建立Skill使用频率监控**
   - 记录每个Skill的使用次数和Token消耗
   - 识别低效使用模式

2. **补充缺失Skill**
   - 如果需要频繁用Python处理某类任务，考虑封装为Skill

3. **定期更新本报告**
   - 新安装Skill时更新本盘点
   - 发现新使用模式时补充最佳实践

---

**报告完成。从此执行: 先查本报告 → 再选Skill → 最后才用通用方法。**
