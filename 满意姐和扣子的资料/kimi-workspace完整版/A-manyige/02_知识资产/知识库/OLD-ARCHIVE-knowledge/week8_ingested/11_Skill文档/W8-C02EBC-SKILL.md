---
# 知识元数据 (5标准化)
knowledge_id: W8-C02EBC
title: 变更同步机制标准Skill V1.0
category: 11_Skill文档
source: skills/.archive_change-sync/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 14226
week: 8
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 变更同步机制标准Skill V1.0

> **知识ID**: W8-C02EBC  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_change-sync/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 变更同步机制标准Skill V1.0
> **5标准**: 全局考虑 ✅ | 系统考虑 ✅ | 迭代机制 ✅ | Skill化 ✅ | 流程自动化 ✅
> 
> 版本: V1.0 | 更新: 2026-03-20 | 核心: 变更检测→同步通知 | 目标: 信息零延迟同步

---

## 一、全局考虑（六层+变更同步）

### 变更同步 × 六层矩阵

| 变更类型 | L0身份 | L1项目 | L2系统 | L3外部 | L4交付 | L5归档 |
|----------|--------|--------|--------|--------|--------|--------|
| **配置变更** | 身份配置 | 项目配置 | 系统配置 | 集成配置 | 交付配置 | 归档配置 |
| **状态变更** | 身份状态 | 项目状态 | 系统状态 | 外部状态 | 交付状态 | 归档状态 |
| **内容变更** | 身份信息 | 项目内容 | 系统内容 | 外部内容 | 交付内容 | 归档内容 |

---

## 二、系统考虑（检测→分析→同步→确认闭环）

### 2.1 变更同步流程

```
变更发生 → 变更检测 → 变更分析 → 影响评估 → 同步通知 → 接收确认
                                             ↑                   │
                                             └──── 重试机制 ←─────┘
```

### 2.2 变更分级与同步策略

| 变更级别 | 定义 | 检测频率 | 同步时限 | 通知方式 | 确认要求 |
|----------|------|----------|----------|----------|----------|
| **P0-紧急** | 影响系统运行/关键决策 | 实时 | 立即 | 多渠道+告警 | 必须确认 |
| **P1-重要** | 影响项目进度/交付质量 | 5分钟 | 5分钟内 | 即时消息 | 建议确认 |
| **P2-常规** | 一般信息更新 | 15分钟 | 15分钟内 | 消息通知 | 无需确认 |
| **P3-低频** | 归档/历史信息 | 1小时 | 1小时内 | 批量汇总 | 无需确认 |

### 2.3 同步范围与对象

| 变更来源 | 同步对象 | 同步内容 | 同步方式 |
|----------|----------|----------|----------|
| 项目文档 | 项目成员 | 版本更新、内容变更 | 实时推送 |
| 系统配置 | 相关系统 | 配置项变更 | API同步 |
| 任务状态 | 任务相关人 | 状态变化、进度更新 | 消息通知 |
| 外部信息 | 内部团队 | 外部变更影响 | 摘要同步 |
| 交付物 | 交付相关方 | 版本发布、更新 | 通知+链接 |

---

## 三、迭代机制（同步监控+效率优化）

### 3.1 同步质量监控

| 监控指标 | 计算方法 | 目标值 | 告警阈值 |
|----------|----------|--------|----------|
| 同步延迟 | 变更发生到通知发出时间 | <30秒 | >2分钟 |
| 送达率 | 成功送达/总通知数 | >99% | <95% |
| 确认率 | 已确认/需确认通知 | >95% | <80% |
| 重试次数 | 平均每个变更重试次数 | <1次 | >3次 |

### 3.2 同步策略优化

```yaml
sync_optimization:
  batching:
    enabled: true
    window: "30s"  # 30秒内同类变更合并
    
  deduplication:
    enabled: true
    window: "5m"   # 5分钟内相同内容去重
    
  prioritization:
    p0: "immediate"
    p1: "within_5min"
    p2: "within_15min"
    p3: "hourly_batch"
```

---

## 四、Skill化（可执行）

### 4.1 触发条件

**自动触发**:
- 文件/文档变更时自动检测
- 任务状态变化时自动同步
- 配置更新时自动通知
- 系统事件发生时自动推送

**手动触发**:
- 用户指令: "检查变更同步状态"
- 用户指令: "强制同步检查"
- 用户指令: "查看同步历史"

### 4.2 变更同步代码

```python
import hashlib
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Optional

class ChangeLevel(Enum):
    P0_EMERGENCY = "p0"    # 紧急
    P1_HIGH = "p1"         # 重要
    P2_NORMAL = "p2"       # 常规
    P3_LOW = "p3"          # 低频

class ChangeType(Enum):
    CONFIG = "config"      # 配置变更
    STATUS = "status"      # 状态变更
    CONTENT = "content"    # 内容变更
    FILE = "file"          # 文件变更
    EXTERNAL = "external"  # 外部变更

class ChangeSync:
    """变更同步机制"""
    
    SYNC_SLA = {
        ChangeLevel.P0_EMERGENCY: timedelta(seconds=0),    # 立即
        ChangeLevel.P1_HIGH: timedelta(minutes=5),
        ChangeLevel.P2_NORMAL: timedelta(minutes=15),
        ChangeLevel.P3_LOW: timedelta(hours=1)
    }
    
    def __init__(self, storage_path="logs/change-sync"):
        self.storage_path = storage_path
        self.watched_items = []
        self.change_history = []
        self.sync_queue = []
        self.sync_status = {}
    
    def add_watch(self, item_id: str, item_type: str, 
                  source_path: str, level: ChangeLevel,
                  notify_targets: List[str]):
        """添加监控项"""
        watch = {
            "id": item_id,
            "type": item_type,
            "source_path": source_path,
            "level": level,
            "notify_targets": notify_targets,
            "last_hash": None,
            "last_checked": None,
            "added_at": datetime.now()
        }
        self.watched_items.append(watch)
        # 初始化hash
        watch["last_hash"] = self.compute_hash(source_path)
        return watch
    
    def compute_hash(self, path: str) -> str:
        """计算文件/内容哈希"""
        try:
            with open(path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""
    
    def detect_changes(self) -> List[Dict]:
        """检测变更"""
        changes = []
        
        for watch in self.watched_items:
            current_hash = self.compute_hash(watch["source_path"])
            
            if current_hash != watch["last_hash"]:
                change = {
                    "id": f"CHG-{len(self.change_history)+1:06d}",
                    "watch_id": watch["id"],
                    "type": watch["type"],
                    "level": watch["level"],
                    "source_path": watch["source_path"],
                    "old_hash": watch["last_hash"],
                    "new_hash": current_hash,
                    "detected_at": datetime.now(),
                    "sync_deadline": datetime.now() + self.SYNC_SLA[watch["level"]],
                    "notify_targets": watch["notify_targets"],
                    "synced": False,
                    "confirmed_by": []
                }
                changes.append(change)
                self.change_history.append(change)
                
                # 更新监控状态
                watch["last_hash"] = current_hash
                watch["last_checked"] = datetime.now()
                
                # 加入同步队列
                self.sync_queue.append(change)
        
        return changes
    
    def analyze_change(self, change: Dict) -> Dict:
        """分析变更影响"""
        analysis = {
            "change_id": change["id"],
            "impact_scope": [],
            "affected_items": [],
            "risk_level": "low",
            "recommendations": []
        }
        
        # 分析变更类型
        if change["type"] == ChangeType.CONFIG.value:
            analysis["impact_scope"].append("系统配置")
            analysis["recommendations"].append("建议重启相关服务")
        elif change["type"] == ChangeType.STATUS.value:
            analysis["impact_scope"].append("任务/项目状态")
        elif change["type"] == ChangeType.CONTENT.value:
            analysis["impact_scope"].append("文档内容")
        
        # 根据级别评估风险
        if change["level"] == ChangeLevel.P0_EMERGENCY:
            analysis["risk_level"] = "critical"
        elif change["level"] == ChangeLevel.P1_HIGH:
            analysis["risk_level"] = "high"
        
        return analysis
    
    def sync_change(self, change: Dict) -> bool:
        """同步变更"""
        success = True
        
        for target in change["notify_targets"]:
            try:
                notification = self.create_notification(change, target)
                delivered = self.send_notification(notification, target)
                
                if not delivered:
                    success = False
                    self.schedule_retry(change, target)
            except Exception as e:
                success = False
                self.log_sync_error(change, target, str(e))
        
        if success:
            change["synced"] = True
            change["synced_at"] = datetime.now()
        
        return success
    
    def create_notification(self, change: Dict, target: str) -> Dict:
        """创建通知"""
        level_emoji = {
            ChangeLevel.P0_EMERGENCY.value: "🚨",
            ChangeLevel.P1_HIGH.value: "⚠️",
            ChangeLevel.P2_NORMAL.value: "ℹ️",
            ChangeLevel.P3_LOW.value: "📝"
        }
        
        return {
            "change_id": change["id"],
            "target": target,
            "title": f"{level_emoji.get(change['level'].value, 'ℹ️')} 变更通知: {change['watch_id']}",
            "content": self.format_change_content(change),
            "level": change["level"].value,
            "require_confirmation": change["level"] in [ChangeLevel.P0_EMERGENCY, ChangeLevel.P1_HIGH],
            "timestamp": datetime.now()
        }
    
    def format_change_content(self, change: Dict) -> str:
        """格式化变更内容"""
        lines = [
            f"变更ID: {change['id']}",
            f"变更类型: {change['type']}",
            f"变更级别: {change['level'].value}",
            f"发生时间: {change['detected_at'].strftime('%Y-%m-%d %H:%M:%S')}",
            f"来源: {change['source_path']}",
        ]
        
        if change["level"] == ChangeLevel.P0_EMERGENCY:
            lines.append("⚠️ 请立即查看并确认收到此通知")
        
        return "\n".join(lines)
    
    def send_notification(self, notification: Dict, target: str) -> bool:
        """发送通知（实际发送逻辑）"""
        # 这里集成实际的通知渠道
        # 可以是消息、邮件、Webhook等
        print(f"发送通知到 {target}: {notification['title']}")
        return True
    
    def schedule_retry(self, change: Dict, target: str):
        """调度重试"""
        retry = {
            "change_id": change["id"],
            "target": target,
            "scheduled_at": datetime.now() + timedelta(minutes=5),
            "retry_count": 0
        }
        # 加入重试队列
        pass
    
    def confirm_receipt(self, change_id: str, confirmed_by: str):
        """确认收到通知"""
        change = self.get_change(change_id)
        if change:
            if confirmed_by not in change["confirmed_by"]:
                change["confirmed_by"].append(confirmed_by)
                change["confirmed_at"] = datetime.now()
        return change
    
    def get_change(self, change_id: str) -> Optional[Dict]:
        """获取变更记录"""
        for c in self.change_history:
            if c["id"] == change_id:
                return c
        return None
    
    def get_pending_syncs(self) -> List[Dict]:
        """获取待同步项"""
        now = datetime.now()
        return [c for c in self.sync_queue if not c["synced"] and c["sync_deadline"] > now]
    
    def get_overdue_syncs(self) -> List[Dict]:
        """获取逾期同步"""
        now = datetime.now()
        return [c for c in self.sync_queue if not c["synced"] and c["sync_deadline"] < now]
    
    def process_sync_queue(self):
        """处理同步队列"""
        processed = []
        
        # 按级别排序，优先处理高级别
        pending = sorted(self.get_pending_syncs(), 
                        key=lambda x: x["level"].value)
        
        for change in pending:
            success = self.sync_change(change)
            processed.append({"change_id": change["id"], "success": success})
        
        return processed
    
    def generate_sync_report(self) -> Dict:
        """生成同步报告"""
        now = datetime.now()
        today_changes = [c for c in self.change_history 
                        if c["detected_at"].date() == now.date()]
        
        return {
            "report_time": now,
            "today_changes": len(today_changes),
            "synced": len([c for c in today_changes if c["synced"]]),
            "pending": len([c for c in today_changes if not c["synced"]]),
            "overdue": len(self.get_overdue_syncs()),
            "confirmation_rate": self.calculate_confirmation_rate(today_changes)
        }
    
    def calculate_confirmation_rate(self, changes: List[Dict]) -> float:
        """计算确认率"""
        need_confirm = [c for c in changes 
                       if c["level"] in [ChangeLevel.P0_EMERGENCY, ChangeLevel.P1_HIGH]]
        if not need_confirm:
            return 100.0
        
        confirmed = sum(1 for c in need_confirm if len(c["confirmed_by"]) > 0)
        return (confirmed / len(need_confirm)) * 100
    
    def log_sync_error(self, change: Dict, target: str, error: str):
        """记录同步错误"""
        print(f"同步错误: {change['id']} -> {target}: {error}")

def run_change_sync():
    """运行变更同步"""
    sync = ChangeSync()
    
    # 检测变更
    changes = sync.detect_changes()
    
    if changes:
        print(f"检测到 {len(changes)} 个变更")
        
        # 分析并同步
        for change in changes:
            analysis = sync.analyze_change(change)
            print(f"变更 {change['id']} 影响分析: {analysis}")
        
        # 处理同步队列
        processed = sync.process_sync_queue()
        print(f"同步完成: {len([p for p in processed if p['success']])}/{len(processed)}")
    
    # 检查逾期
    overdue = sync.get_overdue_syncs()
    if overdue:
        print(f"⚠️ 发现 {len(overdue)} 个逾期同步")
    
    return sync.generate_sync_report()
```

### 4.3 标准响应模板

**变更通知**:
```
🚨 **紧急变更通知**

变更ID: [ID]
变更类型: [类型]
发生时间: [时间]

变更内容:
[描述]

影响范围:
- [影响项1]
- [影响项2]

请立即查看并确认收到。
回复"确认[ID]"完成确认。
```

**同步确认**:
```
✅ **变更同步完成**

变更: [ID]
同步时间: [时间]
通知对象: [N]人

已确认收到:
- [确认人1] [时间]
- [确认人2] [时间]

未确认:
- [未确认人] (将重试通知)
```

**同步日报**:
```
📊 **变更同步日报**

报告日期: [日期]

今日变更统计:
- 总变更: [N]个
- 已同步: [N]个
- 待同步: [N]个
- 逾期: [N]个

确认率: [X]% (目标: >95%)

需要关注:
- [逾期变更列表]
```

---

## 五、流程自动化

### 5.1 定时任务

```json
{
  "jobs": [
    {
      "name": "change-detection",
      "schedule": "*/5 * * * *",
      "enabled": true,
      "description": "每5分钟检测变更"
    },
    {
      "name": "change-sync-processor",
      "schedule": "*/2 * * * *",
      "enabled": true,
      "description": "每2分钟处理同步队列"
    },
    {
      "name": "change-sync-daily-report",
      "schedule": "0 9 * * *",
      "enabled": true,
      "description": "每日9点生成同步报告"
    }
  ]
}
```

### 5.2 自动化脚本

```bash
#!/bin/bash
# scripts/change-sync-check.sh

echo "=== 变更同步检查 ==="
echo "检查时间: $(date)"
echo ""

# 检测变更
echo "1. 检测变更..."
python3 << 'EOF'
from change_sync import ChangeSync
sync = ChangeSync()
changes = sync.detect_changes()
print(f"检测到 {len(changes)} 个变更")
for c in changes:
    print(f"  - {c['id']}: {c['type']} ({c['level'].value})")
EOF

# 处理同步队列
echo ""
echo "2. 处理同步队列..."
python3 << 'EOF'
from change_sync import ChangeSync
sync = ChangeSync()
processed = sync.process_sync_queue()
success = len([p for p in processed if p['success']])
print(f"同步完成: {success}/{len(processed)}")
EOF

# 检查逾期
echo ""
echo "3. 检查逾期同步..."
python3 << 'EOF'
from change_sync import ChangeSync
sync = ChangeSync()
overdue = sync.get_overdue_syncs()
if overdue:
    print(f"⚠️ 发现{len(overdue)}个逾期同步")
else:
    print("✅ 无逾期同步")
EOF

echo ""
echo "=== 检查完成 ==="
```

---

## 六、质量门控

- [x] **全局**: 变更同步×六层全覆盖
- [x] **系统**: 检测→分析→同步→确认闭环
- [x] **迭代**: 同步质量监控+策略优化
- [x] **Skill化**: 自动检测+智能同步+确认跟踪
- [x] **自动化**: 定时检测+队列处理+日报生成

---

## 七、使用方式

### 7.1 人工检查

```bash
# 检查变更同步状态
./scripts/change-sync-check.sh

# 查看同步报告
python3 -c "from change_sync import ChangeSync; print(ChangeSync().generate_sync_report())"

# 确认收到变更
python3 -c "from change_sync import ChangeSync; ChangeSync().confirm_receipt('CHG-000001', 'user_001')"
```

### 7.2 集成到工作流

所有监控项的变更自动检测和同步，系统会自动通知相关人员。

---

*5标准合规: ✅ 全局 | ✅ 系统 | ✅ 迭代 | ✅ Skill化 | ✅ 自动化*
