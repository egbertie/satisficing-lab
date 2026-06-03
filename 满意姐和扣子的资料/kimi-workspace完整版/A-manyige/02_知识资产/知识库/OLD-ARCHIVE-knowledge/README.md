# 满意解知识管理系统 V2.0

> 对标McKinsey/Palantir/Notion的知识管理体系

## 系统架构

### 五层目录结构

```
knowledge/
├── ontology/                    # 第四层：知识本体
│   ├── core.yaml               # 核心定义 (实体、关系、命名空间)
│   ├── entities/               # 实体实例
│   └── relations/              # 关系实例
│
├── data/                        # 第三层：结构化数据
│   ├── experts/                # 专家档案 (YAML)
│   ├── cases/                  # 案例库
│   ├── decisions/              # 决策记录
│   └── tools/                  # 工具配置
│
├── raw/                         # 第二层：原始数据
│   ├── documents/              # 上传的文档
│   ├── media/                  # 录音、视频
│   └── imports/                # 外部导入
│
├── processed/                   # 处理后信息
│   ├── summaries/              # 摘要
│   ├── extracts/               # 提取的关键信息
│   └── linked/                 # 已建立链接的内容
│
├── insights/                    # 第五层：智慧沉淀
│   ├── patterns/               # 模式识别
│   ├── frameworks/             # 决策框架
│   └── recommendations/        # 可复用建议
│
└── system/                      # 系统层
    ├── scripts/                # 自动化脚本
    ├── templates/              # 模板
    └── index.md                # 全局索引
```

## 核心概念

### 五路图腾

| 图腾 | 元素 | 核心能力 | 专家 |
|------|------|----------|------|
| LIU | 火 | 价值纯度 | 罗汉 |
| SIMON | 土 | 理性框架 | 谢宝剑 |
| GUANYIN | 金 | 极限测试 | 李泽湘 |
| CONFUCIUS | 木 | 合伙人伦理 | 黎红雷 |
| HUINENG | 水 | 压力管理 | 方翊沣 |

### 决策维度

1. **价值纯度** (LIU/火) - 罗汉教授
2. **理性框架** (SIMON/土) - 谢宝剑研究员
3. **压力管理** (HUINENG/水) - 方翊沣博士
4. **合伙人伦理** (CONFUCIUS/木) - 黎红雷教授
5. **极限测试** (GUANYIN/金) - 李泽湘教授

## 使用方法

### 1. 查询专家信息

```bash
# 列出所有专家
cd knowledge/system/scripts
python3 query.py experts

# 按图腾查询
python3 query.py totem LIU

# 按状态查询
python3 query.py status 已确认

# 全文搜索
python3 query.py search 压力
```

### 2. 处理新文档

```bash
# 将文档摄入知识库
python3 ingest.py /path/to/document.md

# 这会生成摘要和提取的实体信息
```

### 3. 验证数据一致性

```bash
# 运行一致性检查
python3 validate.py

# 查看验证报告
cat ../validation_report.md
```

### 4. 同步Working文档

```bash
# 从YAML数据自动生成Working文档
python3 sync.py

# 这会更新:
# - /root/.openclaw/workspace/Working_专家层.md
# - /root/.openclaw/workspace/Working_五路图腾.md
```

### 5. 生成全局索引

```bash
# 更新系统索引
python3 index.py

# 查看索引
cat ../index.md
```

## 语义标记

在Markdown文档中使用特殊注释标记实体：

```markdown
<!-- ENTITY:expert:liu_honglei -->黎红雷教授<!-- /ENTITY -->
<!-- ENTITY:methodology:wulu_totem -->五路图腾<!-- /ENTITY -->
```

详见: `system/semantic_markup_spec.md`

## 当前数据

- **专家**: 6位
  - 黎红雷 (CONFUCIUS) - 儒商哲学
  - 罗汉 (LIU) - 数字化转型
  - 谢宝剑 (SIMON) - 决策科学
  - 李泽湘 (GUANYIN) - 硬科技创业
  - 方翊沣 (HUINENG) - 心理学
  - 陈国祥 - 家族企业治理

- **案例**: 待添加
- **方法论**: 5个核心方法论

## 记忆分层

```
memory/
├── working/           # 工作记忆（当前会话）
├── short_term/        # 短期记忆（今日）
├── long_term/         # 长期记忆
│   ├── core/          # 核心身份
│   ├── projects/      # 项目历史
│   └── decisions/     # 关键决策
└── archive/           # 归档记忆
```

## Token效率原则

1. **结构化存储优先**: YAML/JSON比Markdown更省Token
2. **增量更新**: 只处理变更部分
3. **预计算缓存**: 索引、统计提前生成
4. **惰性加载**: 按需加载，不预读全文

## 自动化脚本

| 脚本 | 功能 |
|------|------|
| `ingest.py` | 知识摄入管道，自动解析文档 |
| `validate.py` | 一致性检查，生成报告 |
| `sync.py` | 同步数据到Working文档 |
| `index.py` | 生成全局索引 |
| `query.py` | 快速检索 |

## 状态

- ✅ Phase 1: 基础设施重建 完成
- ✅ Phase 2: 自动化管道 完成
- ✅ Phase 3: 智能增强 完成

## 下一步建议

1. **添加案例数据**: 在 `data/cases/` 目录下创建YAML格式的案例
2. **扩展专家信息**: 补充联系方式、背景等详细信息
3. **处理现有文档**: 使用 `ingest.py` 处理历史文档
4. **建立关系网络**: 在 `ontology/relations/` 中定义专家-方法论-案例关系
5. **训练AI识别**: 优化实体提取规则，提高自动化程度

## 维护者

- 系统维护: Egbertie
- 最后更新: 2026-03-19
- 版本: 2.0
