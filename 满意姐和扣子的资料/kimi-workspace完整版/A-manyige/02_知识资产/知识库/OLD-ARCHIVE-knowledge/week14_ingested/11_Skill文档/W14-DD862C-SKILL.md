---
# 知识元数据 (5标准化)
knowledge_id: W14-DD862C
title: api-monitor Skill V5标准版本
category: 11_Skill文档
source: skills/api-monitor/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 2312
week: 14
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# api-monitor Skill V5标准版本

> **知识ID**: W14-DD862C  
> **分类**: 11_Skill文档  
> **来源**: `skills/api-monitor/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# api-monitor Skill V5标准版本

## S1: 全局考虑（输入→边界→覆盖）

### 输入
- API端点URL
- 监控频率配置
- 告警阈值

### 覆盖维度
| 维度 | 考虑内容 |
|------|----------|
| **人** | 运维人员接收告警、开发人员排查 |
| **事** | API可用性监控、响应时间追踪、错误率统计 |
| **物** | HTTP端点、响应状态码、响应时间 |
| **环境** | 网络环境、时区、频率配置 |
| **外部集成** | Webhook通知、日志记录 |
| **边界情况** | 超时、重试、网络中断、API变更 |

---

## S2: 系统考虑（闭环+故障处理）

### 处理流程
```
配置加载 → 定期检测 → 结果记录 → 异常判断 → 告警通知 → 日志归档
    ↑                                              ↓
    └──────────── 状态报告 ← 趋势分析 ←────────────┘
```

### 故障处理
- **检测失败**: 重试3次后告警
- **网络超时**: 标记为timeout，记录时间戳
- **API变更**: 响应格式校验失败时告警

---

## S3: 输出规范（可观测+可验证）

### 监控报告格式
```json
{
  "timestamp": "2026-03-22T09:00:00+08:00",
  "endpoint": "https://api.example.com/health",
  "status": "up|down|degraded",
  "response_time_ms": 120,
  "status_code": 200,
  "checks": {
    "total": 100,
    "success": 98,
    "failed": 2
  }
}
```

### 告警输出
- P0: API完全不可用（立即通知）
- P1: 响应时间>阈值（延迟通知）
- P2: 错误率上升（日报汇总）

---

## S4: 自动化集成

### Cron集成
```
每5分钟执行一次检测
每1小时生成趋势报告
每日09:00发送监控日报
```

### 脚本位置
- `scripts/api_monitor.py` - 主监控脚本
- `config/endpoints.json` - 端点配置
- `logs/` - 监控日志目录

---

## S5: 自我验证（指标+测试）

### 质量指标
| 指标 | 目标 | 验证方法 |
|------|------|----------|
| 检测准确率 | >99% | 人工抽查 |
| 告警及时性 | <1分钟 | 模拟故障测试 |
| 误报率 | <1% | 统计告警有效性 |

### 测试用例
1. 正常API返回200 → 标记up
2. API返回500 → 标记down，触发告警
3. 网络超时 → 标记timeout，重试3次
4. 配置错误 → 启动时检查并报错

---

## S6: 认知谦逊（局限标注）

### 无法检测的情况
- API逻辑错误但返回200（需业务层检测）
- 第三方依赖故障但API正常（需链式监控）
- 性能退化但仍在阈值内（需趋势分析）

### 依赖假设
- 网络可达
- DNS解析正常
- 本地时间准确

---

## S7: 对抗测试（失效场景）

### 测试场景
| 场景 | 预期行为 |
|------|----------|
| 目标API完全下线 | 3次重试后标记down，触发P0告警 |
| 目标API间歇性故障 | 记录故障模式，生成趋势报告 |
| 监控脚本自身故障 | 启动自检，失败时退出并报错 |
| 配置端点不存在 | 启动时校验，失败时退出 |
| 磁盘空间不足 | 日志轮转，保留最近7天 |

---

## 使用说明

### 快速开始
```bash
# 配置监控端点
edit config/endpoints.json

# 手动执行监控
python3 scripts/api_monitor.py check

# 查看监控状态
python3 scripts/api_monitor.py status

# 生成日报
python3 scripts/api_monitor.py report --daily
```

### 配置文件
```json
{
  "endpoints": [
    {
      "name": "Kimi API",
      "url": "https://api.moonshot.cn/v1/models",
      "method": "GET",
      "headers": {"Authorization": "Bearer $KIMI_API_KEY"},
      "timeout": 10,
      "expected_status": 200,
      "alert_threshold": {
        "response_time_ms": 5000,
        "error_rate": 0.05
      }
    }
  ]
}
```
