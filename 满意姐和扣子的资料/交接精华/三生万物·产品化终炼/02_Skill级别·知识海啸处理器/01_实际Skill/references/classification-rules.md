# 分类规则库

> **编号**: references-02
> **定位**: 智能分类引擎的规则定义和扩展指南
> **版本**: V1.0
> **日期**: 2026-04-25

---

## 一、内置分类规则

### 1.1 核心知识类（core_knowledge）

**定义**: 定义"是什么"和"为什么"的知识，是体系的根基

**关键词**（中文）:
核心、关键、重要、原则、标准、规范、方法论、框架、体系、模型、理论、总结、精华、概要、总纲、导览、指南、基石、本质、原理

**关键词**（英文）:
core, key, important, principle, standard, norm, methodology, framework, system, model, theory, summary, essence, overview, guideline, foundation, essential, principle

**正则模式**:
- `^(\d+_)?(核心|关键|重要)`
- `^(\d+_)?(原则|标准|规范)`
- `^(\d+_)?(总结|概要|overview|summary)`
- `^(\d+_)?(方法论|框架|体系|model|framework)`
- `^(\d+_)?(总纲|导览|index|readme)`

**默认优先级**: P0

**典型文件**:
- `00_总纲.md`
- `01_核心方法论.md`
- `原则与标准.pdf`
- `framework-overview.docx`

---

### 1.2 案例研究类（case_study）

**定义**: 具体的实例、项目、案件，展示"怎么用过"

**关键词**（中文）:
案例、实例、故事、经历、项目、案件、客户、实战、经验、教训、复盘、剖析、诊断、会诊、判例、庭审、交易、并购、纠纷

**关键词**（英文）:
case, example, story, experience, project, client, practice, lesson, review, analysis, diagnosis, consultation, precedent, trial, transaction, merger, dispute

**正则模式**:
- `案例|case study`
- `项目|project`
- `案件|lawsuit`
- `client|客户`

**默认优先级**: P1

**典型文件**:
- `案例一：XXX纠纷.md`
- `项目复盘2024.pdf`
- `client-A项目记录.docx`

---

### 1.3 模板工具类（template_tool）

**定义**: 可直接使用的工具、模板、清单、表格

**关键词**（中文）:
模板、工具、清单、表格、脚本、工具包、模板库、表单、工作表、计算器、生成器、检查表、对照表、速查卡、备忘录

**关键词**（英文）:
template, tool, checklist, form, script, toolkit, worksheet, calculator, generator, checklist, reference card, memo, cheat sheet

**正则模式**:
- `模板|template`
- `工具|tool`
- `清单|checklist`
- `表格|form`

**默认优先级**: P1

**典型文件**:
- `合同模板v2.docx`
- `项目检查清单.md`
- `费用计算表格.xlsx`

---

### 1.4 流程指南类（process_procedure）

**定义**: 描述"怎么做"的步骤、流程、SOP

**关键词**（中文）:
流程、步骤、操作、指南、手册、指引、SOP、程序、规程、教程、怎么做、如何、方法、路径、路线图、操作规范、实施细则

**关键词**（英文）:
process, step, operation, guide, manual, procedure, SOP, tutorial, howto, how to, method, roadmap, protocol, implementation

**正则模式**:
- `流程|process`
- `步骤|step`
- `指南|guide`
- `手册|manual`
- `procedure|process`

**默认优先级**: P1

**典型文件**:
- `诉讼流程指南.md`
- `SOP-合同审查.pdf`
- `如何撰写法律意见书.docx`

---

### 1.5 参考资料类（reference_material）

**定义**: 背景知识、文献、数据，提供上下文

**关键词**（中文）:
参考、资料、文献、文章、论文、报告、调研、数据、法规、判例、条文、解释、注释、附录、 bibliography、背景、历史、综述

**关键词**（英文）:
reference, material, article, paper, report, research, data, regulation, precedent, clause, explanation, note, appendix, bibliography, background, history, review

**正则模式**:
- `参考|reference`
- `资料|material`
- `文献|literature`
- `论文|paper`
- `报告|report`

**默认优先级**: P2

**典型文件**:
- `民法典条文汇总.pdf`
- `2024行业报告.docx`
- `参考文献列表.md`

---

### 1.6 沟通记录类（communication_record）

**定义**: 邮件、会议纪要、讨论记录

**关键词**（中文）:
邮件、会议、讨论、沟通、记录、纪要、聊天、对话、往来、函件、通知、通告、决议、决定、备忘、留言

**关键词**（英文）:
email, meeting, discussion, communication, record, memo, minutes, chat, conversation, correspondence, letter, notice, announcement, resolution, decision, message

**正则模式**:
- `邮件|email`
- `会议|meeting`
- `纪要|minutes`
- `讨论|discussion`

**默认优先级**: P2

**典型文件**:
- `2024-01-15 会议纪要.md`
- `client邮件往来.pdf`
- `团队讨论记录.docx`

---

### 1.7 个人笔记类（personal_note）

**定义**: 个人思考、感悟、随笔、日记

**关键词**（中文）:
笔记、备忘、日记、随想、感想、心得、感悟、随笔、杂记、思考、反思、观察、体会、领悟、灵光、片段、草稿、初稿

**关键词**（英文）:
note, memo, diary, journal, thought, reflection, insight, essay, random, thinking, observation, experience, realization, inspiration, fragment, draft

**正则模式**:
- `笔记|note`
- `备忘|memo`
- `日记|diary`
- `随想|thought`
- `感悟|insight`

**默认优先级**: P2

**典型文件**:
- `工作笔记2024.md`
- `庭审感悟.docx`
- `随想录.pdf`

---

### 1.8 草稿临时类（draft_temporary）

**定义**: 草稿、临时文件、备份、旧版

**关键词**（中文）:
草稿、临时、备份、旧版、历史、废弃、作废、过期、删除、待删、测试、试用、样稿、初稿、修改稿、修订版、副本、复件

**关键词**（英文）:
draft, temp, temporary, backup, old, history, deprecated, obsolete, expired, delete, test, trial, sample, revised, modified, copy, duplicate

**正则模式**:
- `草稿|draft`
- `临时|temp`
- `备份|backup`
- `旧|old`
- `copy|副本`

**默认优先级**: P3

**典型文件**:
- `合同草稿v1.docx`
- `备份_2023旧版`
- `临时笔记.md`

---

## 二、P0/P3强制规则

### 2.1 P0强制规则（高优先级覆盖）

| 规则 | 匹配模式 | 原因 |
|:-----|:---------|:-----|
| 索引文件 | `^(\d+_)?(00_\|01_)` | 编号靠前的通常是核心 |
| 总纲类 | `(README\|INDEX\|总纲\|导览\|overview\|summary)` | 索引/总纲是体系的入口 |
| 核心标记 | `(核心知识\|核心经验\|key knowledge\|core competency)` | 明确标记为核心 |
| 方法论 | `(方法论\|框架\|体系\|model\|framework)` | 方法论是知识体系的骨架 |

### 2.2 P3强制规则（低优先级覆盖）

| 规则 | 匹配模式 | 原因 |
|:-----|:---------|:-----|
| 临时文件 | `(草稿\|draft\|temp\|tmp\|备份\|backup\|旧版\|old)` | 临时/备份文件通常不传承 |
| 副本 | `(copy\|副本\|复件\|修改版\|修订)` | 副本/修改版不是原始文件 |
| 系统临时 | `~\$` | Office等软件的临时文件 |

---

## 三、自定义分类规则

### 3.1 如何添加新分类

编辑 `scripts/smart-triage.py`，在 `CLASSIFICATION_RULES` 中添加：

```python
'your_category': {
    'keywords': ['关键词1', '关键词2', 'keyword1', 'keyword2'],
    'patterns': [r'正则1', r'正则2'],
    'default_priority': 'P1'  # 或 P0/P2/P3
}
```

### 3.2 如何修改优先级

编辑 `scripts/smart-triage.py`，修改对应分类的 `default_priority`。

### 3.3 行业定制

**法律行业定制**:
```python
'legal_precedent': {
    'keywords': ['判例', '判决', '裁定', '裁决', 'precedent', 'judgment', 'ruling', 'verdict'],
    'patterns': [r'判例', r'判决', r'裁决', r'judgment', r'ruling'],
    'default_priority': 'P1'
}
```

**咨询行业定制**:
```python
'consulting_deliverable': {
    'keywords': ['交付物', '建议书', '方案', '报告', 'deliverable', 'proposal', 'solution', 'report'],
    'patterns': [r'交付', r'建议书', r'方案', r'proposal', r'deliverable'],
    'default_priority': 'P1'
}
```

**医疗行业定制**:
```python
'medical_case': {
    'keywords': ['病例', '诊断', '处方', '手术', '治疗', 'case', 'diagnosis', 'prescription', 'surgery', 'treatment'],
    'patterns': [r'病例', r'诊断', r'手术', r'case report', r'diagnosis'],
    'default_priority': 'P0'  # 医疗病例通常是核心
}
```

---

## 四、分类质量优化

### 4.1 提高分类准确率的技巧

1. **规范化文件名**
   - 在导入前，尽量规范化文件名
   - 例如：`草稿.docx` → `合同审查草稿_2024.docx`

2. **使用编号前缀**
   - 核心文件用 `00_`, `01_` 前缀
   - 支撑文件用 `10_`, `11_` 前缀
   - 背景文件用 `90_`, `91_` 前缀

3. **添加类别标签**
   - 在文件名中添加类别标签
   - 例如：`[案例]XXX纠纷_2024.md`, `[模板]合同审查清单.docx`

4. **分层文件夹**
   - 用文件夹结构暗示优先级
   - 例如：`/核心/`, `/支撑/`, `/参考/`, `/归档/`

### 4.2 分类错误处理

**如果发现分类错误**:
1. 在 `03_分类索引.md` 中手动修正
2. 在 `04_P0-P1-P2标记.json` 中修正
3. 记录错误模式，更新分类规则

---

*分类规则库: V1.0*
*来源: 满意解研究所 · 知识海啸处理器*
