# 多子代理并行架构设计 V1.0

> **设计时间**: 2026-03-31 10:56  
> **目标**: 支持最多8个子代理并行处理知识入库  
> **安全防范**: Token限制、超时控制、失败重试

---

## 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    Meta-Scheduler (调度器)                    │
│                 负责任务分发、结果汇总、异常处理                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Sub-Agent-1  │    │ Sub-Agent-2  │    │ Sub-Agent-N  │
│ (文件001-050) │    │ (文件051-100) │    │ (最大8个)    │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                           ▼
              ┌─────────────────────┐
              │    Result-Merger    │
              │    (结果合并器)      │
              └─────────────────────┘
```

---

## 安全防范机制

### 1. Token限制

| 限制项 | 数值 | 说明 |
|--------|------|------|
| 最大并发子代理 | 8个 | 防止Token耗尽 |
| 每子代理Token预算 | 20K | 超出则暂停 |
| 全局Token预算 | 100K/日 | 超出则停止新任务 |

### 2. 超时控制

| 超时类型 | 时间 | 动作 |
|----------|------|------|
| 单个子代理 | 10分钟 | 强制终止，标记失败 |
| 整批任务 | 1小时 | 强制终止，回滚已处理 |
| 全局超时 | 4小时 | 紧急停止，保存状态 |

### 3. 失败重试

| 参数 | 数值 | 说明 |
|------|------|------|
| 最大重试次数 | 3次 | 超过则放弃 |
| 重试间隔 | 30秒 | 指数退避 |
| 失败阈值 | 20% | 超过则整批失败 |

---

## 调度算法

### 任务分配策略

```python
def assign_tasks(files, max_workers=8, batch_size=50):
    """
    任务分配算法
    
    Args:
        files: 待处理文件列表
        max_workers: 最大工作者数
        batch_size: 每批次文件数
    
    Returns:
        batches: 分配好的批次列表
    """
    batches = []
    total_files = len(files)
    
    # 计算需要的批次数
    num_batches = min(
        (total_files + batch_size - 1) // batch_size,  # 向上取整
        max_workers  # 不超过最大工作者数
    )
    
    # 分配文件到批次
    for i in range(num_batches):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, total_files)
        batch = files[start_idx:end_idx]
        batches.append({
            "batch_id": i + 1,
            "files": batch,
            "worker_id": f"worker-{i+1}"
        })
    
    return batches
```

### 结果合并策略

1. **成功结果**: 直接合并到主索引
2. **失败结果**: 记录失败文件，进入重试队列
3. **部分成功**: 分离成功/失败，分别处理
4. **超时结果**: 标记为待处理，下一批次重试

---

## 实现代码框架

### 调度器 (scheduler.py)

```python
#!/usr/bin/env python3
"""
多子代理并行调度器
立即执行版 - 2026-03-31
"""

import concurrent.futures
import time
from datetime import datetime

class MultiAgentScheduler:
    """多子代理调度器"""
    
    def __init__(self, max_workers=8, timeout=600):
        self.max_workers = max_workers
        self.timeout = timeout
        self.results = []
        self.failures = []
    
    def dispatch(self, batches):
        """分发任务到子代理"""
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            # 提交所有任务
            future_to_batch = {
                executor.submit(self.process_batch, batch): batch
                for batch in batches
            }
            
            # 收集结果
            for future in concurrent.futures.as_completed(future_to_batch):
                batch = future_to_batch[future]
                try:
                    result = future.result(timeout=self.timeout)
                    self.results.append(result)
                except Exception as e:
                    self.failures.append({
                        "batch": batch,
                        "error": str(e)
                    })
    
    def process_batch(self, batch):
        """处理单个批次（由子代理执行）"""
        # 调用知识入库Skill处理批次
        pass
    
    def merge_results(self):
        """合并所有子代理结果"""
        pass
```

---

## 检查清单

- [x] 架构设计文档
- [ ] 调度器实现代码
- [ ] 结果合并器实现
- [ ] Token限制逻辑
- [ ] 超时控制逻辑
- [ ] 失败重试逻辑
- [ ] 集成测试

---
*多子代理并行架构 - 立即执行版*
