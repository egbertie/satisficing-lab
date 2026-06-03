# 技能体系完整档案

> 归档位置: `memory/archive/skill_system.md`
> 
> 技能管理规则: `docs/SKILL_MANAGEMENT_RULES.md`

---

## 自建核心技能

| 技能名 | 版本 | 类型 | 状态 | 说明 |
|--------|------|------|------|------|
| **satisficing-partner-decision** | 1.0.0 | 自建 | ✅ 已部署 | 合伙人决策支持体系（6大Skill） |
| **archive-handler** | 1.0.0 | 自建 | ✅ 已部署 | 通用解压工具 |
| **workspace-integrity-guardian** | 1.0.0 | 自建 | ✅ 已部署 | 工作空间完整性守护者（4维巡查） |
| **skill-integration-optimizer** | 1.0.0 | 自建 | ✅ 已部署 | Skill整合优化器（防碎片化） |

## P0批次自建替代套件

| 套件名 | 版本 | 替代Skill数 | 状态 | 说明 |
|--------|------|-------------|------|------|
| **unified-search** | 1.0.0 | 4 | ✅ 已部署 | 统一搜索入口 |
| **data-processor-suite** | 1.0.0 | 3 | ✅ 已部署 | 数据处理统一入口 |
| **document-processor** | 1.0.0 | 3 | ✅ 已部署 | 文档处理统一入口 |
| **marketing-content-generator** | 1.0.0 | 3 | ✅ 已部署 | 营销内容生成统一入口 |
| **合计** | - | **13** | ✅ | 4个套件替代13个外部Skill |

## 已审计外部技能

| 技能名 | 版本 | 状态 | 说明 |
|--------|------|------|------|
| **docker-essentials** | - | ✅ 已部署 | Docker容器管理 |
| **error-guard** | - | ✅ 已部署 | 系统安全恢复（防死锁） |
| **github** | 1.0.0 | ✅ 已审计 | GitHub CLI 集成 |
| **zipcracker** | 2.0.0 | ✅ 已审计 | ZIP 密码破解（CTF级） |
| **cron-scheduling** | 1.0.0 | ✅ 已部署 | 定时任务增强 |
| **mermaid-diagrams** | 0.1.0 | ✅ 已部署 | 图表生成，决策可视化 |

## P1批次待安装套件

| 技能名 | 版本 | 套件归属 | 状态 |
|--------|------|----------|------|
| notion | 1.0.0 | Notion套件 | ⏳ P1待装 |
| notion-api | 1.1.0 | Notion套件 | ⏳ P1待装 |
| feishu-messaging | 0.0.3 | 飞书套件 | ⏳ P1待装 |
| feishu-doc-manager | 1.0.0 | 飞书套件 | ⏳ P1待装 |
| audio-handler | 1.0.0 | 媒体套件 | ⏳ P1待装 |
| ffmpeg-video-editor | 1.0.0 | 媒体套件 | ⏳ P1待装 |
| rss-ai-reader | 1.0.0 | 信息套件 | ⏳ P1待装 |
| firecrawl-search | 1.0.0 | 搜索套件 | ⏳ P1待装 |
| multi-search-engine | 2.0.1 | 搜索套件 | ⏳ P1待装 |

## 管理原则

1. **评估维度**: 安全40% + 成本30% + 功能20% + 可维护10%
2. **使用优先级**: 自建Skill > 已审计外部Skill > 新外部Skill
3. **成本控制**: Kimi包月优先 → MiniMax便宜 → GPT-4中等 → Claude贵重
4. **更新机制**: 每月第一个周六检查更新
5. **淘汰机制**: 30天未使用/功能被替代/成本过高/安全隐患 → 淘汰评估

---

*最后更新: 2026-03-18 | 归入归档记忆*
