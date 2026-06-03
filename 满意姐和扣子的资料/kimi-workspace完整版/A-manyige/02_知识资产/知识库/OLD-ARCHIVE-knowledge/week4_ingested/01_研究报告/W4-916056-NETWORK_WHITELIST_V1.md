---
# 知识元数据 (5标准化)
knowledge_id: W4-916056
title: 网络请求白名单 V1.0
category: 01_研究报告
source: docs/NETWORK_WHITELIST_V1.md
ingested_at: 2026-03-27 17:59:30
word_count: 2866
week: 4
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 网络请求白名单 V1.0

> **知识ID**: W4-916056  
> **分类**: 01_研究报告  
> **来源**: `docs/NETWORK_WHITELIST_V1.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 网络请求白名单 V1.0
> 安全修复：扩展供应链风险控制
> 
> 创建时间: 2026-03-21
> 审核状态: 待蓝军审阅

---

## 一、白名单策略

### 1.1 安全原则

| 原则 | 说明 |
|------|------|
| **最小权限** | 只开放必要的网络访问 |
| **明确授权** | 每个域名必须说明用途和负责人 |
| **定期审计** | 每月审查白名单，移除不再使用的域名 |
| **异常告警** | 非白名单请求触发告警 |

### 1.2 域名分级

| 级别 | 说明 | 示例 |
|------|------|------|
| **P0 核心** | 系统运行必需 | github.com, api.moonshot.cn |
| **P1 业务** | 主要业务功能 | jina.ai, platform.moonshot.cn |
| **P2 辅助** | 非核心功能 | 天气API, 资讯API |
| **P3 临时** | 短期使用，需定期清理 | 实验性服务 |

---

## 二、已授权域名白名单

### P0 核心域名（系统运行必需）

| 域名 | 用途 | 负责人 | 状态 |
|------|------|--------|------|
| `github.com` | GitHub API, Models, 代码托管 | 满意妞 | ✅ 已授权 |
| `api.github.com` | GitHub REST API | 满意妞 | ✅ 已授权 |
| `models.inference.ai.azure.com` | GitHub Models端点 | 满意妞 | ✅ 已授权 |
| `api.moonshot.cn` | Kimi API | 满意妞 | ✅ 已授权 |

### P1 业务域名（主要业务功能）

| 域名 | 用途 | 负责人 | 状态 |
|------|------|--------|------|
| `r.jina.ai` | Jina AI网页提取 | 满意妞 | ✅ 已授权 |
| `jina.ai` | Jina AI官网/API | 满意妞 | ✅ 已授权 |
| `platform.moonshot.cn` | Kimi平台管理 | 满意妞 | ✅ 已授权 |
| `console.anthropic.com` | Claude API管理（当前403） | 满意妞 | ⚠️ 待恢复 |

### P2 辅助域名（非核心功能）

| 域名 | 用途 | 负责人 | 状态 |
|------|------|--------|------|
| `www.example.com` | 示例/测试 | 满意妞 | ✅ 已授权 |
| `httpbin.org` | HTTP测试 | 满意妞 | ✅ 已授权 |

---

## 三、禁止访问的域名

### 明确禁止（高风险）

| 域名/模式 | 风险 | 原因 |
|-----------|------|------|
| `*.onion` | 极高 | 暗网 |
| `localhost:*` | 高 | 本地服务暴露 |
| `127.0.0.1:*` | 高 | 本地服务暴露 |
| `*.internal` | 中 | 内网穿透风险 |
| 未在白名单的域名 | 中 | 供应链风险 |

---

## 四、监控与告警

### 4.1 异常请求检测

```yaml
detection_rules:
  - name: 非白名单请求
    condition: domain NOT IN whitelist
    action: block + alert
    severity: high
    
  - name: P0域名异常流量
    condition: P0_domain_request_rate > 1000/min
    action: rate_limit + alert
    severity: medium
    
  - name: 新域名首次访问
    condition: new_domain_detected
    action: alert + require_approval
    severity: low
```

### 4.2 审计日志

所有网络请求记录：
- 时间戳
- 来源（Skill/脚本）
- 目标域名
- 请求类型
- 是否在白名单
- 处理结果

---

## 五、扩展流程

### 5.1 新增域名申请

```
1. 填写申请表（域名、用途、负责人）
2. 安全评估（风险等级）
3. 蓝军审核
4. 添加到白名单
5. 更新文档
```

### 5.2 申请表模板

```yaml
new_domain_request:
  domain: "api.example.com"
  purpose: "获取XX数据"
  owner: "满意妞"
  skill: "example-skill"
  data_classification: "公开/内部/敏感"
  request_frequency: "每日100次"
  risk_assessment: "低风险，公开API"
  alternative: "是否有替代方案"
```

---

## 六、定期审计

### 6.1 审计周期

| 审计类型 | 频率 | 负责人 |
|----------|------|--------|
| 白名单使用审查 | 每月 | 满意妞 |
| 域名安全状态 | 每季度 | 蓝军 |
| 全量网络请求审计 | 每半年 | 蓝军+满意妞 |

### 6.2 审计内容

- [ ] 白名单中不再使用的域名
- [ ] 高风险域名的使用频率
- [ ] 异常访问模式
- [ ] 新出现的安全威胁

---

## 七、应急处理

### 7.1 域名被入侵/污染

```
1. 立即从白名单移除
2. 阻断所有对该域名的请求
3. 检查历史请求是否受影响
4. 评估数据泄露风险
5. 寻找替代方案
```

### 7.2 误封处理

```
1. 确认域名安全性
2. 临时添加到白名单
3. 蓝军审核
4. 正式恢复或保持封禁
```

---

## 八、版本历史

| 版本 | 日期 | 变更 | 审核 |
|------|------|------|------|
| v1.0 | 2026-03-21 | 初始白名单，P0+P1域名 | 待蓝军 |

---

*文档状态: 已生效，待蓝军审阅*  
*下次审计: 2026-04-21*
