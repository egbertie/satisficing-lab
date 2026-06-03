> 生成时间: 2026-04-01 14:13+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# Universal Task Executor V3.0 - 数据结构定义

**版本**: 3.0.0  
**用途**: 定义V3.0所有核心数据结构，确保跨组件一致性  
**格式**: JSON Schema + Python Dataclass

---

## 1. 任务相关数据结构

### 1.1 基础任务定义

```python
# structures/task.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
import uuid

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"           # 待处理
    RUNNING = "running"           # 执行中
    PAUSED = "paused"             # 已暂停
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"             # 失败
    SKIPPED = "skipped"           # 已跳过
    DEFERRED = "deferred"         # 已推迟

class TaskPriority(Enum):
    """任务优先级枚举"""
    P0 = "p0"  # 核心 - 必须立即处理
    P1 = "p1"  # 重要 - 当日处理
    P2 = "p2"  # 一般 - 本周处理
    P3 = "p3"  # 低优 - 待安排

@dataclass
class TaskMetadata:
    """任务元数据"""
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    source: Optional[str] = None  # 任务来源
    external_id: Optional[str] = None  # 外部系统ID

@dataclass
class Task:
    """
    任务基础数据结构
    
    这是V3.0最核心的数据结构，所有任务类型都基于此扩展
    """
    # 基础标识
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    category: str  # 任务类型：category_1 ~ category_6
    priority: TaskPriority = TaskPriority.P2
    status: TaskStatus = TaskStatus.PENDING
    
    # 任务内容
    title: str = ""  # 任务标题
    description: Optional[str] = None  # 任务描述
    data: Dict[str, Any] = field(default_factory=dict)  # 任务具体数据
    
    # 执行控制
    handler: Optional[str] = None  # 指定处理器
    timeout: Optional[int] = None  # 超时时间(秒)
    max_retries: int = 3  # 最大重试次数
    retry_count: int = 0  # 当前重试次数
    
    # Token预算
    token_budget: int = 0  # Token预算(0表示使用默认值)
    token_consumed: int = 0  # 已消耗Token
    
    # 执行时间
    scheduled_at: Optional[datetime] = None  # 计划执行时间
    started_at: Optional[datetime] = None  # 实际开始时间
    completed_at: Optional[datetime] = None  # 完成时间
    
    # 元数据
    metadata: TaskMetadata = field(default_factory=TaskMetadata)
    
    # 扩展字段
    extra: Dict[str, Any] = field(default_factory=dict)  # 扩展字段
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "category": self.category,
            "priority": self.priority.value,
            "status": self.status.value,
            "title": self.title,
            "description": self.description,
            "data": self.data,
            "handler": self.handler,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "retry_count": self.retry_count,
            "token_budget": self.token_budget,
            "token_consumed": self.token_consumed,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": {
                "created_at": self.metadata.created_at.isoformat(),
                "created_by": self.metadata.created_by,
                "updated_at": self.metadata.updated_at.isoformat() if self.metadata.updated_at else None,
                "updated_by": self.metadata.updated_by,
                "tags": self.metadata.tags,
                "notes": self.metadata.notes,
                "source": self.metadata.source,
                "external_id": self.metadata.external_id,
            },
            "extra": self.extra,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """从字典创建"""
        metadata_data = data.get("metadata", {})
        metadata = TaskMetadata(
            created_at=datetime.fromisoformat(metadata_data["created_at"]),
            created_by=metadata_data.get("created_by", "system"),
            updated_at=datetime.fromisoformat(metadata_data["updated_at"]) if metadata_data.get("updated_at") else None,
            updated_by=metadata_data.get("updated_by"),
            tags=metadata_data.get("tags", []),
            notes=metadata_data.get("notes"),
            source=metadata_data.get("source"),
            external_id=metadata_data.get("external_id"),
        )
        
        return cls(
            task_id=data["task_id"],
            category=data["category"],
            priority=TaskPriority(data.get("priority", "p2")),
            status=TaskStatus(data.get("status", "pending")),
            title=data.get("title", ""),
            description=data.get("description"),
            data=data.get("data", {}),
            handler=data.get("handler"),
            timeout=data.get("timeout"),
            max_retries=data.get("max_retries", 3),
            retry_count=data.get("retry_count", 0),
            token_budget=data.get("token_budget", 0),
            token_consumed=data.get("token_consumed", 0),
            scheduled_at=datetime.fromisoformat(data["scheduled_at"]) if data.get("scheduled_at") else None,
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            metadata=metadata,
            extra=data.get("extra", {}),
        )
```

### 1.2 任务批次

```python
@dataclass
class TaskBatch:
    """任务批次 - 批量处理单位"""
    batch_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: Optional[str] = None  # 批次名称
    description: Optional[str] = None
    
    # 任务列表
    tasks: List[Task] = field(default_factory=list)
    task_ids: List[str] = field(default_factory=list)  # 仅存储ID（大数据量时）
    
    # 执行控制
    category: Optional[str] = None  # 统一类型
    parallel: bool = True  # 是否并行
    max_concurrency: int = 4  # 最大并发
    
    # Token控制
    token_budget_total: int = 0  # 总预算
    token_consumed_total: int = 0  # 总消耗
    
    # 状态统计
    status_counts: Dict[str, int] = field(default_factory=lambda: {
        "pending": 0, "running": 0, "completed": 0, 
        "failed": 0, "skipped": 0, "deferred": 0
    })
    
    # 时间
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取批次统计"""
        total = len(self.tasks) or len(self.task_ids)
        completed = self.status_counts.get("completed", 0)
        failed = self.status_counts.get("failed", 0)
        
        return {
            "batch_id": self.batch_id,
            "total_tasks": total,
            "completed": completed,
            "failed": failed,
            "success_rate": completed / total if total > 0 else 0,
            "token_consumed": self.token_consumed_total,
            "elapsed_time": (self.completed_at - self.started_at).total_seconds() if self.completed_at and self.started_at else None,
        }
```

---

## 2. Token相关数据结构

### 2.1 Token预算与消耗

```python
@dataclass
class TokenConsumption:
    """Token消耗记录"""
    task_id: str
    tokens: int
    operation: str  # 操作类型
    timestamp: datetime = field(default_factory=datetime.now)
    context: Optional[str] = None  # 上下文信息
    
@dataclass
class TokenBudget:
    """Token预算"""
    total: int  # 总预算
    consumed: int = 0  # 已消耗
    reserved: int = 0  # 保留（用于恢复/报告）
    
    @property
    def available(self) -> int:
        """可用预算"""
        return max(0, self.total - self.consumed - self.reserved)
    
    @property
    def usage_ratio(self) -> float:
        """使用率"""
        if self.total <= 0:
            return 0.0
        return self.consumed / self.total
    
    def can_consume(self, amount: int) -> bool:
        """检查是否可以消费指定数量"""
        return self.available >= amount

@dataclass
class TokenLevelConfig:
    """Token档位配置"""
    level: str  # L1-L5
    threshold_min: float  # 最小阈值(0-1)
    threshold_max: float  # 最大阈值(0-1)
    max_concurrency: int  # 最大并发数
    allowed_priorities: List[str]  # 允许的优先级
    description: str
    
    # 各档位标准配置
    @classmethod
    def default_configs(cls) -> List["TokenLevelConfig"]:
        return [
            cls("L5", 0.7, 1.0, 4, ["p0", "p1", "p2", "p3"], "全速执行"),
            cls("L4", 0.5, 0.7, 2, ["p0", "p1", "p2"], "降频33%"),
            cls("L3", 0.3, 0.5, 1, ["p0", "p1"], "降频50%"),
            cls("L2", 0.15, 0.3, 1, ["p0"], "只处理P0"),
            cls("L1", 0.0, 0.15, 0, [], "暂停等待"),
        ]
```

---

## 3. Checkpoint相关数据结构

### 3.1 Checkpoint核心结构

```python
@dataclass
class Checkpoint:
    """
    检查点数据结构 - 支持暂停/重启
    
    这是V3.0最核心的恢复机制
    """
    checkpoint_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: Optional[str] = None  # 检查点名称
    
    # 关联信息
    task_id: Optional[str] = None  # 单任务检查点
    batch_id: Optional[str] = None  # 批次检查点
    
    # 执行状态
    status: str = "active"  # active/completed/failed
    progress: float = 0.0  # 进度0-1
    
    # 数据快照
    task_data: Optional[Dict[str, Any]] = None  # 任务数据快照
    execution_state: Dict[str, Any] = field(default_factory=dict)  # 执行状态
    handler_state: Optional[Dict[str, Any]] = None  # 处理器私有状态
    
    # Token状态
    token_consumed: int = 0
    token_budget_remaining: int = 0
    
    # 批次状态（如果是批次检查点）
    processed_task_ids: List[str] = field(default_factory=list)
    pending_task_ids: List[str] = field(default_factory=list)
    failed_task_ids: List[str] = field(default_factory=list)
    
    # 版本信息（用于升级兼容）
    version: str = "3.0.0"
    schema_version: int = 1
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None  # 过期时间
    
    # 恢复信息
    resume_count: int = 0  # 恢复次数
    last_resume_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化"""
        return {
            "checkpoint_id": self.checkpoint_id,
            "name": self.name,
            "task_id": self.task_id,
            "batch_id": self.batch_id,
            "status": self.status,
            "progress": self.progress,
            "task_data": self.task_data,
            "execution_state": self.execution_state,
            "handler_state": self.handler_state,
            "token_consumed": self.token_consumed,
            "token_budget_remaining": self.token_budget_remaining,
            "processed_task_ids": self.processed_task_ids,
            "pending_task_ids": self.pending_task_ids,
            "failed_task_ids": self.failed_task_ids,
            "version": self.version,
            "schema_version": self.schema_version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "resume_count": self.resume_count,
            "last_resume_at": self.last_resume_at.isoformat() if self.last_resume_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Checkpoint":
        """反序列化"""
        return cls(
            checkpoint_id=data["checkpoint_id"],
            name=data.get("name"),
            task_id=data.get("task_id"),
            batch_id=data.get("batch_id"),
            status=data.get("status", "active"),
            progress=data.get("progress", 0.0),
            task_data=data.get("task_data"),
            execution_state=data.get("execution_state", {}),
            handler_state=data.get("handler_state"),
            token_consumed=data.get("token_consumed", 0),
            token_budget_remaining=data.get("token_budget_remaining", 0),
            processed_task_ids=data.get("processed_task_ids", []),
            pending_task_ids=data.get("pending_task_ids", []),
            failed_task_ids=data.get("failed_task_ids", []),
            version=data.get("version", "3.0.0"),
            schema_version=data.get("schema_version", 1),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            resume_count=data.get("resume_count", 0),
            last_resume_at=datetime.fromisoformat(data["last_resume_at"]) if data.get("last_resume_at") else None,
        )
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at
    
    def is_resumable(self) -> bool:
        """检查是否可恢复"""
        return (
            self.status in ["active", "paused"] and
            not self.is_expired() and
            len(self.pending_task_ids) > 0
        )
```

### 3.2 Checkpoint索引

```python
@dataclass
class CheckpointIndex:
    """检查点索引 - 快速查找"""
    index_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # 索引映射
    by_task: Dict[str, str] = field(default_factory=dict)  # task_id -> checkpoint_id
    by_batch: Dict[str, List[str]] = field(default_factory=dict)  # batch_id -> checkpoint_ids
    by_status: Dict[str, List[str]] = field(default_factory=dict)  # status -> checkpoint_ids
    
    # 统计
    total_checkpoints: int = 0
    active_count: int = 0
    completed_count: int = 0
    expired_count: int = 0
    
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_checkpoint(self, cp: Checkpoint):
        """添加检查点到索引"""
        if cp.task_id:
            self.by_task[cp.task_id] = cp.checkpoint_id
        if cp.batch_id:
            if cp.batch_id not in self.by_batch:
                self.by_batch[cp.batch_id] = []
            self.by_batch[cp.batch_id].append(cp.checkpoint_id)
        if cp.status not in self.by_status:
            self.by_status[cp.status] = []
        self.by_status[cp.status].append(cp.checkpoint_id)
        
        self.total_checkpoints += 1
        self.updated_at = datetime.now()
```

---

## 4. 审计相关数据结构

### 4.1 审计记录

```python
@dataclass
class AuditRecord:
    """审计记录"""
    audit_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # 关联
    task_id: Optional[str] = None
    batch_id: Optional[str] = None
    checkpoint_id: Optional[str] = None
    
    # 审计信息
    auditor: str  # 审计者标识
    audit_type: str  # 类型：self/blue_army/auto
    
    # 审计内容
    criteria: List[str] = field(default_factory=list)  # 审计标准
    findings: List[Dict[str, Any]] = field(default_factory=list)  # 发现
    severity: str = "info"  # info/warning/critical
    
    # 结果
    passed: bool = False
    issues: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # 时间
    audited_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    
    def add_finding(self, item: str, expected: Any, actual: Any, severity: str = "info"):
        """添加审计发现"""
        self.findings.append({
            "item": item,
            "expected": expected,
            "actual": actual,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
        })
        if severity == "critical":
            self.severity = "critical"
        elif severity == "warning" and self.severity == "info":
            self.severity = "warning"
```

### 4.2 审计配置

```python
@dataclass
class AuditConfig:
    """审计配置"""
    category: str  # 任务类型
    
    # 审计要求
    self_audit_required: bool = True  # 自检
    blue_army_required: bool = False  # 蓝军审计
    
    # 抽样配置
    sampling_enabled: bool = True
    sampling_rate_p0: float = 1.0  # P0 100%
    sampling_rate_p1: float = 0.2  # P1 20%
    sampling_rate_p2: float = 0.05  # P2 5%
    
    # 审计标准
    criteria: List[str] = field(default_factory=lambda: [
        "file_exists",      # 文件存在
        "syntax_valid",     # 语法正确
        "executable",       # 可执行
        "documented",       # 有文档
        "tested",           # 已测试
    ])
```

---

## 5. 报告相关数据结构

### 5.1 执行报告

```python
@dataclass
class ExecutionReport:
    """执行报告"""
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    report_type: str  # batch/task/summary
    
    # 关联
    task_id: Optional[str] = None
    batch_id: Optional[str] = None
    
    # 执行统计
    total_tasks: int = 0
    completed: int = 0
    failed: int = 0
    skipped: int = 0
    deferred: int = 0
    
    # Token统计
    token_budget: int = 0
    token_consumed: int = 0
    token_efficiency: float = 0.0  # 效率 = 完成任务数 / Token消耗
    
    # 时间统计
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    # 详细结果
    task_results: List[Dict[str, Any]] = field(default_factory=list)
    
    # 审计结果
    audit_summary: Optional[Dict[str, Any]] = None
    
    # 问题与建议
    issues: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # 生成时间
    generated_at: datetime = field(default_factory=datetime.now)
    
    def get_summary(self) -> str:
        """获取摘要"""
        success_rate = self.completed / self.total_tasks if self.total_tasks > 0 else 0
        return f"""
执行报告摘要
============
任务总数: {self.total_tasks}
成功: {self.completed} ({success_rate*100:.1f}%)
失败: {self.failed}
跳过: {self.skipped}
Token消耗: {self.token_consumed:,} / {self.token_budget:,}
耗时: {self.duration_seconds:.1f}秒
生成时间: {self.generated_at.strftime("%Y-%m-%d %H:%M:%S")}
        """.strip()
```

---

## 6. 处理器相关数据结构

### 6.1 处理器定义

```python
@dataclass
class HandlerInfo:
    """处理器信息"""
    handler_id: str
    name: str
    version: str
    supported_categories: List[str]
    
    # 能力
    supports_parallel: bool = True
    supports_checkpoint: bool = True
    supports_resume: bool = True
    
    # 成本估算
    avg_token_cost: int = 1000  # 平均Token成本
    avg_time_cost: float = 1.0  # 平均时间成本(秒)
    
    # 元数据
    description: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[datetime] = None
    
@dataclass
class HandlerRegistration:
    """处理器注册信息"""
    handler_info: HandlerInfo
    module_path: str  # 模块路径
    class_name: str  # 类名
    config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
```

---

## 7. 配置相关数据结构

### 7.1 执行器配置

```python
@dataclass
class ExecutorConfig:
    """执行器配置"""
    # 基础
    name: str = "universal-task-executor-v3"
    version: str = "3.0.0"
    
    # Token配置
    token_default_budget: int = 100000
    token_reserve_ratio: float = 0.1
    token_alert_thresholds: List[float] = field(default_factory=lambda: [0.7, 0.5, 0.3, 0.15])
    
    # Checkpoint配置
    checkpoint_enabled: bool = True
    checkpoint_default_interval: int = 5
    checkpoint_storage: str = "file"  # file/redis/database
    checkpoint_path: str = "memory/checkpoints/"
    checkpoint_ttl_days: int = 30  # 检查点保留天数
    
    # 执行配置
    max_concurrency: int = 4
    default_timeout: int = 300  # 默认超时5分钟
    max_retries: int = 3
    
    # 处理器配置
    handler_auto_discover: bool = True
    handler_preload: List[str] = field(default_factory=list)
    
    # 升级配置
    upgrade_auto_check: bool = True
    upgrade_hot_reload: bool = True
    upgrade_rollback_on_failure: bool = True
    
    # 审计配置
    audit_blue_army_categories: List[str] = field(default_factory=lambda: ["category_6"])
    audit_sampling_rate: float = 0.2
    
    # 日志配置
    log_level: str = "INFO"
    log_format: str = "json"
    log_output: str = "logs/executor.log"
    
    @classmethod
    def from_yaml(cls, path: str) -> "ExecutorConfig":
        """从YAML加载配置"""
        import yaml
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data.get("executor", {}))
    
    def to_yaml(self, path: str):
        """保存为YAML"""
        import yaml
        data = {"executor": self.to_dict()}
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "token_default_budget": self.token_default_budget,
            "token_reserve_ratio": self.token_reserve_ratio,
            "checkpoint_enabled": self.checkpoint_enabled,
            "checkpoint_default_interval": self.checkpoint_default_interval,
            "max_concurrency": self.max_concurrency,
        }
```

---

## 8. JSON Schema定义

### 8.1 Task JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Task",
  "type": "object",
  "required": ["task_id", "category"],
  "properties": {
    "task_id": {
      "type": "string",
      "description": "任务唯一标识"
    },
    "category": {
      "type": "string",
      "enum": ["category_1", "category_2", "category_3", "category_4", "category_5", "category_6"],
      "description": "任务类型"
    },
    "priority": {
      "type": "string",
      "enum": ["p0", "p1", "p2", "p3"],
      "default": "p2"
    },
    "status": {
      "type": "string",
      "enum": ["pending", "running", "paused", "completed", "failed", "skipped", "deferred"],
      "default": "pending"
    },
    "title": {
      "type": "string"
    },
    "description": {
      "type": "string"
    },
    "data": {
      "type": "object"
    },
    "token_budget": {
      "type": "integer",
      "minimum": 0,
      "default": 0
    },
    "token_consumed": {
      "type": "integer",
      "minimum": 0,
      "default": 0
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "extra": {
      "type": "object"
    }
  }
}
```

### 8.2 Checkpoint JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Checkpoint",
  "type": "object",
  "required": ["checkpoint_id", "version", "schema_version"],
  "properties": {
    "checkpoint_id": {
      "type": "string"
    },
    "task_id": {
      "type": ["string", "null"]
    },
    "batch_id": {
      "type": ["string", "null"]
    },
    "status": {
      "type": "string",
      "enum": ["active", "completed", "failed"]
    },
    "progress": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "execution_state": {
      "type": "object"
    },
    "token_consumed": {
      "type": "integer"
    },
    "version": {
      "type": "string"
    },
    "schema_version": {
      "type": "integer"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "expires_at": {
      "type": ["string", "null"],
      "format": "date-time"
    }
  }
}
```

---

## 9. 数据关系图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            数据关系图                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────┐         1:N          ┌──────────┐                           │
│   │  Task    │◄────────────────────►│Checkpoint│                           │
│   │          │                      │          │                           │
│   │- task_id │         N:1          │- task_id │                           │
│   │- category│◄────────────────────►│- batch_id │                          │
│   │- priority│                      │- progress│                           │
│   │- data    │                      │- state   │                           │
│   └────┬─────┘                      └────┬─────┘                           │
│        │                                  │                                 │
│        │ N:1                             │ 1:1                             │
│        ▼                                  ▼                                 │
│   ┌──────────┐                      ┌──────────┐                           │
│   │TaskBatch │                      │AuditRecord│                          │
│   │          │                      │          │                           │
│   │- batch_id│                      │- audit_id│                           │
│   │- tasks[] │                      │- passed  │                           │
│   │- status  │                      │- findings│                           │
│   └──────────┘                      └──────────┘                           │
│        │                                                                     │
│        │ 1:1                                                                 │
│        ▼                                                                     │
│   ┌──────────┐                                                               │
│   │Execution │                                                               │
│   │  Report  │                                                               │
│   │          │                                                               │
│   │- summary │                                                               │
│   │- stats   │                                                               │
│   └──────────┘                                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**数据结构定义完成** | 2026-03-31 | V3.0.0
