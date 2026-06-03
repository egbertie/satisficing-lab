---
knowledge_id: W1-6D3062
title: SKL-SKILL-v1.0-FIN-260327-Knowledge-Ingestion.md
category: 11_Skill文档
source: skills/knowledge-ingestion/SKILL.md
ingested_at: 2026-03-27T17:44:51.287852
word_count: 3379
---

# SKL-SKILL-v1.0-FIN-260327-Knowledge-Ingestion.md

**知识ID**: W1-6D3062  
**分类**: 11_Skill文档  
**原始路径**: skills/knowledge-ingestion/SKILL.md

---

# SKL-SKILL-v1.0-FIN-260327-Knowledge-Ingestion.md
# 知识入库5标准流程

> **命名空间**: SKL-SKILL-v1.0-FIN-260327-Knowledge-Ingestion  
> **功能**: 所有知识资产标准化入库  
> **原则**: 未经入库的知识不得进入工作流  

---

## 一、知识入库红线（强制）

```
┌─────────────────────────────────────────────────────────────┐
│                    🚫 知识入库红线                            │
├─────────────────────────────────────────────────────────────┤
│ 1. 任何文档必须先入库，才能被引用或处理                       │
│ 2. 入库前必须经过格式标准化（统一为MD）                       │
│ 3. 入库必须经过分类标记和元数据标注                           │
│ 4. 入库后必须在知识库索引中可检索                             │
│ 5. 原始文件保留，知识库为工作副本                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、5标准入库流程

### S1: 全局考虑 - 知识资产全景

**知识来源全覆盖：**
| 来源类型 | 示例 | 入库方式 |
|----------|------|----------|
| 用户上传 | DOCX, PDF, 图片 | 自动转换→MD入库 |
| 网络获取 | 网页, 文章 | 抓取→MD入库 |
| 对话生成 | 研究报告, 分析 | 直接MD入库 |
| 系统输出 | 脚本, 配置 | 复制→MD入库 |
| 外部链接 | 飞书文档, 外部资源 | 链接+摘要入库 |

### S2: 系统闭环 - 入库流程

```
知识输入 → 格式检测 → 标准化转换 → 分类标记 → 元数据标注 → 入库索引 → 完成确认
    │          │           │            │            │           │          │
    │          │           │            │            │           │          └── 蓝军审计
    │          │           │            │            │           └────────── 生成索引
    │          │           │            │            └────────────────────── 提取元数据
    │          │           │            └────────────────────────────────── 自动分类
    │          │           └─────────────────────────────────────────────── 转换为MD
    │          └──────────────────────────────────────────────────────────── 识别格式
    └─────────────────────────────────────────────────────────────────────── 接收知识
```

### S3: 可观测输出 - 入库标准

**元数据标准：**
```yaml
knowledge_entry:
  source: "原始文件路径或URL"
  source_type: "docx|pdf|web|conversation|script|link"
  converted: true/false
  converted_at: "ISO8601时间"
  converter: "工具名称"
  category: "分类路径"
  tags: ["标签1", "标签2"]
  size_kb: 123
  checksum: "md5校验"
  indexed: true/false
```

### S4: 自动化集成

**入库脚本矩阵：**
| 脚本 | 功能 | 触发方式 |
|------|------|----------|
| `knowledge-ingest.sh` | 主入库流程 | 手动/定时 |
| `auto-convert.sh` | 自动格式转换 | 检测到新文件 |
| `classify-content.py` | 智能分类 | 入库时 |
| `update-index.sh` | 更新知识索引 | 入库后 |
| `ingest-audit.py` | 入库审计 | 每次入库 |

### S5: 自我验证

**入库检查清单：**
- [ ] 文件可读取
- [ ] 转换成功
- [ ] 分类正确
- [ ] 索引已更新
- [ ] 蓝军审计通过

---

## 三、知识库目录结构

```
knowledge/
├── converted_docs/          # 转换后的文档（已完成）
│   ├── 01_研究报告/
│   ├── 02_实施方案/
│   ├── 03_学术根基/
│   └── ...
├── generated/               # AI生成的知识
│   ├── analysis/            # 分析报告
│   ├── synthesis/           # 综合研究
│   └── decisions/           # 决策记录
├── external/                # 外部资源
│   ├── web_clips/           # 网页摘录
│   └── links/               # 链接索引
├── system/                  # 系统知识
│   ├── skills/              # Skill文档
│   ├── configs/             # 配置说明
│   └── procedures/          # 操作流程
└── INDEX.md                 # 全局知识索引
```

---

## 四、入库命令

```bash
# 手动入库单个文件
./scripts/knowledge-ingest.sh /path/to/file.docx

# 批量入库目录
./scripts/knowledge-ingest.sh --batch /path/to/folder/

# 强制重新入库
./scripts/knowledge-ingest.sh --force /path/to/file.docx

# 查看入库状态
./scripts/knowledge-status.sh
```

---

## 五、验收标准

| 标准 | 达成要求 |
|------|----------|
| S1 | 覆盖6种知识来源 |
| S2 | 7步闭环流程 |
| S3 | 8项元数据标准 |
| S4 | 5个自动化脚本 |
| S5 | 5项检查清单 |

---

*知识入库5标准流程 - 未经入库，不得使用*
