---
# 知识元数据 (5标准化)
knowledge_id: W11-90BCD6
title: LangChain助手 Skill
category: 11_Skill文档
source: skills/.archive_langchain-assistant/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1100
week: 11
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# LangChain助手 Skill

> **知识ID**: W11-90BCD6  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_langchain-assistant/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: langchain-assistant
description: 使用LangChain构建AI应用和工作流。头脑加速，智能增强。
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["python3"], "env": ["KIMI_API_KEY"] },
        "emoji": "🧠",
      },
  }

# LangChain助手 Skill

利用LangChain框架构建智能工作流，实现头脑加速。

## 核心能力

### 1. 文档智能处理
- 长文档摘要和问答
- 多文档对比分析
- 知识库检索增强(RAG)

### 2. 自动化工作流
- 定时任务自动化
- 多步骤AI处理流程
- 条件分支和决策

### 3. 智能分析
- 数据模式识别
- 趋势预测
- 异常检测

## 使用场景

### 场景1：EEO经验萃取
```
输入：访谈录音转文本
LangChain处理：
  1. 文本分块
  2. 提取关键洞察
  3. 生成方法论框架
  4. 存储到知识库
输出：结构化经验文档
```

### 场景2：案例研究自动化
```
输入：客户案例资料
LangChain处理：
  1. 案例分类
  2. 成功要素提取
  3. 模式识别
  4. 生成案例库
输出：可复用的案例模板
```

### 场景3：决策支持
```
输入：决策问题+相关数据
LangChain处理：
  1. 数据检索
  2. 多维度分析
  3. 方案生成
  4. 风险评估
输出：决策建议报告
```

## 集成方式

```python
from langchain import OpenAI, LLMChain, PromptTemplate

# 使用Kimi作为LLM
llm = OpenAI(
    api_key=os.getenv("KIMI_API_KEY"),
    base_url="https://api.moonshot.cn/v1",
    model="kimi-k2.5"
)

# 构建工作流
chain = LLMChain(llm=llm, prompt=prompt)
result = chain.run(input_data)
```

## 注意事项

1. 使用Kimi API时遵守Allegretto限额
2. 复杂任务使用本地模型降级
3. 结果保存到GitHub版本控制
