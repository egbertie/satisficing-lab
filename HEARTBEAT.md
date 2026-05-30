# Heartbeat Tasks

## 每次心跳检查 (triggered ~periodically)

### 反孤岛检测 (5项)
1. **产品-索引一致性**: 扫描 site/ 目录 HTML ↔ entities_index products[].url，发现遗漏或死链 → 生成TASK
2. **任务僵尸检测**: open_tasks_audit中deadline已过的待执行任务 >3条 → P0告警
3. **Cron健康检测**: 任何Cron超过预期周期2倍未执行 → P0告警
4. **元数据新鲜度**: 任何实体超过7天未更新 → 标记可能腐烂
5. **知识消化进度**: 连续2周knowledge_digestion_pipeline进度为0 → 推动任务

### 专家团队维护
- Read `memory/expert_team_manifest.md` — refresh expert team context
- Read `memory/expert_workflow_rules.md` — refresh workflow rules
- Check if `memory/expert_team_audit.jsonl` has new entries since last check
- If SOUL.md has changed, note any new auto-trigger rules

### 产品-索引一致性 (已集成到entities_index_autoupdate Cron)

## 每周 (Sunday)
- Cron job `weekly-expert-team-review` handles the full review
- 反孤岛健康分报告: 一致性% + 新鲜度% + 闭环率% + Cron存活率%
