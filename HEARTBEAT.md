# Heartbeat Tasks

## Morning Check (triggered ~daily)
- Read `memory/expert_team_manifest.md` — refresh expert team context
- Read `memory/expert_workflow_rules.md` — refresh workflow rules
- Check if `memory/expert_team_audit.jsonl` has new entries since last check
- If SOUL.md has changed, note any new auto-trigger rules
- Quick scan: any P0 tasks in `memory/_data/open_tasks_audit.json` that need attention?

## Weekly (Sunday)
- Cron job `weekly-expert-team-review` handles the full review
