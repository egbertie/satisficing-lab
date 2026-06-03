> 生成时间: 2026-04-01 14:13+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# Universal Task Executor V3.0 - 架构设计文档

**版本**: 3.0.0  
**设计目标**: 1-6类任务通用、可插拔处理器、Token优化内置、预留升级接口  
**设计时间**: 2026-03-31  
**状态**: 设计稿

---

## 1. 架构核心思想

### 1.1 从V2.0到V3.0的演进

| 维度 | V2.0 (mass-task-executor) | V3.0 (universal-task-executor) |
|------|---------------------------|--------------------------------|
| **适用范围** | 仅第6类（大规模审计任务） | 1-6类任务全通用 |
| **处理器** | 硬编码9步流程 | 可插拔处理器架构 |
| **扩展性** | 修改核心代码 | 插件式扩展 |
| **Token优化** | 外部监控 | 内置优化引擎 |
| **升级机制** | 无 | 预留热升级接口 |

### 1.2 核心设计原则

1. **通用性**: 通过任务类型定义机制，支持任意类型任务
2. **可插拔**: 处理器、检查点、审计器均可替换
3. **Token感知**: 每个操作都考虑Token成本
4. **可恢复**: 任意时刻可暂停，任意时刻可重启
5. **可进化**: 预留升级接口，不停机更新

---

## 2. 整体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Universal Task Executor V3.0                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  API Layer  │  │  CLI Layer  │  │ Event Layer │  │ Cron Layer  │        │
│  │  (REST/Web) │  │  (Command)  │  │  (Webhook)  │  │(Scheduled)  │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         └────────────────┴────────────────┴────────────────┘                │
│                                    │                                        │
│                           ┌────────▼────────┐                               │
│                           │  Task Router    │                               │
│                           │  (任务分发器)    │                               │
│                           └────────┬────────┘                               │
│                                    │                                        │
│  ┌─────────────────────────────────▼─────────────────────────────────────┐ │
│  │                      Core Engine (核心引擎)                            │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐  │ │
│  │  │Task Registry│ │Handler Mgr  │ │Token Engine │ │ Checkpoint Mgr  │  │ │
│  │  │ (任务注册表) │ │(处理器管理) │ │(Token引擎)  │ │  (检查点管理)    │  │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                        │
│  ┌─────────────────────────────────▼─────────────────────────────────────┐ │
│  │                    Plugin System (插件系统)                            │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐  │ │
│  │  │Type 1-6     │ │   Audit     │ │  Storage    │ │   Reporting     │  │ │
│  │  │Handlers     │ │  Plugins    │ │  Plugins    │ │    Plugins      │  │ │
│  │  │(任务处理器)  │ │ (审计插件)  │ │ (存储插件)  │ │   (报告插件)    │  │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                        │
│  ┌─────────────────────────────────▼─────────────────────────────────────┐ │
│  │                  Upgrade Interface (升级接口)                          │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐  │ │
│  │  │Version Mgr  │ │ Hot Reload  │ │ Migration   │ │   Rollback      │  │ │
│  │  │(版本管理)   │ │ (热重载)    │ │ (迁移引擎)  │ │   (回滚机制)     │  │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 任务类型定义（1-6类通用）

### 3.1 六类任务标准定义

```yaml
# config/task_types.yaml
task_types:
  category_1:  # 第1类：治理体系完善
    name: "governance_enhancement"
    display_name: "治理体系完善"
    description: "完善管理规则、检查清单、SOP文档"
    default_handler: "governance_handler"
    priority_weights: { p0: 10, p1: 5, p2: 2 }
    audit_required: true
    checkpoint_interval: 5  # 每5条记录检查点
    
  category_2:  # 第2类：周期性任务部署
    name: "cron_deployment"
    display_name: "周期性任务部署"
    description: "部署和管理Cron定时任务"
    default_handler: "cron_handler"
    priority_weights: { p0: 8, p1: 4, p2: 1 }
    audit_required: true
    checkpoint_interval: 3
    
  category_3:  # 第3类：系统能力建设
    name: "system_building"
    display_name: "系统能力建设"
    description: "构建自动化脚本、监控系统、灾备机制"
    default_handler: "system_handler"
    priority_weights: { p0: 9, p1: 5, p2: 2 }
    audit_required: true
    checkpoint_interval: 1  # 每条记录检查点（系统建设重要）
    
  category_4:  # 第4类：历史数据治理
    name: "data_governance"
    display_name: "历史数据治理"
    description: "清理、整理、归档历史数据"
    default_handler: "data_handler"
    priority_weights: { p0: 6, p1: 4, p2: 2 }
    audit_required: true
    checkpoint_interval: 10
    
  category_5:  # 第5类：杂项清理
    name: "misc_cleanup"
    display_name: "杂项清理"
    description: "清理临时文件、过期配置、待分类项"
    default_handler: "misc_handler"
    priority_weights: { p0: 5, p1: 3, p2: 1 }
    audit_required: false
    checkpoint_interval: 20
    
  category_6:  # 第6类：全量任务审计
    name: "full_audit"
    display_name: "全量任务审计"
    description: "大规模历史任务深度审计（继承V2.0）"
    default_handler: "audit_handler"
    priority_weights: { p0: 10, p1: 6, p2: 3 }
    audit_required: true
    checkpoint_interval: 5
    blue_army_required: true  # 必须蓝军审计
```

### 3.2 任务类型动态注册

```python
# core/task_registry.py
class TaskRegistry:
    """任务类型注册中心 - 支持动态扩展"""
    
    _handlers: Dict[str, TaskHandler] = {}
    _configs: Dict[str, TaskTypeConfig] = {}
    
    @classmethod
    def register(cls, category: str, handler: TaskHandler, config: TaskTypeConfig):
        """注册新任务类型"""
        cls._handlers[category] = handler
        cls._configs[category] = config
        
    @classmethod
    def get_handler(cls, category: str) -> TaskHandler:
        """获取任务处理器"""
        if category not in cls._handlers:
            # 尝试加载插件
            cls._load_plugin(category)
        return cls._handlers.get(category)
    
    @classmethod
    def _load_plugin(cls, category: str):
        """动态加载处理器插件"""
        plugin_path = f"plugins/handlers/{category}_handler.py"
        if os.path.exists(plugin_path):
            # 动态导入并注册
            module = importlib.import_module(f"plugins.handlers.{category}_handler")
            module.register_handler()
```

---

## 4. 可插拔处理器架构

### 4.1 处理器接口定义

```python
# core/handler_interface.py
from abc import ABC, abstractmethod
from typing import Iterator, Optional
from dataclasses import dataclass

@dataclass
class TaskContext:
    """任务执行上下文"""
    task_id: str
    category: str
    priority: str  # p0/p1/p2
    data: Dict[str, Any]
    checkpoint_state: Optional[Dict] = None
    token_budget: int = 0  # Token预算
    start_time: Optional[datetime] = None

@dataclass
class TaskResult:
    """任务执行结果"""
    task_id: str
    status: str  # success/failed/skipped
    output: Dict[str, Any]
    token_consumed: int
    time_elapsed: float
    audit_required: bool = False
    next_action: Optional[str] = None

class TaskHandler(ABC):
    """任务处理器抽象基类 - 所有处理器必须实现"""
    
    @property
    @abstractmethod
    def handler_name(self) -> str:
        """处理器名称"""
        pass
    
    @property
    @abstractmethod
    def supported_categories(self) -> List[str]:
        """支持的任务类型"""
        pass
    
    @abstractmethod
    def validate(self, context: TaskContext) -> bool:
        """验证任务数据是否合法"""
        pass
    
    @abstractmethod
    def execute(self, context: TaskContext) -> Iterator[TaskResult]:
        """
        执行任务
        使用Iterator支持流式处理和Checkpoint恢复
        """
        pass
    
    @abstractmethod
    def estimate_cost(self, context: TaskContext) -> Dict[str, int]:
        """估算Token和时间成本"""
        pass
    
    def on_checkpoint(self, state: Dict) -> None:
        """Checkpoint回调 - 处理器保存状态"""
        pass
    
    def on_resume(self, state: Dict) -> TaskContext:
        """恢复回调 - 从Checkpoint恢复"""
        pass
```

### 4.2 处理器管理器

```python
# core/handler_manager.py
class HandlerManager:
    """处理器管理器 - 管理所有处理器实例"""
    
    def __init__(self):
        self._handlers: Dict[str, TaskHandler] = {}
        self._middlewares: List[Middleware] = []
        
    def register_handler(self, handler: TaskHandler) -> None:
        """注册处理器"""
        for category in handler.supported_categories:
            self._handlers[category] = handler
            
    def add_middleware(self, middleware: Middleware) -> None:
        """添加中间件（审计、日志、Token监控等）"""
        self._middlewares.append(middleware)
        
    async def execute(self, context: TaskContext) -> TaskResult:
        """执行任务（带中间件链）"""
        # 前置中间件
        for mw in self._middlewares:
            context = await mw.before_execute(context)
            
        # 获取处理器
        handler = self._handlers.get(context.category)
        if not handler:
            raise HandlerNotFoundError(f"No handler for category: {context.category}")
            
        # 验证
        if not handler.validate(context):
            raise ValidationError(f"Task validation failed: {context.task_id}")
            
        # 执行
        result = await handler.execute(context)
        
        # 后置中间件
        for mw in reversed(self._middlewares):
            result = await mw.after_execute(context, result)
            
        return result
```

### 4.3 标准处理器实现示例

```python
# handlers/audit_handler.py (第6类处理器 - 继承V2.0)
class AuditHandler(TaskHandler):
    """全量审计处理器 - 实现9步流程"""
    
    @property
    def handler_name(self) -> str:
        return "full_audit_handler"
        
    @property
    def supported_categories(self) -> List[str]:
        return ["category_6"]
    
    def execute(self, context: TaskContext) -> Iterator[TaskResult]:
        """9步流程实现"""
        # Step 1: 分类
        yield self._step1_classify(context)
        
        # Step 2: 建立目录
        yield self._step2_setup_dirs(context)
        
        # Step 3-4: P0/P1审计
        for result in self._step3_audit_p0(context):
            yield result
            
        # Step 5: P2处理
        yield self._step5_process_p2(context)
        
        # Step 5.5: 蓝军审计
        yield self._step5_5_blue_army(context)
        
        # ...后续步骤
```

---

## 5. Token优化引擎（内置）

### 5.1 五级Token档位

```python
# core/token_engine.py
class TokenLevel(Enum):
    """Token优化五级档位"""
    L5_FULL = "full"          # >70% Token - 全速执行
    L4_NORMAL = "normal"      # 50-70% - 降频33%
    L3_THROTTLE = "throttle"  # 30-50% - 降频50%
    L2_CRITICAL = "critical"  # 15-30% - 只处理P0
    L1_HALT = "halt"          # <15% - 暂停等待

@dataclass
class TokenBudget:
    """Token预算管理"""
    total_budget: int
    consumed: int = 0
    reserved: int = 0  # 保留给恢复/报告
    
    @property
    def available(self) -> int:
        return self.total_budget - self.consumed - self.reserved
        
    @property
    def level(self) -> TokenLevel:
        ratio = self.available / self.total_budget
        if ratio > 0.7: return TokenLevel.L5_FULL
        elif ratio > 0.5: return TokenLevel.L4_NORMAL
        elif ratio > 0.3: return TokenLevel.L3_THROTTLE
        elif ratio > 0.15: return TokenLevel.L2_CRITICAL
        else: return TokenLevel.L1_HALT

class TokenEngine:
    """Token优化引擎 - 全局Token管理"""
    
    def __init__(self, total_budget: int):
        self.budget = TokenBudget(total_budget=total_budget, reserved=total_budget//10)
        self._observers: List[Callable] = []
        
    def consume(self, tokens: int, context: str = "") -> TokenLevel:
        """消费Token，返回当前档位"""
        self.budget.consumed += tokens
        level = self.budget.level
        
        # 通知观察者
        for observer in self._observers:
            observer(level, self.budget)
            
        return level
    
    def should_execute(self, category: str, priority: str) -> bool:
        """根据档位判断是否应该执行任务"""
        level = self.budget.level
        
        if level == TokenLevel.L5_FULL:
            return True
        elif level == TokenLevel.L4_NORMAL:
            return priority in ["p0", "p1"]
        elif level == TokenLevel.L3_THROTTLE:
            return priority == "p0"
        elif level == TokenLevel.L2_CRITICAL:
            return priority == "p0" and category in ["category_1", "category_6"]
        else:  # L1_HALT
            return False
```

### 5.2 Token感知执行策略

```python
# core/token_aware_executor.py
class TokenAwareExecutor:
    """Token感知执行器 - 根据Token档位动态调整策略"""
    
    def __init__(self, token_engine: TokenEngine):
        self.token_engine = token_engine
        self.execution_stats = {
            "executed": 0,
            "skipped": 0,
            "deferred": 0
        }
    
    async def execute_batch(self, tasks: List[TaskContext]) -> List[TaskResult]:
        """批量执行任务，根据Token档位调整"""
        results = []
        
        for task in tasks:
            level = self.token_engine.budget.level
            
            # L2以下只处理P0
            if level == TokenLevel.L2_CRITICAL and task.priority != "p0":
                self.execution_stats["skipped"] += 1
                results.append(TaskResult(
                    task_id=task.task_id,
                    status="skipped",
                    output={"reason": "Token critical, only P0 allowed"},
                    token_consumed=0,
                    time_elapsed=0
                ))
                continue
                
            # 估算成本
            handler = HandlerManager.get_handler(task.category)
            cost_estimate = handler.estimate_cost(task)
            
            # 检查预算
            if cost_estimate["tokens"] > self.token_engine.budget.available:
                # 降级策略：简化处理
                task.data["_degraded"] = True
                self.execution_stats["deferred"] += 1
            
            # 执行
            result = await HandlerManager.execute(task)
            results.append(result)
            
            # 记录Token消耗
            self.token_engine.consume(result.token_consumed, task.task_id)
            self.execution_stats["executed"] += 1
            
        return results
```

---

## 6. 预留升级接口

### 6.1 版本管理

```python
# upgrade/version_manager.py
class VersionManager:
    """版本管理器 - 管理处理器版本"""
    
    def __init__(self):
        self.versions: Dict[str, VersionInfo] = {}
        self.migrations: Dict[str, List[Migration]] = {}
    
    def register_version(self, component: str, version: str, handler_class: Type):
        """注册组件版本"""
        self.versions[component] = VersionInfo(
            component=component,
            version=version,
            handler_class=handler_class,
            registered_at=datetime.now()
        )
    
    def check_upgrade(self, component: str, target_version: str) -> bool:
        """检查是否需要升级"""
        current = self.versions.get(component)
        if not current:
            return True
        return self._compare_version(current.version, target_version) < 0
    
    async def upgrade(self, component: str, target_version: str) -> bool:
        """执行升级"""
        # 1. 加载新版本处理器
        new_handler = self._load_handler(component, target_version)
        
        # 2. 执行数据迁移
        migration_path = self._get_migration_path(component, target_version)
        for migration in migration_path:
            await migration.run()
        
        # 3. 热切换（不停机）
        await self._hot_swap(component, new_handler)
        
        return True
```

### 6.2 热重载机制

```python
# upgrade/hot_reloader.py
class HotReloader:
    """热重载器 - 不停机更新处理器"""
    
    def __init__(self, handler_manager: HandlerManager):
        self.handler_manager = handler_manager
        self._drain_queue: asyncio.Queue = asyncio.Queue()
        self._active_handlers: Set[str] = set()
    
    async def hot_swap(self, category: str, new_handler: TaskHandler):
        """热切换处理器"""
        # 1. 标记旧处理器为 draining（不再接受新任务）
        old_handler = self.handler_manager.get_handler(category)
        
        # 2. 等待活跃任务完成（或超时强制）
        await self._wait_for_drain(category, timeout=60)
        
        # 3. 注册新处理器
        self.handler_manager.register_handler(new_handler)
        
        # 4. 验证新处理器
        if not await self._validate_handler(new_handler):
            # 回滚
            self.handler_manager.register_handler(old_handler)
            raise UpgradeFailedError("Validation failed, rolled back")
    
    async def _wait_for_drain(self, category: str, timeout: int):
        """等待活跃任务完成"""
        start = time.time()
        while category in self._active_handlers:
            if time.time() - start > timeout:
                # 强制完成（保存Checkpoint后终止）
                await self._force_checkpoint(category)
                break
            await asyncio.sleep(0.1)
```

### 6.3 迁移引擎

```python
# upgrade/migration_engine.py
class MigrationEngine:
    """迁移引擎 - 数据迁移和兼容性处理"""
    
    def __init__(self):
        self.migrations: Dict[str, List[Migration]] = {}
    
    def register_migration(self, from_ver: str, to_ver: str, migration: Migration):
        """注册迁移步骤"""
        key = f"{from_ver}->{to_ver}"
        if key not in self.migrations:
            self.migrations[key] = []
        self.migrations[key].append(migration)
    
    async def migrate_checkpoint(self, checkpoint: Dict, target_version: str) -> Dict:
        """迁移检查点数据到新版本"""
        current_ver = checkpoint.get("version", "1.0.0")
        
        while current_ver != target_version:
            next_ver = self._get_next_version(current_ver, target_version)
            if not next_ver:
                raise MigrationError(f"No migration path from {current_ver} to {target_version}")
            
            key = f"{current_ver}->{next_ver}"
            for migration in self.migrations.get(key, []):
                checkpoint = await migration.apply(checkpoint)
            
            current_ver = next_ver
            checkpoint["version"] = current_ver
        
        return checkpoint
```

---

## 7. 核心数据流

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            任务执行数据流                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Input                                                                        │
│    │                                                                          │
│    ▼                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Task Router (任务路由器)                                            │    │
│  │  - 解析任务类型、优先级、数据                                          │    │
│  │  - 加载对应处理器配置                                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│    │                                                                          │
│    ▼                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Token Engine (Token引擎)                                            │    │
│  │  - 检查预算是否充足                                                    │    │
│  │  - 决定执行策略(L1-L5)                                                 │    │
│  │  - 分配Token配额                                                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│    │                                                                          │
│    ▼                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Handler Manager (处理器管理器)                                        │    │
│  │  - 获取对应处理器                                                      │    │
│  │  - 执行中间件链(审计/日志/监控)                                         │    │
│  │  - 调用处理器执行                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│    │                                                                          │
│    ▼                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Checkpoint Manager (检查点管理器)                                     │    │
│  │  - 定期保存执行状态                                                    │    │
│  │  - 支持中断恢复                                                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│    │                                                                          │
│    ▼                                                                          │
│  Output                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  - 执行结果报告                                                        │    │
│  │  - Token消耗统计                                                       │    │
│  │  - 审计报告                                                            │    │
│  │  - 下一步建议                                                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. 配置示例

```yaml
# config/executor.yaml
executor:
  name: "universal-task-executor-v3"
  version: "3.0.0"
  
  # Token配置
  token:
    default_budget: 100000  # 默认Token预算
    reserve_ratio: 0.1      # 保留比例
    alert_thresholds: [0.7, 0.5, 0.3, 0.15]  # 档位阈值
  
  # Checkpoint配置
  checkpoint:
    enabled: true
    default_interval: 5     # 默认每5条记录
    storage: "file"         # file/redis/database
    path: "memory/checkpoints/"
    max_retries: 3
  
  # 处理器配置
  handlers:
    auto_discover: true     # 自动发现plugins/handlers/下的处理器
    preload: ["category_1", "category_6"]  # 预加载
  
  # 升级配置
  upgrade:
    auto_check: true        # 自动检查更新
    hot_reload: true        # 启用热重载
    rollback_on_failure: true  # 失败自动回滚
  
  # 审计配置
  audit:
    blue_army_required: ["category_6"]  # 必须蓝军审计的类型
    sampling_rate: 0.2      # P1默认抽样率
  
  # 日志配置
  logging:
    level: "INFO"
    format: "json"
    output: "logs/executor.log"
```

---

## 9. 部署架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          生产部署架构                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Load Balancer                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│              ┌─────────────────────┼─────────────────────┐                  │
│              ▼                     ▼                     ▼                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │  Executor Node 1 │  │  Executor Node 2 │  │  Executor Node N │          │
│  │  (Primary)       │  │  (Secondary)     │  │  (Scale)         │          │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘          │
│           │                     │                     │                     │
│           └─────────────────────┼─────────────────────┘                     │
│                                 ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Shared Storage (检查点/配置)                      │   │
│  │  - Checkpoint持久化                                                  │   │
│  │  - 配置中心                                                          │   │
│  │  - 审计日志                                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. 下一步实施计划

| 阶段 | 内容 | 时间 | 产出 |
|------|------|------|------|
| P0 | 核心引擎实现 | 1周 | core/模块完成 |
| P1 | 6类处理器实现 | 2周 | handlers/完成 |
| P2 | 插件系统实现 | 1周 | plugins/完成 |
| P3 | 升级接口实现 | 1周 | upgrade/完成 |
| P4 | 集成测试 | 1周 | 测试通过 |
| P5 | 文档完善 | 持续 | 完整文档 |

---

**设计完成** | 2026-03-31 | 待评审
