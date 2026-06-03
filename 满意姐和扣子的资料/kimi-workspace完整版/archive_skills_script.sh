#!/bin/bash
# Skills archive script for memory leak remediation
# Keep only essential skills, archive the rest

SKILLS_DIR="/root/.openclaw/workspace/skills"
ARCHIVE_DIR="/root/.openclaw/workspace/skills-archive/small-2026-04-12"
mkdir -p "$ARCHIVE_DIR"

# Whitelist of essential skills to KEEP
cat > /tmp/keep_skills.txt << 'EOF'
1001night-stories
12006
academic-deep-research
adi-decision-engine
afrexai-okr-engine
afrexai-strategic-thinking
agent-browser-clawdbot
agent-reach
ai-expert-analyst
antifragile-taleb
architecture-designer
article-outline-template
automation-workflows
automation-workflows-0-1-0
baseline-checker
batch-processing-patterns
baidu-scholar-search
blue-army-auditor
blue-army-deep-insight-auditor
blue-army-interceptor
blue-army-self-closure
blue-auditor
blue-sentinel
browser-automation
browser-use
business-model-analyzer
caesar-research
channels-setup
clawhub
competitor-analysis
consultant_bridge
consulting
cron
cron-automation
daily-report
data-analyst
debug-pro
decision-framework
decision-maker
diagram-generator
edge-tts
error-handler
execution-system-clear
feishu-bitable
feishu-calendar
feishu-create-doc
doc
feishu-doc
feishu-docs
feishu-drive-backup
feishu-evolver-wrapper
feishu-fetch-doc
feishu-file-sender
feishu-im-read
feishu-suite
feishu-task
feishu-update-doc
first-principles-decomposer
founder-playbook
github
healthcheck
heartbeat-protocol
hibernation-protocol
interview-simulator
investment-committee
kimi-file-transfer
kimi-usage-monitor
learning-system-skill
marketing-mode
mbb-strategist
md-to-pdf
memory
memory-hygiene
memory-indexer
memory-setup
metacognitive-loop-enforcer
multi-agent-roles
neuroscience-baseline
node-connect
openclaw-token-optimizer
partner-matching-engine
post-market-review
pre-market-sentiment
prompt-compress
quality-assessment
quality-assurance
quality-closure
quality-gate-system
readgzh
react-email
reason
research-pro
rss-ai-reader
satisficing-gene-engine
satisfying_sister
scenario-planner
second-brain
self-improving-agent
skill-creator
skill-finder
skill-finder-cn
skillhub-preference
startup-0-to-1-workflow
stock-assistant
strategy-consultant-package
system-builder
system-commander
tavily-search
thinking-mentor
token-budget-enforcer
token-budget-guard
token-fuse-system
token-management-satisficing
token-optimizer
token-saver
token-saver-active
token-saver-king
token-saver-qclaw
token-throttle-controller
token-weekly-monitor
totem-system
totem_engine
totem-avatar
totem-quality-gate
tushare-finance
weather
wechat-article-assistant
wechat-publisher
wechat-toolkit
weixin-reader
xiaohongshu-writer-expert
xhs-note-creator
EOF

# Generate current skills list
ls -1 "$SKILLS_DIR" | sort > /tmp/current_skills.txt
sort /tmp/keep_skills.txt > /tmp/keep_skills_sorted.txt

# Find skills NOT in whitelist
comm -23 /tmp/current_skills.txt /tmp/keep_skills_sorted.txt > /tmp/archive_skills.txt

# Count
echo "Total current: $(wc -l < /tmp/current_skills.txt)"
echo "Keep: $(wc -l < /tmp/keep_skills_sorted.txt)"
echo "Archive: $(wc -l < /tmp/archive_skills.txt)"

# Move them
while IFS= read -r skill; do
    if [ -d "$SKILLS_DIR/$skill" ]; then
        mv "$SKILLS_DIR/$skill" "$ARCHIVE_DIR/"
    fi
done < /tmp/archive_skills.txt

# Final count
echo "Final skills count: $(ls -1 "$SKILLS_DIR" | wc -l)"
ls -1 "$SKILLS_DIR" | wc -l > /tmp/final_count.txt
