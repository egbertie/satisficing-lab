---
# 知识元数据 (5标准化)
knowledge_id: W16-0DADB2
title: rss-ai-reader Skill V5标准版本
category: 11_Skill文档
source: skills/rss-ai-reader/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1908
week: 16
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# rss-ai-reader Skill V5标准版本

> **知识ID**: W16-0DADB2  
> **分类**: 11_Skill文档  
> **来源**: `skills/rss-ai-reader/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# rss-ai-reader Skill V5标准版本

## S1: 全局考虑

### 输入
- RSS订阅源URL列表
- AI摘要配置（模型选择、摘要长度）
- 推送渠道配置（飞书/邮件/等）
- 更新频率

### 覆盖维度
| 维度 | 考虑内容 |
|------|----------|
| **人** | 信息消费者、研究人员、决策者 |
| **事** | RSS抓取、AI摘要、多渠道推送 |
| **物** | RSS feed、文章、摘要、推送消息 |
| **环境** | 网络环境、API配额、时区 |
| **外部集成** | RSS服务、AI模型、飞书/邮件/Discord |
| **边界情况** | feed失效、抓取失败、AI限流 |

---

## S2: 系统考虑

### 处理流程
```
RSS抓取 → 去重检查 → AI摘要 → 质量评估 → 多渠道推送 → 存档记录
```

### 故障处理
- **feed失效**: 标记并告警，尝试恢复
- **抓取失败**: 重试3次，记录错误
- **AI限流**: 延迟处理，队列积压
- **推送失败**: 重试并记录失败渠道

---

## S3: 输出规范

### 摘要输出格式
```json
{
  "source": "RSS源名称",
  "title": "文章标题",
  "url": "原文链接",
  "published": "2026-03-22T09:00:00+08:00",
  "summary": "AI生成摘要...",
  "key_points": ["要点1", "要点2", "要点3"],
  "relevance_score": 0.85,
  "sentiment": "positive|neutral|negative"
}
```

### 推送格式
- 标题：【RSS摘要】源名称 - 文章标题
- 内容：摘要 + 关键要点 + 原文链接
- 标签：#RSS #AI摘要 #资讯

---

## S4: 自动化集成

### 定时任务
```
每30分钟检查RSS更新
每小时生成摘要并推送
每日09:00发送资讯汇总
```

### 配置示例
```json
{
  "feeds": [
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "category": "tech"},
    {"name": "36氪", "url": "https://36kr.com/feed", "category": "startup"}
  ],
  "ai_model": "kimi-coding/k2p5",
  "summary_length": "medium",
  "channels": ["feishu", "email"],
  "dedup_hours": 24
}
```

---

## S5: 自我验证

### 质量指标
| 指标 | 目标 | 验证方法 |
|------|------|----------|
| 抓取成功率 | >95% | 统计日志 |
| 摘要准确性 | >85% | 人工抽查 |
| 推送成功率 | >90% | 渠道反馈 |
| 去重准确率 | >99% | 重复检测 |

---

## S6: 认知谦逊

### 局限
- AI摘要可能丢失细节
- 无法判断文章真实性
- 依赖RSS源稳定性
- 多语言支持有限

---

## S7: 对抗测试

| 场景 | 预期行为 |
|------|----------|
| RSS源失效 | 标记离线，尝试恢复，告警 |
| 大量更新（>100篇） | 批量处理，优先级排序 |
| AI服务不可用 | 延迟处理，队列积压 |
| 推送渠道全部失败 | 本地存档，稍后重试 |
| 文章过长（>1万字） | 分段摘要，标记超长 |

---

## 使用说明

```bash
# 添加RSS源
python3 scripts/rss_reader.py add "TechCrunch" "https://techcrunch.com/feed/"

# 手动执行抓取
python3 scripts/rss_reader.py fetch

# 查看统计
python3 scripts/rss_reader.py stats
```
