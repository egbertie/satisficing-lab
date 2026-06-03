"""
Universal Task Executor V3.0 - 任务注册表
支持1-6类任务的动态注册和配置管理
"""

import os
import sys
import json
import logging
import importlib.util
from typing import Dict, List, Optional, Type, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path

from .structures import Task, HandlerInfo, HandlerRegistration, TaskResult

logger = logging.getLogger(__name__)


@dataclass
class TaskTypeConfig:
    """任务类型配置"""
    category: str
    name: str
    display_name: str
    description: str
    default_handler: str
    priority_weights: Dict[str, int] = field(default_factory=dict)
    audit_required: bool = True
    blue_army_required: bool = False
    checkpoint_interval: int = 5  # 每N条记录检查点
    
    def __post_init__(self):
        """设置默认值"""
        if not self.priority_weights:
            self.priority_weights = {"p0": 10, "p1": 5, "p2": 2, "p3": 1}


class TaskHandler:
    """
    任务处理器基类 - 所有处理器必须继承此类
    
    子类需要实现:
    - handler_name: 处理器名称
    - supported_categories: 支持的任务类型列表
    - validate(): 验证任务数据
    - execute(): 执行任务
    - estimate_cost(): 估算成本
    """
    
    # 子类必须覆盖
    handler_name: str = "base_handler"
    supported_categories: List[str] = []
    version: str = "1.0.0"
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化处理器
        
        Args:
            config: 处理器配置
        """
        self.config = config or {}
        self.enabled = True
        self.stats = {
            "executed": 0,
            "succeeded": 0,
            "failed": 0,
            "total_tokens": 0
        }
        logger.info(f"Handler initialized: {self.handler_name} v{self.version}")
    
    def validate(self, task: Task) -> bool:
        """
        验证任务数据是否合法
        
        Args:
            task: 待验证任务
            
        Returns:
            是否验证通过
        """
        # 基础验证
        if not task.task_id:
            logger.error("Task validation failed: missing task_id")
            return False
        
        if not task.category:
            logger.error("Task validation failed: missing category")
            return False
        
        if task.category not in self.supported_categories:
            logger.error(f"Task validation failed: unsupported category {task.category}")
            return False
        
        return True
    
    def execute(self, task: Task, checkpoint_state: Optional[Dict] = None) -> TaskResult:
        """
        执行任务
        
        Args:
            task: 要执行的任务
            checkpoint_state: 检查点状态（用于恢复）
            
        Returns:
            任务执行结果
        """
        raise NotImplementedError("Subclasses must implement execute()")
    
    def estimate_cost(self, task: Task) -> Dict[str, int]:
        """
        估算Token和时间成本
        
        Args:
            task: 待估算任务
            
        Returns:
            {"tokens": int, "time_seconds": int}
        """
        # 基础估算，子类应覆盖
        return {
            "tokens": 1000,
            "time_seconds": 60
        }
    
    def get_checkpoint_state(self) -> Dict[str, Any]:
        """
        获取处理器状态用于Checkpoint
        
        返回的状态必须是JSON可序列化的
        """
        return {
            "handler_name": self.handler_name,
            "version": self.version,
            "stats": self.stats
        }
    
    def restore_from_checkpoint(self, state: Dict[str, Any]) -> None:
        """
        从Checkpoint状态恢复
        
        Args:
            state: 检查点状态
        """
        if "stats" in state:
            self.stats = state["stats"]
        logger.info(f"Handler restored from checkpoint: {self.handler_name}")
    
    def get_info(self) -> HandlerInfo:
        """获取处理器信息"""
        return HandlerInfo(
            handler_id=f"{self.handler_name}_v{self.version}",
            name=self.handler_name,
            version=self.version,
            supported_categories=self.supported_categories,
            description=f"Base handler for {', '.join(self.supported_categories)}"
        )


class TaskRegistry:
    """
    任务注册表 - 核心组件
    
    职责:
    1. 管理6类任务的标准配置
    2. 注册和查找任务处理器
    3. 动态加载处理器插件
    4. 任务类型扩展
    """
    
    # 6类任务标准配置
    DEFAULT_TASK_TYPES: Dict[str, TaskTypeConfig] = {
        "category_1": TaskTypeConfig(
            category="category_1",
            name="governance_enhancement",
            display_name="治理体系完善",
            description="完善管理规则、检查清单、SOP文档",
            default_handler="governance_handler",
            priority_weights={"p0": 10, "p1": 5, "p2": 2, "p3": 1},
            audit_required=True,
            checkpoint_interval=5
        ),
        "category_2": TaskTypeConfig(
            category="category_2",
            name="cron_deployment",
            display_name="周期性任务部署",
            description="部署和管理Cron定时任务",
            default_handler="cron_handler",
            priority_weights={"p0": 8, "p1": 4, "p2": 1, "p3": 1},
            audit_required=True,
            checkpoint_interval=3
        ),
        "category_3": TaskTypeConfig(
            category="category_3",
            name="system_building",
            display_name="系统能力建设",
            description="构建自动化脚本、监控系统、灾备机制",
            default_handler="system_handler",
            priority_weights={"p0": 9, "p1": 5, "p2": 2, "p3": 1},
            audit_required=True,
            checkpoint_interval=1  # 系统建设重要，每条记录检查点
        ),
        "category_4": TaskTypeConfig(
            category="category_4",
            name="data_governance",
            display_name="历史数据治理",
            description="清理、整理、归档历史数据",
            default_handler="data_handler",
            priority_weights={"p0": 6, "p1": 4, "p2": 2, "p3": 1},
            audit_required=True,
            checkpoint_interval=10
        ),
        "category_5": TaskTypeConfig(
            category="category_5",
            name="misc_cleanup",
            display_name="杂项清理",
            description="清理临时文件、过期配置、待分类项",
            default_handler="misc_handler",
            priority_weights={"p0": 5, "p1": 3, "p2": 1, "p3": 1},
            audit_required=False,  # 杂项不需要审计
            checkpoint_interval=20
        ),
        "category_6": TaskTypeConfig(
            category="category_6",
            name="full_audit",
            display_name="全量任务审计",
            description="大规模历史任务深度审计（继承V2.0）",
            default_handler="audit_handler",
            priority_weights={"p0": 10, "p1": 6, "p2": 3, "p3": 1},
            audit_required=True,
            blue_army_required=True,  # 必须蓝军审计
            checkpoint_interval=5
        ),
    }
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, plugin_path: str = None):
        """
        初始化注册表
        
        Args:
            plugin_path: 插件目录路径
        """
        if self._initialized:
            return
        
        self._handlers: Dict[str, TaskHandler] = {}
        self._handler_classes: Dict[str, Type[TaskHandler]] = {}
        self._configs: Dict[str, TaskTypeConfig] = {}
        self._registrations: Dict[str, HandlerRegistration] = {}
        self._plugin_path = plugin_path or "plugins/handlers"
        
        # 初始化默认配置
        self._init_default_configs()
        
        self._initialized = True
        logger.info("TaskRegistry initialized")
    
    def _init_default_configs(self):
        """初始化默认任务类型配置"""
        for category, config in self.DEFAULT_TASK_TYPES.items():
            self._configs[category] = config
        logger.info(f"Loaded {len(self._configs)} default task type configs")
    
    def register_handler(self, handler_class: Type[TaskHandler], 
                        config: Dict[str, Any] = None) -> None:
        """
        注册处理器类
        
        Args:
            handler_class: 处理器类（必须继承TaskHandler）
            config: 处理器配置
        """
        if not issubclass(handler_class, TaskHandler):
            raise ValueError(f"Handler class must inherit from TaskHandler: {handler_class}")
        
        # 创建临时实例获取信息
        temp_instance = handler_class(config)
        handler_name = temp_instance.handler_name
        supported_categories = temp_instance.supported_categories
        
        # 注册类
        self._handler_classes[handler_name] = handler_class
        
        # 为每个支持的类别注册实例
        for category in supported_categories:
            if category not in self._configs:
                logger.warning(f"Unknown category: {category}")
                continue
            
            instance = handler_class(config)
            self._handlers[category] = instance
            
            # 保存注册信息
            self._registrations[category] = HandlerRegistration(
                handler_info=instance.get_info(),
                module_path=handler_class.__module__,
                class_name=handler_class.__name__,
                config=config or {},
                enabled=True
            )
        
        logger.info(f"Handler registered: {handler_name} for categories: {supported_categories}")
    
    def register_handler_instance(self, handler: TaskHandler) -> None:
        """
        注册处理器实例
        
        Args:
            handler: 处理器实例
        """
        for category in handler.supported_categories:
            self._handlers[category] = handler
            self._registrations[category] = HandlerRegistration(
                handler_info=handler.get_info(),
                module_path=handler.__class__.__module__,
                class_name=handler.__class__.__name__,
                config=getattr(handler, 'config', {}),
                enabled=True
            )
        
        logger.info(f"Handler instance registered: {handler.handler_name}")
    
    def get_handler(self, category: str) -> Optional[TaskHandler]:
        """
        获取任务处理器
        
        Args:
            category: 任务类别
            
        Returns:
            处理器实例，如果不存在则尝试加载插件
        """
        if category in self._handlers:
            return self._handlers[category]
        
        # 尝试加载插件
        self._load_plugin(category)
        
        return self._handlers.get(category)
    
    def get_handler_class(self, handler_name: str) -> Optional[Type[TaskHandler]]:
        """
        获取处理器类
        
        Args:
            handler_name: 处理器名称
            
        Returns:
            处理器类
        """
        return self._handler_classes.get(handler_name)
    
    def _load_plugin(self, category: str) -> bool:
        """
        动态加载处理器插件
        
        Args:
            category: 任务类别
            
        Returns:
            是否加载成功
        """
        config = self._configs.get(category)
        if not config:
            logger.error(f"Unknown category: {category}")
            return False
        
        handler_name = config.default_handler
        plugin_file = f"{handler_name}.py"
        plugin_path = os.path.join(self._plugin_path, plugin_file)
        
        if not os.path.exists(plugin_path):
            logger.warning(f"Plugin not found: {plugin_path}")
            return False
        
        try:
            # 动态加载模块
            spec = importlib.util.spec_from_file_location(handler_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[handler_name] = module
            spec.loader.exec_module(module)
            
            # 调用注册函数
            if hasattr(module, 'register_handler'):
                module.register_handler(self)
                logger.info(f"Plugin loaded: {handler_name} for {category}")
                return True
            else:
                logger.error(f"Plugin {handler_name} has no register_handler function")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load plugin {handler_name}: {e}")
            return False
    
    def get_config(self, category: str) -> Optional[TaskTypeConfig]:
        """
        获取任务类型配置
        
        Args:
            category: 任务类别
            
        Returns:
            任务类型配置
        """
        return self._configs.get(category)
    
    def register_task_type(self, config: TaskTypeConfig) -> None:
        """
        注册新任务类型
        
        Args:
            config: 任务类型配置
        """
        self._configs[config.category] = config
        logger.info(f"Task type registered: {config.category} - {config.display_name}")
    
    def list_categories(self) -> List[str]:
        """列出所有已注册的任务类别"""
        return list(self._configs.keys())
    
    def list_handlers(self) -> List[HandlerInfo]:
        """列出所有已注册的处理器"""
        return [reg.handler_info for reg in self._registrations.values()]
    
    def get_registration(self, category: str) -> Optional[HandlerRegistration]:
        """获取处理器注册信息"""
        return self._registrations.get(category)
    
    def is_handler_enabled(self, category: str) -> bool:
        """检查处理器是否启用"""
        reg = self._registrations.get(category)
        return reg.enabled if reg else False
    
    def enable_handler(self, category: str) -> None:
        """启用处理器"""
        if category in self._registrations:
            self._registrations[category].enabled = True
            logger.info(f"Handler enabled: {category}")
    
    def disable_handler(self, category: str) -> None:
        """禁用处理器"""
        if category in self._registrations:
            self._registrations[category].enabled = False
            logger.info(f"Handler disabled: {category}")
    
    def get_priority_weight(self, category: str, priority: str) -> int:
        """
        获取优先级权重
        
        Args:
            category: 任务类别
            priority: 优先级 (p0/p1/p2/p3)
            
        Returns:
            权重值
        """
        config = self._configs.get(category)
        if not config:
            return 1
        return config.priority_weights.get(priority, 1)
    
    def is_audit_required(self, category: str) -> bool:
        """检查是否需要审计"""
        config = self._configs.get(category)
        return config.audit_required if config else False
    
    def is_blue_army_required(self, category: str) -> bool:
        """检查是否需要蓝军审计"""
        config = self._configs.get(category)
        return config.blue_army_required if config else False
    
    def get_checkpoint_interval(self, category: str) -> int:
        """获取检查点间隔"""
        config = self._configs.get(category)
        return config.checkpoint_interval if config else 5
    
    def auto_discover_plugins(self) -> int:
        """
        自动发现插件目录中的处理器
        
        Returns:
            发现的插件数量
        """
        if not os.path.exists(self._plugin_path):
            logger.warning(f"Plugin path not found: {self._plugin_path}")
            return 0
        
        count = 0
        for file in os.listdir(self._plugin_path):
            if file.endswith("_handler.py"):
                # 尝试提取类别
                handler_name = file[:-3]  # 去掉.py
                # 假设处理器名称为 xxx_handler，尝试找到对应类别
                for category, config in self._configs.items():
                    if config.default_handler == handler_name:
                        if self._load_plugin(category):
                            count += 1
                        break
        
        logger.info(f"Auto-discovered {count} plugins")
        return count
    
    def export_config(self) -> Dict[str, Any]:
        """导出所有配置"""
        return {
            "task_types": {
                cat: {
                    "category": cfg.category,
                    "name": cfg.name,
                    "display_name": cfg.display_name,
                    "description": cfg.description,
                    "default_handler": cfg.default_handler,
                    "priority_weights": cfg.priority_weights,
                    "audit_required": cfg.audit_required,
                    "blue_army_required": cfg.blue_army_required,
                    "checkpoint_interval": cfg.checkpoint_interval,
                }
                for cat, cfg in self._configs.items()
            },
            "handlers": {
                cat: {
                    "handler_id": reg.handler_info.handler_id,
                    "name": reg.handler_info.name,
                    "version": reg.handler_info.version,
                    "supported_categories": reg.handler_info.supported_categories,
                    "enabled": reg.enabled,
                }
                for cat, reg in self._registrations.items()
            }
        }
    
    def import_config(self, config: Dict[str, Any]) -> None:
        """导入配置"""
        task_types = config.get("task_types", {})
        for cat, cfg_data in task_types.items():
            config = TaskTypeConfig(**cfg_data)
            self._configs[cat] = config
        
        logger.info(f"Imported {len(task_types)} task type configs")


# 全局注册表实例
_registry: Optional[TaskRegistry] = None


def get_registry(plugin_path: str = None) -> TaskRegistry:
    """
    获取全局注册表实例
    
    Args:
        plugin_path: 插件目录路径
        
    Returns:
        任务注册表实例
    """
    global _registry
    if _registry is None:
        _registry = TaskRegistry(plugin_path)
    return _registry


def reset_registry() -> None:
    """重置全局注册表（主要用于测试）"""
    global _registry
    _registry = None
