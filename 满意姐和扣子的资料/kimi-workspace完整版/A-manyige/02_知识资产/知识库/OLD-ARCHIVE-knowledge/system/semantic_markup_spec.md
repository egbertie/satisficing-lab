# 语义标记规范 V1.0

## 概述

轻量级语义标记系统，用于在Markdown文档中标注实体，支持快速检索和知识图谱构建。

## 标记格式

### 基本语法

```markdown
<!-- ENTITY:<类型>:<ID> -->显示文本<!-- /ENTITY -->
```

### 支持的实体类型

| 类型 | ID格式 | 示例 |
|------|--------|------|
| expert | 专家英文名(lower_snake) | liu_honglei |
| methodology | 方法论英文名 | wulu_totem |
| case | 案例代号 | CASE_2024_001 |
| decision | 决策ID | DEC_001 |
| tool | 工具名 | query_script |
| insight | 洞察ID | INS_001 |

### 标记示例

```markdown
<!-- ENTITY:expert:liu_honglei -->黎红雷教授<!-- /ENTITY -->提出了
<!-- ENTITY:methodology:wulu_totem -->五路图腾<!-- /ENTITY -->方法论。

这个案例<!-- ENTITY:case:CASE_2024_001 -->客户A的决策<!-- /ENTITY -->
使用了<!-- ENTITY:methodology:value_purity -->价值纯度评估<!-- /ENTITY -->。
```

## 使用场景

### 1. Working文档中的专家引用

当在决策文档中提及专家时，使用实体标记：

```markdown
针对这个问题，建议咨询 <!-- ENTITY:expert:luo_han -->罗汉教授<!-- /ENTITY -->，
他在<!-- ENTITY:methodology:value_purity -->价值纯度<!-- /ENTITY -->方面有深入研究。
```

### 2. 案例记录中的方法引用

```markdown
本案例使用了以下方法论：
- <!-- ENTITY:methodology:wulu_totem -->五路图腾<!-- /ENTITY -->进行专家匹配
- <!-- ENTITY:methodology:partner_ethics -->合伙人伦理<!-- /ENTITY -->进行伦理评估
```

### 3. 工具输出标记

```markdown
分析由 <!-- ENTITY:tool:ingest_script -->ingest.py<!-- /ENTITY --> 自动生成。
```

## 解析规则

1. **不可嵌套**: 实体标记不能嵌套使用
2. **唯一ID**: 每个实体ID在文档中应唯一
3. **显示文本**: 可以是人可读的中文名，ID必须是英文
4. **可选标记**: 非强制，但在关键实体上建议使用

## 自动化处理

ingest.py脚本会自动识别以下内容并建议添加标记：
- 专家姓名
- 方法论关键词
- 图腾名称

## 向后兼容

未标记的文档仍然有效，标记是增量增强。已有文档可逐步添加标记。
