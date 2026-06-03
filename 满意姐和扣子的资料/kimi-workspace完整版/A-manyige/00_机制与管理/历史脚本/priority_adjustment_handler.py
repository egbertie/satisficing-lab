#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优先级调整冲突处理器
Priority Adjustment Conflict Handler

核心原则: 新指令覆盖旧指令时，不暂停，而是子代理承接 + 冲突说明 + 次序调整
"""

import json
import uuid
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('PriorityAdjustmentHandler')


class ConflictType(Enum):
    """冲突类型枚举"""
    PRIORITY = "PRIORITY_CONFLICT"        # 优先级冲突
    RESOURCE = "RESOURCE_CONFLICT"        # 资源冲突
    DEPENDENCY = "DEPENDENCY_CONFLICT"    # 依赖冲突
    TIME = "TIME_CONFLICT"                # 时间冲突


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUBAGENT_RUNNING = "subagent_running"
    COMPLETED = "completed"
    FAILED = "failed"
    STUCK = "stuck"


@dataclass
class Task:
    """任务数据模型"""
    id: str
    name: str
    description: str
    priority: int  # 0=P0, 1=P1, 2=P2, 3=P3
    status: str = TaskStatus.PENDING.value
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    deadline: Optional[str] = None
    assignee: str = "main"  # main 或 subagent_{id}
    parent_task: Optional[str] = None
    resources: List[str] = field(default_factory=list)
    progress: float = 0.0
    intermediate_results: Dict = field(default_factory=dict)
    handoff_reason: Optional[str] = None
    priority_adjusted_reason: Optional[str] = None
    estimated_duration: int = 30  # 预计耗时(分钟)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        return cls(**data)


@dataclass
class Conflict:
    """冲突数据模型"""
    id: str
    type: str
    new_task_id: str
    existing_task_id: str
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())
    details: Dict = field(default_factory=dict)
    resolution: Optional[str] = None
    resolved_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class TaskManager:
    """任务管理器 - 负责任务的CRUD和持久化"""
    
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            storage_path = Path(__file__).parent / "data" / "tasks.json"
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.tasks: Dict[str, Task] = {}
        self.conflicts: Dict[str, Conflict] = {}
        self._load()
    
    def _load(self):
        """从文件加载任务数据"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = {k: Task.from_dict(v) for k, v in data.get('tasks', {}).items()}
                    self.conflicts = {k: Conflict(**v) for k, v in data.get('conflicts', {}).items()}
                logger.info(f"已加载 {len(self.tasks)} 个任务，{len(self.conflicts)} 个冲突记录")
            except Exception as e:
                logger.error(f"加载任务数据失败: {e}")
    
    def _save(self):
        """保存任务数据到文件"""
        try:
            data = {
                'tasks': {k: v.to_dict() for k, v in self.tasks.items()},
                'conflicts': {k: v.to_dict() for k, v in self.conflicts.items()},
                'updated_at': datetime.now().isoformat()
            }
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存任务数据失败: {e}")
    
    def create_task(self, name: str, description: str, priority: int, 
                    resources: List[str] = None, deadline: str = None,
                    estimated_duration: int = 30) -> Task:
        """创建新任务"""
        task = Task(
            id=str(uuid.uuid4())[:8],
            name=name,
            description=description,
            priority=priority,
            resources=resources or [],
            deadline=deadline,
            estimated_duration=estimated_duration
        )
        self.tasks[task.id] = task
        self._save()
        logger.info(f"创建任务: {task.name} (P{task.priority}, ID: {task.id})")
        return task
    
    def get_active_tasks(self) -> List[Task]:
        """获取所有活跃任务(非完成状态)"""
        active_statuses = [TaskStatus.PENDING.value, TaskStatus.RUNNING.value, 
                          TaskStatus.SUBAGENT_RUNNING.value, TaskStatus.STUCK.value]
        return [t for t in self.tasks.values() if t.status in active_statuses]
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取指定任务"""
        return self.tasks.get(task_id)
    
    def update_task(self, task: Task) -> Task:
        """更新任务"""
        self.tasks[task.id] = task
        self._save()
        return task
    
    def create_conflict(self, conflict_type: ConflictType, new_task: Task, 
                       existing_task: Task, details: Dict = None) -> Conflict:
        """创建冲突记录"""
        conflict = Conflict(
            id=str(uuid.uuid4())[:8],
            type=conflict_type.value,
            new_task_id=new_task.id,
            existing_task_id=existing_task.id,
            details=details or {}
        )
        self.conflicts[conflict.id] = conflict
        self._save()
        logger.warning(f"检测到冲突: {conflict_type.value} "
                      f"(新任务: {new_task.name}, 现有任务: {existing_task.name})")
        return conflict
    
    def resolve_conflict(self, conflict_id: str, resolution: str):
        """解决冲突"""
        if conflict_id in self.conflicts:
            self.conflicts[conflict_id].resolution = resolution
            self.conflicts[conflict_id].resolved_at = datetime.now().isoformat()
            self._save()


class ConflictDetector:
    """冲突检测器"""
    
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
    
    def detect_all_conflicts(self, new_task: Task, include_saved: bool = False) -> List[Conflict]:
        """检测新任务与所有现有任务的冲突
        
        Args:
            new_task: 新任务对象
            include_saved: 是否包含已保存的任务（用于演示场景）
        """
        conflicts = []
        existing_tasks = self.task_manager.get_active_tasks()
        
        # 如果新任务已保存到task_manager，需要排除它自己
        if include_saved and new_task.id in [t.id for t in existing_tasks]:
            existing_tasks = [t for t in existing_tasks if t.id != new_task.id]
        
        for existing in existing_tasks:
            # 检查优先级冲突
            if self._is_priority_conflict(new_task, existing):
                conflicts.append(self.task_manager.create_conflict(
                    ConflictType.PRIORITY,
                    new_task,
                    existing,
                    {'priority_diff': existing.priority - new_task.priority}
                ))
            
            # 检查资源冲突
            resource_overlap = self._get_resource_overlap(new_task, existing)
            if resource_overlap:
                conflicts.append(self.task_manager.create_conflict(
                    ConflictType.RESOURCE,
                    new_task,
                    existing,
                    {'shared_resources': resource_overlap}
                ))
            
            # 检查依赖冲突
            if self._is_dependency_conflict(new_task, existing):
                conflicts.append(self.task_manager.create_conflict(
                    ConflictType.DEPENDENCY,
                    new_task,
                    existing,
                    {'dependency_chain': self._get_dependency_chain(new_task, existing)}
                ))
        
        return conflicts
    
    def _is_priority_conflict(self, new_task: Task, existing: Task) -> bool:
        """检查是否存在优先级冲突
        
        冲突条件:
        1. 新任务优先级高于现有任务 (数字更小)
        2. 两者都是P0 (需要P0独占)
        """
        # 新任务优先级更高
        if new_task.priority < existing.priority:
            return True
        
        # 两者都是P0，需要处理P0独占
        if new_task.priority == 0 and existing.priority == 0:
            return True
        
        return False
    
    def _get_resource_overlap(self, new_task: Task, existing: Task) -> List[str]:
        """获取资源重叠列表"""
        return list(set(new_task.resources) & set(existing.resources))
    
    def _is_dependency_conflict(self, new_task: Task, existing: Task) -> bool:
        """检查是否存在依赖冲突"""
        # 简化的依赖检查：检查任务描述中是否提到依赖
        # 实际实现可能需要更复杂的依赖图
        return False  # TODO: 实现依赖图检测
    
    def _get_dependency_chain(self, new_task: Task, existing: Task) -> List[str]:
        """获取依赖链"""
        return []


class SubagentSpawner:
    """子代理生成器 - 负责任务的子代理承接"""
    
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
    
    def should_handoff(self, task: Task) -> bool:
        """判断任务是否应该由子代理承接"""
        # 检查任务是否已经开始执行
        if task.status != TaskStatus.RUNNING.value:
            return False
        
        # 检查任务持续时间
        if task.started_at:
            started = datetime.fromisoformat(task.started_at)
            duration = (datetime.now() - started).total_seconds() / 60
            if duration > 5:  # 执行超过5分钟
                return True
        
        # 检查是否有明确交付物
        if task.intermediate_results:
            return True
        
        # 检查是否涉及外部资源
        if task.resources:
            return True
        
        return False
    
    def handoff(self, task: Task, reason: str) -> Dict:
        """将任务交接给子代理"""
        subagent_id = f"subagent_{uuid.uuid4().hex[:6]}"
        
        # 更新任务状态
        task.status = TaskStatus.SUBAGENT_RUNNING.value
        task.assignee = subagent_id
        task.handoff_reason = reason
        self.task_manager.update_task(task)
        
        # 构建子代理上下文
        context = {
            'task': task.to_dict(),
            'handoff_reason': reason,
            'original_session': 'main',
            'instructions': self._generate_subagent_instructions(task, reason)
        }
        
        logger.info(f"任务 {task.name} 已交接给子代理 {subagent_id}")
        
        return {
            'subagent_id': subagent_id,
            'context': context,
            'task_id': task.id
        }
    
    def _generate_subagent_instructions(self, task: Task, reason: str) -> str:
        """生成子代理执行指令"""
        return f"""
【子代理承接任务】

任务名称: {task.name}
任务描述: {task.description}
优先级: P{task.priority}
当前进度: {task.progress}%

交接原因: {reason}

你的职责:
1. 继续执行此任务，不要从头开始
2. 利用现有的中间结果: {json.dumps(task.intermediate_results, ensure_ascii=False)}
3. 完成后向主代理报告结果
4. 如遇到问题立即上报

截止时间: {task.deadline or '无'}
"""


class PriorityReorderer:
    """优先级重排序器"""
    
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
    
    def reorder(self, new_task: Task) -> Dict:
        """
        重新排序所有任务的优先级
        返回调整详情
        """
        adjustments = []
        all_tasks = self.task_manager.get_active_tasks()
        
        # P0限制：只能有一个P0
        if new_task.priority == 0:
            existing_p0 = [t for t in all_tasks if t.priority == 0 and t.id != new_task.id]
            for old_p0 in existing_p0:
                old_priority = old_p0.priority
                old_p0.priority = 1  # 降级为P1
                old_p0.priority_adjusted_reason = f"新P0任务产生: {new_task.name}"
                self.task_manager.update_task(old_p0)
                adjustments.append({
                    'task_id': old_p0.id,
                    'task_name': old_p0.name,
                    'from_priority': old_priority,
                    'to_priority': 1,
                    'reason': old_p0.priority_adjusted_reason
                })
        
        # P1限制：最多3个
        if new_task.priority == 1:
            existing_p1 = [t for t in all_tasks if t.priority == 1 and t.id != new_task.id]
            if len(existing_p1) >= 3:
                # 按创建时间排序，最早的降级
                existing_p1.sort(key=lambda t: t.created_at)
                to_downgrade = existing_p1[0]  # 最早的P1降级
                old_priority = to_downgrade.priority
                to_downgrade.priority = 2  # 降级为P2
                to_downgrade.priority_adjusted_reason = f"P1超限，新P1任务: {new_task.name}"
                self.task_manager.update_task(to_downgrade)
                adjustments.append({
                    'task_id': to_downgrade.id,
                    'task_name': to_downgrade.name,
                    'from_priority': old_priority,
                    'to_priority': 2,
                    'reason': to_downgrade.priority_adjusted_reason
                })
        
        return {
            'new_task_priority': new_task.priority,
            'adjustments': adjustments,
            'total_active_tasks': len(all_tasks) + 1
        }


class UserNotifier:
    """用户通知器"""
    
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
    
    def notify_conflict(self, conflicts: List[Conflict], new_task: Task, 
                       resolution_plan: Dict) -> str:
        """向用户发送冲突通知"""
        
        message = self._generate_notification(conflicts, new_task, resolution_plan)
        
        # 记录通知日志
        logger.info("=" * 60)
        logger.info("【优先级调整通知】")
        logger.info(message)
        logger.info("=" * 60)
        
        return message
    
    def _generate_notification(self, conflicts: List[Conflict], new_task: Task,
                              resolution_plan: Dict) -> str:
        """生成通知消息"""
        
        lines = [
            "## 🔔 任务优先级调整通知",
            "",
            f"**新任务**: {new_task.name} (P{new_task.priority})",
            f"**任务描述**: {new_task.description}",
            "",
            "### 检测到的冲突",
        ]
        
        for conflict in conflicts:
            existing = self.task_manager.get_task(conflict.existing_task_id)
            if existing:
                lines.append(f"- **{conflict.type}**: 与 '{existing.name}' (P{existing.priority})")
                if conflict.details:
                    for key, value in conflict.details.items():
                        lines.append(f"  - {key}: {value}")
        
        lines.extend([
            "",
            "### 调整方案",
            f"1. **新任务** '{new_task.name}' 将立即启动，优先级为 P{new_task.priority}",
        ])
        
        # 子代理承接信息
        if resolution_plan.get('handoffs'):
            lines.append("2. **以下任务将由子代理继续执行**:")
            for handoff in resolution_plan['handoffs']:
                task = self.task_manager.get_task(handoff['task_id'])
                if task:
                    lines.append(f"   - '{task.name}' → 子代理 {handoff['subagent_id']}")
        
        # 优先级调整信息
        if resolution_plan.get('priority_adjustments', {}).get('adjustments'):
            lines.append("3. **优先级调整**:")
            for adj in resolution_plan['priority_adjustments']['adjustments']:
                lines.append(f"   - '{adj['task_name']}': P{adj['from_priority']} → P{adj['to_priority']}")
                lines.append(f"     原因: {adj['reason']}")
        
        # 预计完成时间
        lines.extend([
            "",
            "### 预计时间",
            f"- 新任务 '{new_task.name}': {new_task.estimated_duration}分钟",
        ])
        if resolution_plan.get('handoffs'):
            for handoff in resolution_plan['handoffs']:
                task = self.task_manager.get_task(handoff['task_id'])
                if task:
                    remaining = int(task.estimated_duration * (1 - task.progress / 100))
                    lines.append(f"- 子代理任务 '{task.name}': {remaining}分钟")
        
        lines.extend([
            "",
            "### 您的选择",
            "- **[确认]**: 按上述方案执行",
            "- **[调整]**: 我需要修改优先级",
            "- **[合并]**: 将相关任务合并执行",
            "",
            f"*通知时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ])
        
        return "\n".join(lines)


class PriorityAdjustmentHandler:
    """
    优先级调整冲突处理器 - 主入口类
    
    使用示例:
        handler = PriorityAdjustmentHandler()
        result = handler.handle_new_task(
            name="紧急Bug修复",
            description="修复生产环境登录问题",
            priority=0
        )
    """
    
    def __init__(self, storage_path: str = None):
        self.task_manager = TaskManager(storage_path)
        self.conflict_detector = ConflictDetector(self.task_manager)
        self.subagent_spawner = SubagentSpawner(self.task_manager)
        self.priority_reorderer = PriorityReorderer(self.task_manager)
        self.user_notifier = UserNotifier(self.task_manager)
    
    def handle_new_task(self, name: str, description: str, priority: int = 1,
                       resources: List[str] = None, deadline: str = None,
                       estimated_duration: int = 30, auto_execute: bool = True) -> Dict:
        """
        处理新任务，自动检测冲突并调整优先级
        
        Args:
            name: 任务名称
            description: 任务描述
            priority: 优先级 (0=P0, 1=P1, 2=P2, 3=P3)
            resources: 占用的资源列表
            deadline: 截止时间 (ISO格式)
            estimated_duration: 预计耗时(分钟)
            auto_execute: 是否自动执行调整
        
        Returns:
            处理结果字典
        """
        # 1. 创建新任务
        new_task = self.task_manager.create_task(
            name=name,
            description=description,
            priority=priority,
            resources=resources or [],
            deadline=deadline,
            estimated_duration=estimated_duration
        )
        
        # 2. 检测冲突 (排除新任务自身)
        conflicts = self.conflict_detector.detect_all_conflicts(new_task, include_saved=True)
        
        if not conflicts:
            # 无冲突，直接标记为运行中
            new_task.status = TaskStatus.RUNNING.value
            new_task.started_at = datetime.now().isoformat()
            self.task_manager.update_task(new_task)
            
            logger.info(f"新任务 '{name}' 无冲突，直接启动")
            
            return {
                'success': True,
                'task_id': new_task.id,
                'conflicts_detected': 0,
                'action': 'direct_execute',
                'message': f"任务 '{name}' 已启动，无冲突"
            }
        
        # 3. 有冲突，执行调整流程
        logger.info(f"检测到 {len(conflicts)} 个冲突，开始调整")
        
        # 3.1 子代理承接现有任务
        handoffs = []
        for conflict in conflicts:
            existing = self.task_manager.get_task(conflict.existing_task_id)
            if existing and self.subagent_spawner.should_handoff(existing):
                handoff_result = self.subagent_spawner.handoff(
                    existing,
                    reason=f"优先级调整: 新任务 '{new_task.name}' (P{new_task.priority}) 产生冲突"
                )
                handoffs.append(handoff_result)
        
        # 3.2 重排序优先级
        priority_adjustments = self.priority_reorderer.reorder(new_task)
        
        # 3.3 启动新任务
        new_task.status = TaskStatus.RUNNING.value
        new_task.started_at = datetime.now().isoformat()
        self.task_manager.update_task(new_task)
        
        # 3.4 生成解决方案
        resolution_plan = {
            'handoffs': handoffs,
            'priority_adjustments': priority_adjustments,
            'conflicts': [c.to_dict() for c in conflicts]
        }
        
        # 3.5 通知用户
        notification = self.user_notifier.notify_conflict(
            conflicts, new_task, resolution_plan
        )
        
        # 3.6 解决冲突记录
        for conflict in conflicts:
            self.task_manager.resolve_conflict(
                conflict.id,
                resolution=f"优先级调整完成: 新任务P{new_task.priority}，"
                          f"{len(handoffs)}个任务移交子代理"
            )
        
        return {
            'success': True,
            'task_id': new_task.id,
            'conflicts_detected': len(conflicts),
            'action': 'priority_adjusted',
            'resolution_plan': resolution_plan,
            'notification': notification,
            'message': f"任务 '{name}' 已启动，优先级已调整，{len(handoffs)}个任务移交子代理"
        }
    
    def get_task_status(self, task_id: str = None) -> Dict:
        """获取任务状态"""
        if task_id:
            task = self.task_manager.get_task(task_id)
            if task:
                return {'task': task.to_dict()}
            return {'error': f'任务 {task_id} 不存在'}
        
        active_tasks = self.task_manager.get_active_tasks()
        return {
            'active_tasks': [t.to_dict() for t in active_tasks],
            'total_active': len(active_tasks),
            'p0_count': sum(1 for t in active_tasks if t.priority == 0),
            'p1_count': sum(1 for t in active_tasks if t.priority == 1),
        }
    
    def list_conflicts(self) -> List[Dict]:
        """列出所有未解决的冲突"""
        unresolved = [c for c in self.task_manager.conflicts.values() 
                     if c.resolution is None]
        return [c.to_dict() for c in unresolved]


# 命令行接口
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="优先级调整冲突处理器")
    parser.add_argument("action", choices=["create", "status", "conflicts"],
                       help="操作类型")
    parser.add_argument("--name", help="任务名称")
    parser.add_argument("--description", help="任务描述")
    parser.add_argument("--priority", type=int, default=1, 
                       help="优先级 (0=P0, 1=P1, 2=P2, 3=P3)")
    parser.add_argument("--resources", help="资源列表，逗号分隔")
    parser.add_argument("--task-id", help="任务ID")
    
    args = parser.parse_args()
    
    handler = PriorityAdjustmentHandler()
    
    if args.action == "create":
        if not args.name or not args.description:
            print("错误: --name 和 --description 是必需的")
            exit(1)
        
        resources = args.resources.split(",") if args.resources else []
        result = handler.handle_new_task(
            name=args.name,
            description=args.description,
            priority=args.priority,
            resources=resources
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.action == "status":
        result = handler.get_task_status(args.task_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.action == "conflicts":
        result = handler.list_conflicts()
        print(json.dumps(result, ensure_ascii=False, indent=2))
