> 生成时间: 2026-04-05 08:18+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# case-repository - 案例库管理Skill

## 描述
硬科技合伙人匹配案例库管理系统。支持案例的CRUD管理、多维度标签检索、相似案例推荐、复盘报告生成，并为合伙人匹配引擎提供结构化数据支持。

## 触发条件
- 用户要求"查看案例库"、"添加案例"、"搜索案例"
- 需要生成合伙人匹配的参考案例
- 需要输出复盘报告或相似案例推荐

## 功能
- 案例CRUD：增删改查案例，支持五元组结构化存储（创始人、合伙人、决策框架、结果、判断过程）
- 标签检索：按行业、结果、能力维度、伦理标签等多条件组合搜索
- 相似推荐：基于能力维度和决策风格的 difflib 相似度匹配
- 复盘报告：生成 Markdown 格式的案例复盘与合伙人匹配建议
- 数据导出：支持 JSON 导出，供 partner-matching-engine 调用

## 核心文件
- `scripts/case_repository.py` - 真正实现
- `scripts/main.py` - CLI 入口

## 使用方法
```bash
cd skills/case-repository/scripts
python3 case_repository.py --help
```

## 数据结构
案例会自动附加以下元数据字段之一或多项：
- `industry`（行业）
- `outcome`（结果：success / failure / partial / ongoing / pending）
- `dimensions`（能力维度列表）
- `ethics_tags`（伦理标签）
- `case_patterns`（案例模式）

## 依赖
- Python 3.10+
- 无外部依赖（仅标准库）

## 版本
- 1.0.0-real
- 作者：满意妞（蓝军监督）
