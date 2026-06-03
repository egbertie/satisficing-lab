---
# 知识元数据 (5标准化)
knowledge_id: W11-AB86F9
title: 知识沉淀自动化标准Skill V2.0
category: 11_Skill文档
source: skills/.archive_knowledge-extraction/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 2836
week: 11
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 知识沉淀自动化标准Skill V2.0

> **知识ID**: W11-AB86F9  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_knowledge-extraction/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 知识沉淀自动化标准Skill V2.0
> **5标准**: 全局考虑 ✅ | 系统考虑 ✅ | 迭代机制 ✅ | Skill化 ✅ | 流程自动化 ✅
> 
> 版本: V2.0 | 更新: 2026-03-20 | 核心: 自动萃取+结构化存储

---

## 一、全局考虑（六层+知识生命周期）

### 知识生命周期 × 六层矩阵

| 生命周期 | L0身份 | L1项目 | L2系统 | L3外部 | L4交付 | L5归档 |
|----------|--------|--------|--------|--------|--------|--------|
| **采集** | 学习记录 | 项目笔记 | 日志收集 | 外部信息 | 交付复盘 | 历史归档 |
| **萃取** | 认知提炼 | 方法论提取 | 模式识别 | 洞察生成 | 最佳实践 | 经验总结 |
| **存储** | 知识图谱 | 项目知识库 | 系统文档 | 外部wiki | 交付物 | 归档库 |
| **复用** | 能力应用 | 项目借鉴 | 系统优化 | 外部分享 | 模板复用 | 历史参考 |

---

## 二、系统考虑（采集→萃取→存储→复用闭环）

### 2.1 自动萃取流程

```
对话/任务 → 自动监听 → 知识萃取 → 结构化存储 → 知识图谱更新
                ↑                                       │
                └──────────── 复用反馈 ←─────────────────┘
```

### 2.2 萃取规则

| 知识类型 | 萃取触发 | 存储位置 | 标签 |
|----------|----------|----------|------|
| 决策记录 | 每次决策 | 决策知识库 | #decision |
| 方法论 | 模式识别 | 方法论手册 | #methodology |
| 经验教训 | 失败/成功案例 | 经验库 | #lessons |
| 最佳实践 | 高质量产出 | 实践库 | #best-practice |
| 专家知识 | 专家对话 | 专家档案 | #expert |

---

## 三、迭代机制（每日萃取+每周整合）

### 3.1 每日知识萃取（23:47）

```yaml
daily_extraction:
  time: "23:47"
  scope: "当日所有对话和任务"
  
  steps:
    - scan_conversations: "扫描当日对话"
    - identify_knowledge: "识别知识点"
    - extract_structured: "结构化萃取"
    - update_knowledge_graph: "更新知识图谱"
    - archive_notes: "归档笔记"
```

### 3.2 每周知识整合（周六）

| 整合项 | 动作 | 产出 |
|--------|------|------|
| 知识去重 | 合并相似知识 | 精简知识库 |
| 知识关联 | 建立知识链接 | 知识网络 |
| 知识评估 | 评估知识价值 | 价值排序 |
| 知识归档 | 归档过期知识 | 历史库 |

---

## 四、Skill化（可执行）

### 4.1 自动萃取代码

```python
def knowledge_extraction_pipeline():
    """
    知识萃取流水线
    """
    # 1. 采集当日内容
    content = collect_daily_content()
    
    # 2. 知识识别
    knowledge_items = identify_knowledge(content)
    
    # 3. 结构化萃取
    for item in knowledge_items:
        structured = extract_structured(item)
        store_knowledge(structured)
    
    # 4. 更新知识图谱
    update_knowledge_graph(knowledge_items)
    
    # 5. 生成日报
    generate_extraction_report(knowledge_items)

def identify_knowledge(content):
    """识别知识内容"""
    knowledge_types = {
        "decision": r"决定|决策|选择.*因为",
        "methodology": r"方法|方法论|框架|模型",
        "lesson": r"教训|经验|总结|反思",
        "best_practice": r"最佳实践|优秀案例|成功模式"
    }
    
    identified = []
    for ktype, pattern in knowledge_types.items():
        matches = re.findall(pattern, content)
        identified.extend([(m, ktype) for m in matches])
    
    return identified
```

---

## 五、流程自动化

### 5.1 定时任务

```json
{
  "jobs": [
    {"name": "daily-knowledge-extraction", "schedule": "47 23 * * *", "enabled": true},
    {"name": "weekly-knowledge-integration", "schedule": "0 11 * * 6", "enabled": true}
  ]
}
```

---

## 六、质量门控

- [x] **全局**: 知识生命周期×六层覆盖
- [x] **系统**: 采集→萃取→存储→复用闭环
- [x] **迭代**: 每日萃取+每周整合
- [x] **Skill化**: 自动识别+结构化萃取
- [x] **自动化**: 定时萃取+自动归档

---

*5标准合规: ✅ 全局 | ✅ 系统 | ✅ 迭代 | ✅ Skill化 | ✅ 自动化*