> 生成时间: 2026-04-01 14:13+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# Universal Task Executor V3.0 - Knowledge Integration

## 概述

本模块将 `super-knowledge-ingest` Skill 集成到 Universal Task Executor V3.0，实现任务输出的自动知识入库。

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│              Universal Task Executor V3.0                    │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Task 1    │  │   Task 2    │  │   Task N    │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                │
│         └────────────────┼────────────────┘                │
│                          ▼                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Auto Ingestor (auto_ingest.py)          │  │
│  │  - 任务完成自动触发                                  │  │
│  │  - 配置化入库策略                                    │  │
│  │  - 失败自动重试                                      │  │
│  └─────────────────────────┬───────────────────────────┘  │
│                            ▼                               │
│  ┌─────────────────────────────────────────────────────┐  │
│  │            Knowledge Bridge (knowledge_bridge.py)    │  │
│  │  - 统一接口调用super-knowledge-ingest               │  │
│  │  - 批量入库（Token优化）                             │  │
│  │  - 增量更新支持                                      │  │
│  │  - Checkpoint支持                                    │  │
│  └─────────────────────────┬───────────────────────────┘  │
│                            ▼                               │
│  ┌─────────────────────────────────────────────────────┐  │
│  │       super-knowledge-ingest Skill (V6.2)            │  │
│  │  - 9种文件类型支持                                   │  │
│  │  - 5标准实现                                         │  │
│  │  - 19项蓝军测试                                      │  │
│  └─────────────────────────┬───────────────────────────┘  │
│                            ▼                               │
│  ┌─────────────────────────────────────────────────────┐  │
│  │           Knowledge Base (knowledge/ingested-v6)     │  │
│  └─────────────────────────┬───────────────────────────┘  │
│                            ▼                               │
│  ┌─────────────────────────────────────────────────────┐  │
│  │            Index Manager (index_manager.py)          │  │
│  │  - 任务→知识库索引                                   │  │
│  │  - 快速检索                                          │  │
│  │  - 版本管理                                          │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 模块说明

### 1. Knowledge Bridge (`knowledge_bridge.py`)

**职责**: 封装super-knowledge-ingest Skill调用

**核心功能**:
- 单文件入库 (`ingest_file`)
- 批量文件入库 (`ingest_batch`)
- 增量更新（基于校验和）
- Token优化（分批处理）
- Checkpoint支持

**关键类**:
- `KnowledgeBridge`: 主桥接器
- `IngestConfig`: 配置
- `IngestResult`: 单文件入库结果
- `BatchIngestResult`: 批量入库结果

### 2. Auto Ingestor (`auto_ingest.py`)

**职责**: 任务完成时自动触发入库

**核心功能**:
- 任务完成自动触发 (`trigger_on_task_complete`)
- 批次完成触发 (`trigger_on_batch_complete`)
- 多种入库策略（立即/延迟/选择/禁用）
- 失败自动重试（指数退避）
- 入库记录追踪

**关键类**:
- `AutoIngestor`: 自动入库器
- `IngestPolicy`: 入库策略配置
- `IngestRecord`: 入库记录
- `IngestTrigger`: 触发时机枚举
- `IngestStrategy`: 入库策略枚举

### 3. Index Manager (`index_manager.py`)

**职责**: 维护任务与知识库的索引关系

**核心功能**:
- 任务→知识条目映射
- 快速检索（按类型/分类/标签/关键词）
- 版本管理（支持回滚）
- Checkpoint集成

**关键类**:
- `IndexManager`: 索引管理器
- `KnowledgeEntry`: 知识条目
- `IndexVersion`: 索引版本
- `TaskKnowledgeMapping`: 任务知识映射

## 使用示例

### 基础使用

```python
from skills.universal-task-executor-v3.integration import (
    KnowledgeBridge, AutoIngestor, IndexManager
)

# 1. 创建组件
bridge = KnowledgeBridge()
auto_ingest = AutoIngestor(knowledge_bridge=bridge)
index_manager = IndexManager()

# 2. 单文件入库
result = bridge.ingest_file("path/to/file.md")
print(f"Success: {result.success}, Tokens: {result.token_consumed}")

# 3. 批量入库
import asyncio
results = asyncio.run(bridge.ingest_batch(["file1.md", "file2.py"]))
print(f"Success: {results.success_count}/{results.total_files}")
```

### 与TaskEngine集成

```python
from skills.universal-task-executor-v3.core.engine import TaskEngine
from skills.universal-task-executor-v3.integration import AutoIngestor

# 创建引擎和自动入库器
engine = TaskEngine()
auto_ingest = AutoIngestor()

# 注册任务完成回调
async def on_task_complete(task, result):
    await auto_ingest.trigger_on_task_complete(task, result)

# 执行任务
async with engine:
    result = await engine.execute_task(task)
    await on_task_complete(task, result)
```

### 配置化入库策略

```python
from skills.universal-task-executor-v3.integration import (
    IngestPolicy, IngestTrigger, IngestStrategy, AutoIngestor
)

# 创建策略：只处理category_3-6，选择性入库
policy = IngestPolicy(
    trigger=IngestTrigger.TASK_COMPLETE,
    strategy=IngestStrategy.SELECTIVE,
    include_categories=["category_3", "category_4", "category_5", "category_6"],
    exclude_patterns=[".tmp", ".log"],  # 排除临时文件
    max_retries=3,
)

auto_ingest = AutoIngestor(policy=policy)
```

### 检索知识库

```python
from skills.universal-task-executor-v3.integration import IndexManager

index_manager = IndexManager()

# 按任务检索
entries = index_manager.get_entries_by_task("task_123")

# 按关键词搜索
results = index_manager.search(query="checkpoint", file_type="python")

# 获取任务知识摘要
summary = index_manager.get_task_knowledge_summary("task_123")
```

## Token优化策略

### 1. 分批处理

```python
# 大任务自动分批
bridge = KnowledgeBridge(IngestConfig(
    batch_size=10,  # 每批10个文件
    max_tokens_per_batch=50000,  # 每批最多50K tokens
))
```

### 2. 增量更新

```python
# 只处理变更的文件
bridge = KnowledgeBridge(IngestConfig(
    incremental_mode=True,  # 启用增量更新
))

# 第一次：处理全部
result1 = bridge.ingest_file("file.md")  # 处理

# 第二次：文件未变更，跳过
result2 = bridge.ingest_file("file.md")  # 跳过

# 强制重新处理
result3 = bridge.ingest_file("file.md", force=True)  # 强制处理
```

### 3. Token上限控制

```python
policy = IngestPolicy(
    max_tokens_per_auto_ingest=10000,  # 单次自动入库上限
)
```

## Checkpoint支持

### 创建Checkpoint

```python
# 索引Checkpoint
checkpoint_id = index_manager.create_checkpoint()

# 批量入库Checkpoint
async def checkpoint_callback(data):
    print(f"Checkpoint: {data['processed_count']}/{data['total_count']}")

results = await bridge.ingest_batch(files, checkpoint_callback=checkpoint_callback)
```

### 从Checkpoint恢复

```python
# 恢复索引
index_manager.restore_from_checkpoint("idx_cp_20240331120000")

# TaskEngine自动支持从Checkpoint恢复
async with engine:
    result = await engine.resume_from_checkpoint("cp_xxx")
```

## 重要约束

1. **必须通过Skill调用**: 所有知识入库必须通过 `super_knowledge_ingest_v6.2.py`，不能绕过Skill直接操作知识库

2. **Token红线**:
   - 单个文件不超过5K tokens
   - 批量入库不超过50K tokens
   - 单日不超过200K tokens

3. **文件限制**:
   - 最大文件大小: 10MB
   - 支持类型: .md, .py, .json, .sh, .txt, .yaml/.yml, .html, .svg, .log

4. **增量更新**: 基于文件校验和，只处理变更的文件

## 蓝军审计点

- [x] 所有入库通过super-knowledge-ingest Skill
- [x] 支持批量入库和Token优化
- [x] 支持增量更新
- [x] 支持Checkpoint（状态可恢复）
- [x] 不绕过Skill直接操作知识库
