---
# 知识元数据 (5标准化)
knowledge_id: W17-E21EB0
title: vendor-api-monitor Skill V5标准版本
category: 11_Skill文档
source: skills/vendor-api-monitor/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1032
week: 17
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# vendor-api-monitor Skill V5标准版本

> **知识ID**: W17-E21EB0  
> **分类**: 11_Skill文档  
> **来源**: `skills/vendor-api-monitor/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# vendor-api-monitor Skill V5标准版本

## S1: 全局考虑

### 输入
- 第三方API端点列表
- 监控频率配置
- 告警阈值

### 覆盖维度
| 维度 | 考虑内容 |
|------|----------|
| **人** | 系统运维、依赖管理人员 |
| **事** | API可用性监控、响应时间追踪、依赖健康度评估 |
| **物** | API端点、监控数据、告警记录 |
| **环境** | 网络环境、API配额、服务商状态 |
| **外部集成** | 各第三方API服务 |
| **边界情况** | API限流、服务降级、文档变更 |

---

## S2: 系统考虑

### 处理流程
```
端点配置 → 定期探测 → 健康评估 → 告警通知 → 趋势报告
```

### 故障处理
- **API限流**: 降低探测频率
- **服务降级**: 标记降级状态，调整期望
- **文档变更**: 检测响应格式变化

---

## S3: 输出规范

### 监控报告
```json
{
  "api": "vendor_name",
  "endpoint": "https://api.vendor.com/v1/health",
  "status": "healthy|degraded|down",
  "response_time_ms": 150,
  "success_rate_24h": 99.5,
  "last_incident": "2026-03-20T10:00:00Z"
}
```

---

## S4: 自动化集成

### 监控频率
- 关键API: 每5分钟
- 普通API: 每15分钟
- 报告: 每日汇总

---

## S5: 自我验证

### 质量指标
- 探测准确率: >99%
- 告警及时性: <2分钟
- 误报率: <1%

---

## S6: 认知谦逊

### 局限
- 只能探测公开端点
- 无法获知服务商内部状态
- 受网络环境影响

---

## S7: 对抗测试

| 场景 | 预期行为 |
|------|----------|
| API完全下线 | 立即告警 |
| 间歇性故障 | 记录模式，趋势告警 |
| 响应变慢 | 降级标记，非紧急告警 |
| 限流触发 | 自适应降低探测频率 |
