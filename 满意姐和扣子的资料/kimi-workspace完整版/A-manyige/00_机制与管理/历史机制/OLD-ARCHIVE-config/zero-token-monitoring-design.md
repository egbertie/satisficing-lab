# 零Token消耗监控体系设计方案

**设计原则**: 监控 ≠ AI交互，Token消耗仅发生在AI对话环节

---

## 一、GC监控与Token消耗

### 答案：不增加Token消耗

| 监控类型 | 是否消耗Token | 原因 |
|----------|---------------|------|
| GC频率/时长监控 | ❌ 否 | 系统级指标，纯代码采集 |
| 内存使用率监控 | ❌ 否 | 系统调用，无AI交互 |
| Token使用量监控 | ❌ 否 | 本地计数，周期性写入文件 |
| **向AI报告异常** | ✅ 是 | 仅在触发阈值时产生AI对话 |

**关键区分**:
- **采集监控数据** → 零Token（纯技术操作）
- **AI分析/报告** → 消耗Token（仅在必要时触发）

---

## 二、内存监控 vs 持久化

### 现状问题

| 存储位置 | 重启后 | 适用场景 | 我们现在的状况 |
|----------|--------|----------|----------------|
| 纯内存变量 | ❌ 丢失 | 临时计数 | 部分监控在此 |
| 内存+定期写文件 | ✅ 保留 | 关键指标 | **应采用此模式** |
| 数据库/日志 | ✅ 保留 | 历史分析 | 未启用 |

### 正确做法

```python
# 错误：纯内存
request_count = 0  # 重启丢失

# 正确：内存+延迟持久化
request_count = 0
# ... 累积100次或每5分钟 ...
append_to_file(f"{timestamp},{count}")  # 持久化
```

---

## 三、零Token消耗监控体系

### 层级设计

```
┌─────────────────────────────────────────┐
│  L1: 系统级监控（Linux原生，零开销）       │
│  - CPU/内存/磁盘/网络                     │
│  - 工具：free, top, vmstat, iostat       │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  L2: 应用级监控（文件持久化，零Token）     │
│  - 请求计数/错误率/响应时间               │
│  - 存储：本地JSON/文本文件               │
│  - 频率：批量写入（非实时）               │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  L3: AI级监控（阈值触发，控制频率）        │
│  - 仅当异常时触发AI报告                   │
│  - 阈值：内存>85%，错误率>5%等            │
│  - 冷却期：同一问题30分钟内不重复报告      │
└─────────────────────────────────────────┘
```

### 具体实施方案

#### 1. 系统级（无Token）

```bash
# 内存监控脚本 - 纯Shell，零Token
cat > /root/.openclaw/scripts/memory-monitor.sh << 'EOF'
#!/bin/bash
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100)}')
echo "$(date '+%Y-%m-%d %H:%M'),${MEMORY_USAGE}" >> /var/log/memory.log

if [ "$MEMORY_USAGE" -gt 85 ]; then
    # 仅记录，不触发AI
    echo "$(date) - 内存告警: ${MEMORY_USAGE}%" >> /var/log/memory-alerts.log
fi
EOF

# 每5分钟执行一次
echo "*/5 * * * * /root/.openclaw/scripts/memory-monitor.sh" | crontab -
```

#### 2. 应用级（无Token）

```python
# openclaw-gateway内部监控 - 批量写入
class ZeroTokenMonitor:
    def __init__(self):
        self.batch = []
        self.batch_size = 100
        self.last_write = time.time()
    
    def record(self, metric_type, value):
        # 纯内存累积
        self.batch.append({
            'time': time.time(),
            'type': metric_type,
            'value': value
        })
        
        # 批量条件：100条或5分钟
        if len(self.batch) >= self.batch_size or \
           time.time() - self.last_write > 300:
            self._flush()
    
    def _flush(self):
        # 写入文件，无AI交互
        with open('/var/log/openclaw-metrics.jsonl', 'a') as f:
            for item in self.batch:
                f.write(json.dumps(item) + '\n')
        self.batch = []
        self.last_write = time.time()
```

#### 3. AI级（阈值控制）

```python
class AIAlertManager:
    def __init__(self):
        self.cooldown = {}  # 冷却期记录
    
    def should_alert(self, alert_type):
        # 同一类型30分钟内只报告一次
        last_time = self.cooldown.get(alert_type, 0)
        if time.time() - last_time < 1800:
            return False
        self.cooldown[alert_type] = time.time()
        return True
    
    def alert_memory_high(self, usage):
        if usage > 85 and self.should_alert('memory_high'):
            # 此时才触发AI交互
            send_to_ai(f"内存使用率{usage}%，建议处理")
```

---

## 四、我们的监控缺口

| 监控项 | 当前状态 | 应对方案 | Token消耗 |
|--------|----------|----------|-----------|
| Token周消耗 | ✅ 已部署 | 文件记录 | 零 |
| 内存使用率 | ❌ 缺失 | Shell脚本+文件 | 零 |
| GC频率/时长 | ❌ 缺失 | Node.js内置API | 零 |
| 响应延迟 | ❌ 缺失 | 应用层记录 | 零 |
| 错误率 | ❌ 缺失 | 应用层记录 | 零 |
| 异常告警 | ❌ 缺失 | 阈值触发+冷却期 | 可控 |

---

## 五、立即执行的监控补强

### 1. 部署内存监控（5分钟，零Token）

```bash
# 创建监控脚本
mkdir -p /root/.openclaw/scripts
cat > /root/.openclaw/scripts/system-monitor.sh << 'EOF'
#!/bin/bash
LOG_DIR="/root/.openclaw/logs"
mkdir -p $LOG_DIR

# 内存监控
MEMORY=$(free | awk '/Mem:/ {printf("%.1f", $3/$2*100)}')
echo "$(date '+%Y-%m-%d %H:%M:%S'),memory,${MEMORY}" >> $LOG_DIR/system-metrics.csv

# 负载监控
LOAD=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')
echo "$(date '+%Y-%m-%d %H:%M:%S'),load,${LOAD}" >> $LOG_DIR/system-metrics.csv
EOF

chmod +x /root/.openclaw/scripts/system-monitor.sh

# 每2分钟执行
echo "*/2 * * * * /root/.openclaw/scripts/system-monitor.sh" | crontab -
```

### 2. 部署GC监控（Node.js应用层）

在openclaw-gateway启动时添加：

```javascript
// 零Token消耗GC监控
const v8 = require('v8');
const fs = require('fs');

let gcStats = {
    count: 0,
    totalDuration: 0,
    lastGC: Date.now()
};

// 使用 performanceObserver 监控GC（Node.js v16+）
const { PerformanceObserver } = require('perf_hooks');

const obs = new PerformanceObserver((list) => {
    const entry = list.getEntries()[0];
    gcStats.count++;
    gcStats.totalDuration += entry.duration;
    
    // 批量写入（每10次或5分钟）
    if (gcStats.count % 10 === 0) {
        const log = `${new Date().toISOString()},gc_count,${gcStats.count},gc_duration,${gcStats.totalDuration}\n`;
        fs.appendFileSync('/root/.openclaw/logs/gc-metrics.csv', log);
    }
});

obs.observe({ entryTypes: ['gc'] });
```

### 3. 异常告警触发器（可控Token）

```bash
# 告警检查脚本
cat > /root/.openclaw/scripts/alert-checker.sh << 'EOF'
#!/bin/bash
ALERT_STATE="/root/.openclaw/logs/alert-state.json"
MEMORY=$(free | awk '/Mem:/ {printf("%.0f", $3/$2*100)}')

# 内存>85%触发告警
if [ "$MEMORY" -gt 85 ]; then
    LAST_ALERT=$(cat $ALERT_STATE 2>/dev/null | grep memory_high | cut -d: -f2 || echo 0)
    NOW=$(date +%s)
    
    # 30分钟冷却期
    if [ $((NOW - LAST_ALERT)) -gt 1800 ]; then
        # 此时才需要AI交互（通过消息或其他方式）
        echo "{\"memory_high\":$NOW}" > $ALERT_STATE
        # 触发告警...
    fi
fi
EOF
```

---

## 六、总结

| 问题 | 答案 |
|------|------|
| GC监控增加Token？ | 否，纯技术监控 |
| 内存监控重启丢失？ | 当前部分会丢失，应改为文件持久化 |
| 有效的零Token监控？ | 系统级+应用级文件记录，AI仅异常时触发 |

**核心原则**: 监控是技术问题，不是AI问题。让监控留在技术层，只有需要决策时才调用AI。

---

**下一步**: 部署上述监控脚本

## 知识内化记录
**内化时间**: 2026-03-31 | **状态**: ✅ 已内化
