---
title: Skill使用优先机制
type: 核心执行机制
version: V1.0
status: 新增（2026-04-17强化）
created: 2026-04-17
updated: 2026-04-17
source: 结合GoS文章洞察
---

# Skill使用优先机制

> **核心原则**: 先检查skill，禁止直接写代码  
> **来源**: Egbertie反复强调 + Graph of Skills文章洞察

---

## 一、机制定义

### 1.1 为什么需要这个机制？

**现状问题**:
- 我们有119个skill，已进入"规模诅咒"区间
- 刚才（2026-04-17）用Python提取DOCX，未用`doc-converter` skill
- 惯性思维导致重复造轮子

**GoS文章洞察**:
- 当Skill库从几十个膨胀到几千个时，Agent最先失去的是"找对Skill"的能力
- 向量检索只能找到语义相似的高层skill，遗漏底层依赖
- 需要建立skill的**依赖关系图谱**

### 1.2 核心规则

1. **先检查**: 执行`openclaw skills list | grep 关键词`
2. **找到即用**: 如果找到skill，直接使用
3. **找不到才造**: 如果没找到，才考虑自己写代码
4. **记录学习**: 每次使用skill后，记录到`memory/skill-usage-log.json`

---

## 二、执行检查清单

### 2.1 任务启动时

- [ ] 明确任务类型（文件处理/信息获取/内容生成/沟通协作）
- [ ] 执行`openclaw skills list | grep 关键词`
- [ ] 查看是否有匹配的skill

### 2.2 找到Skill后

- [ ] 阅读skill的SKILL.md了解用法
- [ ] 使用skill完成任务
- [ ] 记录使用结果到`memory/skill-usage-log.json`

### 2.3 未找到Skill后

- [ ] 确认是否真的需要自定义代码
- [ ] 评估是否值得创建新skill
- [ ] 写代码前向Egbertie确认
- [ ] 记录"该有但没有"的skill缺口

---

## 三、常见任务Skill速查表

| 任务场景 | 推荐Skill | 命令/用法 |
|:---------|:----------|:----------|
| **提取DOCX/PDF** | doc-converter | `markitdown file.docx` |
| **读微信公众号** | readgzh | 需配置API key |
| **网页内容提取** | kimi_fetch / web_fetch | 内置工具 |
| **生成图片** | canvas | `canvas action=snapshot` |
| **搜索信息** | kimi_search / web_search | 内置工具 |
| **文件操作** | feishu_drive_file | 飞书云盘操作 |
| **日历管理** | feishu_calendar_event | 飞书日程管理 |
| **任务管理** | feishu_task_task | 飞书任务管理 |

---

## 四、Skill依赖图谱（规划中）

```yaml
# skill-dependency-graph.yaml（待建立）
doc-extraction:
  name: "文档内容提取"
  primary: doc-converter      # 优先
  fallback: python-docx       # 备选
  
web-content:
  name: "网页内容获取"
  primary: kimi_fetch         # 优先（已集成）
  fallback: web_fetch         # 备选
  
image-generation:
  name: "图片生成"
  primary: canvas             # 优先（OpenClaw原生）
  fallback: python-pillow     # 备选
```

**执行状态**: 🔄 2026-04-18前完成

---

## 五、Skill使用记忆

### 5.1 记录格式

`memory/skill-usage-log.json`:
```json
{
  "usage_history": [
    {
      "timestamp": "2026-04-17T12:00:00+08:00",
      "task": "提取DOCX文档内容",
      "skill_used": "python-docx",
      "skill_should_use": "doc-converter",
      "result": "success_but_suboptimal",
      "lesson": "应该先检查doc-converter skill"
    }
  ],
  "skill_proficiency": {
    "doc-converter": {"used": 0, "success": 0},
    "readgzh": {"used": 15, "success": 15}
  }
}
```

### 5.2 每周分析

- 哪些skill"该用没用"？
- 哪些skill使用频率最高？
- 哪些skill需要强化学习？

---

## 六、违反案例库

### 案例1：DOCX提取（2026-04-17）

**违反行为**: 直接写Python代码用`python-docx`提取DOCX

**应该使用**: `doc-converter` skill

**检查缺失**: 
- [ ] 未执行`openclaw skills list | grep docx`
- [ ] 未检查是否有现成的skill

**后果**: Token消耗增加30-50%，路径不优雅

**教训**: 每次任务启动时，先检查skill列表

---

## 七、相关机制

- [双经济执行机制](03-双经济执行机制.md) — Skill使用优先是双经济的技术实现路径
- [机制优化建议](10-基于外部文章洞察的机制优化建议.md) — GoS文章详细洞察

---

**蓝军审计**: 本机制为2026-04-17新增，需持续强化执行 🟡  
**满意姐确认**: 已记录违反案例，立即建立Skill使用记忆 🟢  
**下次审计**: 2026-04-24
