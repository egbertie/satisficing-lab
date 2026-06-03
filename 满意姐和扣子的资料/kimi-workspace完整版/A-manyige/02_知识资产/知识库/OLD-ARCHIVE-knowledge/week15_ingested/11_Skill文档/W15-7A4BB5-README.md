---
# 知识元数据 (5标准化)
knowledge_id: W15-7A4BB5
title: Conversation Researcher - 对话研究专家
category: 11_Skill文档
source: skills/conversation-researcher/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 1548
week: 15
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Conversation Researcher - 对话研究专家

> **知识ID**: W15-7A4BB5  
> **分类**: 11_Skill文档  
> **来源**: `skills/conversation-researcher/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Conversation Researcher - 对话研究专家

**Level 5 Skill** | 多源深度研究 + 7-S标准合规

---

## 快速开始

```bash
# 执行研究
python3 skills/conversation-researcher/scripts/research-runner.py "研究主题"

# 或使用环境变量
export RESEARCH_TOPIC="研究主题"
export RESEARCH_DEPTH="deep"  # shallow/normal/deep
python3 skills/conversation-researcher/scripts/research-runner.py
```

---

## 7-S标准

| 标准 | 名称 | 状态 |
|------|------|------|
| S1 | 输入：研究主题/问题/关键词 | ✅ |
| S2 | 处理：多源搜索→整合→分析 | ✅ |
| S3 | 输出：摘要→发现→引用→建议 | ✅ |
| S4 | 触发：手动执行 | ✅ |
| S5 | 准确性：引用检查 | ✅ |
| S6 | 局限性：时效性/偏见标注 | ✅ |
| S7 | 验证：对抗验证（≥3源） | ✅ |

---

## 文件结构

```
skills/conversation-researcher/
├── SKILL.md                    # 技能定义
├── README.md                   # 本文件
├── cron.json                   # 定时配置
├── config/
│   └── researcher.json         # 研究配置
├── lib/
│   └── research_lib.py         # 共享库
├── scripts/
│   ├── research-runner.py      # 主研究脚本
│   └── self-check.py           # 自检脚本
└── output/                     # 输出目录
    └── research-{timestamp}/
        ├── report.md           # 完整报告
        ├── summary.md          # 执行摘要
        ├── sources.json        # 来源详情
        ├── validation.md       # 验证结果
        └── limitations.md      # 局限性分析
```

---

## 自检

```bash
python3 skills/conversation-researcher/scripts/self-check.py
```

---

## 报告示例

生成的报告包含：
- **执行摘要**: 3-5句核心发现
- **核心发现**: 带可信度评级的研究发现
- **来源引用**: 可追溯的引用列表
- **可执行建议**: 基于研究的行动建议
- **局限性**: 时效性/偏见分析
- **验证结果**: 多源交叉验证详情

---

## 配置

编辑 `config/researcher.json` 调整：
- 最少/最多来源数
- 共识度阈值
- 来源权威性权重

---

*版本: 2.0 | 标准: Level 5 (7-S)*
