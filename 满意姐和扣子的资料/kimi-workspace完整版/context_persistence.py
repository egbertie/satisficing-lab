"""
---
KIA-CODE: 知识入库代码级闭环
Asset: context_persistence.py
Status: ✅ 代码级KIA完成
Date: 2026-04-15
Batch: OM-03 Python资产25份代码级KIA-批次三

KIA-Loop:
  - 接收清点: 2026-04-15
  - 轻量提取: 2026-04-15 (代码结构识别)
  - 查重去冗: 2026-04-15 (无重复代码)
  - Tier分级: T1 (核心项目资产)
  - 深度洞察: 2026-04-15 (案例库与决策系统)
  - 血液化: ✅ 完成 (五路图腾映射确认)
  - 归档锁定: 2026-04-15

功能定位:
  - 用途: 上下文持久化
  - 关联: 会话记忆
  - 维护者: 蓝军+满意姐

血液化映射:
  - 五路图腾关联: 记忆系统
  - 产品映射: 观自在-记忆
  - 运营映射: 案例库与决策支持

---
"""

#!/usr/bin/env python3
"""
上下文持久化管理器
解决"永远在碎片中"的问题：确保跨会话的上下文连续性
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class ContextPersistenceManager:
    """
    上下文持久化管理器
    保存和恢复完整上下文（不仅是记录，是可恢复的状态）
    """
    
    def __init__(self):
        self.workspace = "/root/.openclaw/workspace"
        self.context_file = f"{self.workspace}/.persistent_context.json"
        self.checksum_file = f"{self.workspace}/.context_checksum"
        self.session_file = f"{self.workspace}/.session_context.json"
        
        # 上下文结构定义
        self.context_schema = {
            'timestamp': str,
            'session_id': str,
            'ongoing_tasks': List[Dict],
            'pending_decisions': List[Dict],
            'user_preferences': Dict,
            'working_memory': Dict,
            'recent_decisions': List[Dict],
            'file_processing_queue': List[Dict],
            'skill_reflex_state': Dict,
            'last_session_summary': str,
            'next_session_prerequisites': List[str]
        }
    
    def save_full_context(self, extra_data: Dict = None):
        """
        保存完整上下文
        
        包含：
        - 进行中任务
        - 待决策事项
        - 用户偏好
        - 工作记忆快照
        - 文件处理队列
        - Skill反射状态
        """
        context = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self._generate_session_id(),
            'ongoing_tasks': self._get_ongoing_tasks(),
            'pending_decisions': self._get_pending_decisions(),
            'user_preferences': self._get_user_preferences(),
            'working_memory': self._get_working_memory_snapshot(),
            'recent_decisions': self._get_recent_decisions(),
            'file_processing_queue': self._get_file_queue(),
            'skill_reflex_state': self._get_skill_reflex_state(),
            'last_session_summary': self._generate_session_summary(),
            'next_session_prerequisites': self._generate_prerequisites()
        }
        
        if extra_data:
            context.update(extra_data)
        
        # 保存上下文
        with open(self.context_file, 'w') as f:
            json.dump(context, f, indent=2, default=str)
        
        # 生成校验和（防篡改）
        checksum = self._generate_checksum(context)
        with open(self.checksum_file, 'w') as f:
            f.write(checksum)
        
        # 同时保存会话上下文（轻量级）
        with open(self.session_file, 'w') as f:
            json.dump({
                'timestamp': context['timestamp'],
                'ongoing_tasks_count': len(context['ongoing_tasks']),
                'pending_decisions_count': len(context['pending_decisions']),
                'file_queue_count': len(context['file_processing_queue'])
            }, f, indent=2)
        
        print(f"💾 完整上下文已保存")
        print(f"   进行中任务: {len(context['ongoing_tasks'])}个")
        print(f"   待决策事项: {len(context['pending_decisions'])}个")
        print(f"   文件队列: {len(context['file_processing_queue'])}个")
        
        return context
    
    def restore_context(self) -> Dict:
        """
        恢复上下文（会话开始时调用）
        
        Returns:
            恢复后的上下文，包含状态指示
        """
        if not os.path.exists(self.context_file):
            return {
                'status': 'no_previous_context',
                'message': '无历史上下文，可能是首次会话'
            }
        
        # 读取上下文
        with open(self.context_file, 'r') as f:
            content = f.read()
            context = json.loads(content)
        
        # 验证校验和
        current_checksum = hashlib.sha256(content.encode()).hexdigest()
        
        if os.path.exists(self.checksum_file):
            with open(self.checksum_file, 'r') as f:
                stored_checksum = f.read().strip()
            
            if current_checksum != stored_checksum:
                return {
                    'status': 'corrupted',
                    'message': '上下文校验失败！可能被篡改或损坏',
                    'action': '建议重新建立上下文'
                }
        
        # 计算时间差
        last_time = datetime.fromisoformat(context['timestamp'])
        time_diff = datetime.now() - last_time
        
        print(f"📂 恢复上一会话上下文")
        print(f"   上次时间: {context['timestamp']}")
        print(f"   时间间隔: {time_diff.days}天{time_diff.seconds//3600}小时")
        print(f"   进行中任务: {len(context.get('ongoing_tasks', []))}个")
        print(f"   待决策事项: {len(context.get('pending_decisions', []))}个")
        
        # 生成恢复后的行动建议
        recommendations = self._generate_recovery_recommendations(context)
        
        return {
            'status': 'restored',
            'context': context,
            'time_diff': str(time_diff),
            'recommendations': recommendations
        }
    
    def _generate_session_id(self) -> str:
        """生成会话ID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_part = hashlib.sha256(
            str(datetime.now().timestamp()).encode()
        ).hexdigest()[:8]
        return f"session_{timestamp}_{random_part}"
    
    def _generate_checksum(self, context: Dict) -> str:
        """生成上下文校验和"""
        content = json.dumps(context, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _get_ongoing_tasks(self) -> List[Dict]:
        """获取进行中任务"""
        # 从任务登记目录读取
        tasks = []
        task_dir = f"{self.workspace}/A-manyige/汇报"
        
        if os.path.exists(task_dir):
            for file in os.listdir(task_dir):
                if '任务登记' in file and file.endswith('.md'):
                    file_path = os.path.join(task_dir, file)
                    mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    tasks.append({
                        'name': file.replace('.md', ''),
                        'file': file,
                        'last_modified': mtime.isoformat(),
                        'status': 'ongoing'
                    })
        
        return sorted(tasks, key=lambda x: x['last_modified'], reverse=True)[:10]
    
    def _get_pending_decisions(self) -> List[Dict]:
        """获取待决策事项"""
        # 从决策索引读取
        decisions = []
        index_file = f"{self.workspace}/memory/.decision_index.json"
        
        if os.path.exists(index_file):
            with open(index_file, 'r') as f:
                index = json.load(f)
            
            for keyword, entries in index.items():
                for entry in entries[-3:]:  # 最近3条
                    decisions.append({
                        'keyword': keyword,
                        'type': entry.get('type', 'unknown'),
                        'weight': entry.get('weight', 0),
                        'timestamp': entry.get('timestamp', '')
                    })
        
        return sorted(decisions, key=lambda x: x.get('timestamp', ''), reverse=True)[:10]
    
    def _get_user_preferences(self) -> Dict:
        """获取用户偏好"""
        # 从USER.md解析
        preferences = {
            'communication_style': '简短有画面感',
            'decision_framework': '左脑风控+右脑直觉',
            'priority_system': 'P0立即/P1当日/P2本周/P3待定',
            'work_hours': '09:00-18:00核心时段'
        }
        
        # TODO: 实际从USER.md解析
        return preferences
    
    def _get_working_memory_snapshot(self) -> Dict:
        """获取工作记忆快照"""
        # 从.reflex_db读取
        reflex_state = {}
        reflex_file = f"{self.workspace}/.skill_reflex_db.json"
        
        if os.path.exists(reflex_file):
            with open(reflex_file, 'r') as f:
                reflex_state = json.load(f)
        
        return {
            'skill_reflexes': reflex_state,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_recent_decisions(self) -> List[Dict]:
        """获取最近决策"""
        decisions = []
        episodic_dir = f"{self.workspace}/memory/episodic"
        
        if os.path.exists(episodic_dir):
            # 读取最新的情景记忆文件
            files = sorted(
                [f for f in os.listdir(episodic_dir) if f.endswith('.jsonl')],
                reverse=True
            )
            
            if files:
                latest_file = os.path.join(episodic_dir, files[0])
                with open(latest_file, 'r') as f:
                    for line in f.readlines()[-5:]:  # 最近5条
                        try:
                            entry = json.loads(line)
                            decisions.append({
                                'memory_id': entry.get('memory_id', '')[:8],
                                'type': entry.get('decision', {}).get('type', 'unknown'),
                                'content': entry.get('decision', {}).get('content', '')[:50]
                            })
                        except:
                            pass
        
        return decisions
    
    def _get_file_queue(self) -> List[Dict]:
        """获取文件处理队列"""
        # 从重复检测索引读取
        queue = []
        index_file = f"{self.workspace}/.file_duplicates_index.json"
        
        if os.path.exists(index_file):
            with open(index_file, 'r') as f:
                index = json.load(f)
            
            for item in index.get('processing_order', []):
                if item.get('status') == '待处理':
                    queue.append({
                        'core_name': item['core_name'],
                        'file': item['file'],
                        'size': item.get('size', 0)
                    })
        
        return queue[:5]  # 最近5个待处理
    
    def _get_skill_reflex_state(self) -> Dict:
        """获取Skill反射状态"""
        reflex_file = f"{self.workspace}/.skill_reflex_db.json"
        
        if os.path.exists(reflex_file):
            with open(reflex_file, 'r') as f:
                return json.load(f)
        
        return {}
    
    def _generate_session_summary(self) -> str:
        """生成会话摘要"""
        # 基于当前状态生成
        tasks = self._get_ongoing_tasks()
        decisions = self._get_recent_decisions()
        
        summary = f"""上次会话摘要:
- 进行中任务: {len(tasks)}个
- 最近决策: {len(decisions)}个
- 保存时间: {datetime.now().isoformat()}
"""
        return summary
    
    def _generate_prerequisites(self) -> List[str]:
        """生成下一会话的前置检查清单"""
        return [
            "检查上一会话的待决策事项是否已解决",
            "确认用户偏好是否有变化",
            "验证进行中任务的状态",
            "回顾最近固化的决策",
            "检查文件处理队列进度"
        ]
    
    def _generate_recovery_recommendations(self, context: Dict) -> List[str]:
        """生成恢复后的建议"""
        recommendations = []
        
        ongoing_tasks = context.get('ongoing_tasks', [])
        if ongoing_tasks:
            recommendations.append(f"建议优先继续任务: {ongoing_tasks[0]['name']}")
        
        pending_decisions = context.get('pending_decisions', [])
        if pending_decisions:
            recommendations.append(f"有{len(pending_decisions)}个待决策事项需要确认")
        
        file_queue = context.get('file_processing_queue', [])
        if file_queue:
            recommendations.append(f"文件队列中有{len(file_queue)}个待处理文件")
        
        return recommendations
    
    def session_startup_check(self) -> bool:
        """会话启动检查"""
        print("\n📋 会话启动检查清单:")
        
        result = self.restore_context()
        
        if result['status'] == 'no_previous_context':
            print("   ℹ️ 无历史上下文，新会话开始")
            return True
        
        if result['status'] == 'corrupted':
            print(f"   ⚠️  {result['message']}")
            return False
        
        # 显示建议
        recommendations = result.get('recommendations', [])
        if recommendations:
            print("   💡 建议:")
            for rec in recommendations[:3]:
                print(f"      - {rec}")
        
        return True

if __name__ == "__main__":
    cpm = ContextPersistenceManager()
    
    print("=" * 60)
    print("🔧 上下文持久化管理器测试")
    print("=" * 60)
    
    # 测试保存
    print("\n[测试1] 保存上下文")
    context = cpm.save_full_context()
    
    # 测试恢复
    print("\n[测试2] 恢复上下文")
    result = cpm.restore_context()
    
    # 测试启动检查
    print("\n[测试3] 会话启动检查")
    cpm.session_startup_check()
    
    print("\n" + "=" * 60)
    print("✅ 上下文持久化管理器测试完成")
    print("=" * 60)
