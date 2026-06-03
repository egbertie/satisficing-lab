---
# 知识元数据 (5标准化)
knowledge_id: W4-65C013
title: 飞书 × 企微 快速使用指南
category: 01_研究报告
source: docs/FEISHU_WECOM_QUICKSTART.md
ingested_at: 2026-03-27 17:59:30
word_count: 3504
week: 4
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 飞书 × 企微 快速使用指南

> **知识ID**: W4-65C013  
> **分类**: 01_研究报告  
> **来源**: `docs/FEISHU_WECOM_QUICKSTART.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 飞书 × 企微 快速使用指南

**生成时间**: 2026-03-25  
**状态**: 立即可用

---

## 🚀 5分钟快速开始

### 1. 飞书云盘备份（已就绪）

```bash
# 上传任意文件到飞书云盘
python3 /root/.openclaw/workspace/plugins/feishu_drive_uploader.py upload /path/to/file.pdf

# 查看云盘文件列表
python3 /root/.openclaw/workspace/plugins/feishu_drive_uploader.py list
```

### 2. 企微文档创建

```bash
# 创建新文档
wecom_mcp call doc create_doc '{"doc_type": 3, "doc_name": "满意解方法论"}'

# 编辑文档内容
wecom_mcp call doc edit_doc_content '{"docid": "YOUR_DOC_ID", "content": "# 满意解理论\n\n基于西蒙的满意解理论...", "content_type": 1}'
```

### 3. 企微日程查询

```bash
# 查询未来7天日程
wecom_mcp call schedule get_schedule_list_by_range '{"start_time": "2026-03-25 00:00:00", "end_time": "2026-04-01 23:59:59"}'
```

### 4. 企微待办管理

```bash
# 创建待办
wecom_mcp call todo create_todo '{"content": "完成V1.5百科全书", "remind_time": "2026-03-26 18:00:00"}'

# 查询待办列表
wecom_mcp call todo get_todo_list '{"limit": 10}'
```

---

## 📋 常用场景速查

### 场景1：每日文件备份

```bash
#!/bin/bash
# save as: /root/.openclaw/workspace/scripts/daily_backup.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="/tmp/backup_${DATE}"
mkdir -p ${BACKUP_DIR}

# 复制关键文件
cp /root/.openclaw/workspace/MEMORY.md ${BACKUP_DIR}/
cp /root/.openclaw/workspace/USER.md ${BACKUP_DIR}/
cp /root/.openclaw/workspace/SOUL.md ${BACKUP_DIR}/

# 打包
cd /tmp && zip -r backup_${DATE}.zip backup_${DATE}/

# 上传到飞书
python3 /root/.openclaw/workspace/plugins/feishu_drive_uploader.py upload /tmp/backup_${DATE}.zip

# 清理
rm -rf ${BACKUP_DIR} /tmp/backup_${DATE}.zip
```

### 场景2：创建知识库文档

```bash
# 创建满意解方法论文档
wecom_mcp call doc create_doc '{"doc_type": 3, "doc_name": "满意解方法论V1.0"}'

# 获取返回的 docid，然后编辑内容
# docid 格式: doc_xxxxxxxxxxxxxxxx
```

### 场景3：创建智能表格（信息罗盘）

```bash
# 创建案例库表格
wecom_mcp call doc create_doc '{"doc_type": 10, "doc_name": "满意解案例库"}'

# 获取 docid 和默认 sheet_id
wecom_mcp call doc smartsheet_get_sheet '{"docid": "YOUR_DOC_ID"}'

# 添加字段
wecom_mcp call doc smartsheet_add_fields '{
  "docid": "YOUR_DOC_ID",
  "sheet_id": "YOUR_SHEET_ID",
  "fields": [
    {"field_title": "案例编号", "field_type": "FIELD_TYPE_TEXT"},
    {"field_title": "客户类型", "field_type": "FIELD_TYPE_SINGLE_SELECT"},
    {"field_title": "决策方法", "field_type": "FIELD_TYPE_SINGLE_SELECT"},
    {"field_title": "关键洞察", "field_type": "FIELD_TYPE_TEXT"},
    {"field_title": "结果", "field_type": "FIELD_TYPE_SINGLE_SELECT"}
  ]
}'
```

---

## 🔧 工具速查表

### 飞书（当前可用）

| 工具 | 功能 | 状态 |
|------|------|------|
| 云盘上传 | 文件备份 | ✅ 可用 |
| 云盘列表 | 查看文件 | ✅ 可用 |
| 日历 | 日程管理 | ⏳ 待权限 |
| 任务 | 待办管理 | ⏳ 待权限 |
| 知识库 | 文档沉淀 | ⏳ 待权限 |

### 企微（完全可用）

| 类别 | 工具数量 | 功能 |
|------|---------|------|
| 文档 | 15个 | 创建/编辑/查看/智能表格 |
| 日程 | 8个 | 查询/创建/更新/取消/忙闲检查 |
| 待办 | 6个 | 列表/详情/创建/更新/删除/状态变更 |
| 通讯录 | 1个 | 成员列表 |

---

## 📁 关键文件位置

| 文件 | 路径 | 说明 |
|------|------|------|
| 飞书上传器 | `/root/.openclaw/workspace/plugins/feishu_drive_uploader.py` | 命令行工具 |
| 完整规划 | `/root/.openclaw/workspace/docs/FEISHU_WECOM_INTEGRATION_PLAN.md` | 详细方案 |
| 权限检查 | `/tmp/openclaw/feishu_permission_checker.py` | 检查权限状态 |

---

## 💡 使用原则（重要）

1. **当前页面 = 主对话场所**
   - 日常对话在此进行
   - 飞书/企微只接收各自通道消息
   - 减少跨通道Token浪费

2. **文档双备份**
   - 重要文档 → 飞书云盘 + 企微文档
   - 大文件 → 飞书云盘（自动压缩）

3. **管理功能优先用企微**
   - 日程管理 → 企微（功能完整）
   - 待办任务 → 企微（功能完整）
   - 知识库 → 企微文档（成熟稳定）

4. **未来增强等飞书权限**
   - 日历权限开通 → 日程双通道
   - 任务权限开通 → 任务双通道
   - 知识库权限开通 → 飞书知识库

---

## 🎯 下一步行动

### 今天（立即执行）
- [ ] 测试企微文档创建
- [ ] 创建第一个知识库文档
- [ ] 配置每日自动备份cron

### 本周
- [ ] 建立企微文档空间结构
- [ ] 创建案例库智能表格
- [ ] 配置晨间日报自动生成

### 未来（权限开通后）
- [ ] 飞书日历/任务同步
- [ ] 飞书知识库建设
- [ ] 全功能双通道备份

---

*快速开始指南 - 版本 1.0*
