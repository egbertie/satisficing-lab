---
# 知识元数据 (5标准化)
knowledge_id: W19-A31B2F
title: Skill市场整合报告 - TOP20必装清单
category: 12_记忆档案
source: memory/skill-integration-report-2026-03-27.md
ingested_at: 2026-03-27 17:59:30
word_count: 2470
week: 19
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Skill市场整合报告 - TOP20必装清单

> **知识ID**: W19-A31B2F  
> **分类**: 12_记忆档案  
> **来源**: `memory/skill-integration-report-2026-03-27.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Skill市场整合报告 - TOP20必装清单

## 调研完成
- **时间**: 2026-03-27
- **数据来源**: 阿里云开发者社区、腾讯云、知乎、绿联NAS社区
- **当前系统Skill数**: 306个（含.archive_归档）

---

## 第一梯队：必备基础（5个）

| 排名 | 技能名称 | 下载量 | 核心功能 | 优先级 |
|------|----------|--------|----------|--------|
| 1 | **self-improving-agent** | 32K | 跨会话学习记忆，越用越贴合 | P0 |
| 2 | **summarize** | 26.1K | PDF/视频/音频一键总结 | P0 |
| 3 | **github** | 24.8K | Issues/PR/CI管理 | P0 |
| 4 | **tavily-search** | 28K | AI优化网页搜索 | P0 |
| 5 | **weather** | 21.1K | 天气查询，零配置 | P1 |

## 第二梯队：生产力（5个）

| 排名 | 技能名称 | 下载量 | 核心功能 | 优先级 |
|------|----------|--------|----------|--------|
| 6 | **ontology** | 27.6K | 知识图谱构建 | P1 |
| 7 | **notion** | 13.9K | Notion双向同步 | P1 |
| 8 | **obsidian** | 12.4K | 本地Markdown管理 | P1 |
| 9 | **gog** | 33.8K | Gmail/Calendar/Docs全套 | P2 |
| 10 | **google-calendar** | - | 日程管理+Cron联动 | P2 |

## 第三梯队：搜索研究（3个）

| 排名 | 技能名称 | 下载量 | 核心功能 | 优先级 |
|------|----------|--------|----------|--------|
| 11 | **brave-search** | 10.4K | 隐私搜索 | P2 |
| 12 | **multi-search-engine** | 4.5K | 17个搜索引擎整合 | P2 |
| 13 | **clawddocs** | 9.9K | 官方文档导航 | P2 |

## 第四梯队：内容创作（4个）

| 排名 | 技能名称 | 下载量 | 核心功能 | 优先级 |
|------|----------|--------|----------|--------|
| 14 | **nano-banana-pro** | 13.4K | Gemini图像生成 | P2 |
| 15 | **openai-whisper** | 11.5K | 本地语音转文字 | P2 |
| 16 | **youtube-watcher** | 9.1K | YouTube字幕提取 | P3 |
| 17 | **spotify** | 6.2K | 音乐控制 | P3 |

## 第五梯队：安全工具（3个）

| 排名 | 技能名称 | 说明 | 优先级 |
|------|----------|------|--------|
| 18 | **skill-vetter** | 安全扫描，先装它 | P0 |
| 19 | **find-skills** | 技能发现 | P1 |
| 20 | **skill-creator** | 自定义技能封装 | P2 |

---

## 安装计划

### 立即安装（P0+P1 = 11个）
```bash
# 安全优先
clawhub install skill-vetter

# 基础能力
clawhub install self-improving-agent
clawhub install summarize
clawhub install github
clawhub install tavily-search

# 知识管理
clawhub install ontology
clawhub install notion
clawhub install obsidian
clawhub install find-skills

# 实用工具
clawhub install weather
clawhub install brave-search
```

---

## 已存在Skill盘点（本地306个）

### 核心治理Skill（6个）✅
- honesty-tagging-protocol
- quality-gate-system
- blue-army-interceptor
- quality-assurance
- backup-verification
- digital-avatar-swarm

### 需要评估整合的外部Skill（15个待安装）
- [ ] self-improving-agent
- [ ] summarize
- [ ] github
- [ ] tavily-search
- [ ] ontology
- [ ] notion
- [ ] obsidian
- [ ] skill-vetter
- [ ] find-skills
- [ ] skill-creator
- [ ] gog
- [ ] google-calendar
- [ ] brave-search
- [ ] nano-banana-pro
- [ ] openai-whisper

---

*报告生成时间: 2026-03-27*
