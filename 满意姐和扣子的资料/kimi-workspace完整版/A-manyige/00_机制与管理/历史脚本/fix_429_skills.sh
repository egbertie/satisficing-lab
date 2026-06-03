#!/bin/bash
# Skill 429修复脚本
# 生成时间: 2026-03-14
# 用途: 批量修复59个Skill的SKILL.md 429下载失败问题

REPO_BASE="https://github.com/clawhub/skills"
TARGET_DIR="/root/openclaw/kimi/downloads/fixed_skills"
mkdir -p "$TARGET_DIR"

echo "==============================================="
echo "    Skill 429修复脚本"
echo "==============================================="
echo "生成时间: 2026-03-14"
echo "目标目录: $TARGET_DIR"
echo ""

# ==============================================
# P0优先级修复（立即安装 - 10个Skill）
# ==============================================
declare -a P0_SKILLS=(
  "brave-search"
  "automate-excel"
  "csvtoexcel"
  "copywriting"
  "duckdb-cli-ai-skills"
  "cron-scheduling"
  "markdown-converter"
  "markdown-exporter"
  "mermaid-diagrams"
)

echo "【P0优先级 - 10个Skill（立即安装）】"
echo "------------------------------------------------"
for skill in "${P0_SKILLS[@]}"; do
  echo "  [P0] $skill"
  # 克隆命令（取消注释以执行）
  # git clone --depth 1 "$REPO_BASE/$skill.git" "$TARGET_DIR/$skill" 2>/dev/null && echo "    ✓ 成功" || echo "    ✗ 失败"
done

echo ""

# ==============================================
# P1优先级修复（合并安装 - 25个Skill）
# ==============================================
declare -a P1_SKILLS=(
  "adwords"
  "copywriting"
  "auto-redbook-skills"
  "notion"
  "notion-api"
  "notion-api-skill"
  "obsidian"
  "feishu-messaging"
  "feishu-doc-manager"
  "feishu-docx-powerwrite"
  "feishu-file-sender"
  "feishu-send-file"
  "sendfiles-to-feishu"
  "dingtalk-feishu-cn"
  "slack"
  "git"
  "git-essentials"
  "audio-handler"
  "ffmpeg-video-editor"
  "bilibili-subtitle-download-skill"
  "mineru"
  "firecrawl-search"
  "multi-search-engine"
  "tavily"
  "openclaw-tavily-search"
  "smart-web-fetch"
  "news-summary"
  "rss-ai-reader"
)

echo "【P1优先级 - 25个Skill（合并安装）】"
echo "------------------------------------------------"
for skill in "${P1_SKILLS[@]}"; do
  echo "  [P1] $skill"
done

echo ""

# ==============================================
# P2/P3优先级（24个Skill）
# ==============================================
declare -a P2_P3_SKILLS=(
  "agent-orchestrator"
  "agents-manager"
  "agent-task-tracker"
  "multi-agent-cn"
  "ai-image-generation"
  "ai-lmage-for-file-repair"
  "antigravity-image-gen"
  "attribution-engine"
  "audio-cog"
  "canva-connect"
  "design-assets"
  "gembox-skill"
  "visual-file-sorter"
  "web-form-automation"
  "nano-banana-pro"
  "nano-banana-pro-2"
  "memory-setup"
  "elite-longterm-memory"
  "instagram-poster"
  "dingtalk-feishu-cn"
)

echo "【P2/P3优先级 - 20个Skill（延迟/不安装）】"
echo "------------------------------------------------"
for skill in "${P2_P3_SKILLS[@]}"; do
  echo "  [P2/P3] $skill"
done

echo ""
echo "==============================================="
echo "修复命令模板（手动执行）:"
echo "==============================================="
echo ""
echo "# 方式1: 使用clawhub直接安装（推荐）"
echo "clawhub install brave-search"
echo "clawhub install automate-excel"
echo "clawhub install csvtoexcel"
echo "# ... 以此类推"
echo ""
echo "# 方式2: GitHub克隆（需手动处理）"
echo "# git clone --depth 1 $REPO_BASE/<skill-name>.git $TARGET_DIR/<skill-name>"
echo ""
echo "# 方式3: 延时批量下载（避免429）"
echo "# 使用 /root/.openclaw/workspace/scripts/download_skills_delayed.sh"
echo ""
echo "==============================================="
echo "修复完成提示:"
echo "==============================================="
echo "1. P0批次建议今晚23:00执行安装"
echo "2. P1批次建议合并为7个套件后安装"
echo "3. P2/P3批次按需处理"
echo "4. 安装完成后更新MEMORY.md信赖清单"
echo "==============================================="
