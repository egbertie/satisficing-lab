#!/bin/bash
# P0批次Skill立即安装脚本 - 不等今晚，完成即安装
# 生成时间: 2026-03-15 10:54

echo "==============================================="
echo "    P0批次Skill立即安装"
echo "    执行时间: $(date)"
echo "==============================================="
echo ""

INSTALL_DIR="/root/.openclaw/workspace/skills"
REPO_BASE="https://github.com/clawhub/skills"

cd "$INSTALL_DIR" || exit 1

# P0批次列表
P0_SKILLS=(
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

SUCCESS=0
FAILED=0

for skill in "${P0_SKILLS[@]}"; do
  echo "Installing: $skill ..."
  
  # 如果已存在，先备份
  if [ -d "$INSTALL_DIR/$skill" ]; then
    mv "$INSTALL_DIR/$skill" "$INSTALL_DIR/${skill}.bak.$(date +%s)"
    echo "  已备份现有版本"
  fi
  
  # 克隆新版本
  if git clone --depth 1 "$REPO_BASE/$skill.git" "$skill" 2>/dev/null; then
    echo "  ✓ $skill 安装成功"
    SUCCESS=$((SUCCESS + 1))
  else
    echo "  ✗ $skill 安装失败"
    FAILED=$((FAILED + 1))
    # 恢复备份
    if [ -d "$INSTALL_DIR/${skill}.bak"* ]; then
      LATEST_BAK=$(ls -td "$INSTALL_DIR/${skill}.bak"* 2>/dev/null | head -1)
      [ -n "$LATEST_BAK" ] && mv "$LATEST_BAK" "$INSTALL_DIR/$skill"
    fi
  fi
  
  # 延时避免429
  sleep 2
done

echo ""
echo "==============================================="
echo "    安装完成统计"
echo "==============================================="
echo "成功: $SUCCESS / ${#P0_SKILLS[@]}"
echo "失败: $FAILED / ${#P0_SKILLS[@]}"
echo "完成时间: $(date)"
echo "==============================================="

# 更新信赖清单
if [ $SUCCESS -gt 0 ]; then
  echo "" >> "$INSTALL_DIR/../MEMORY.md"
  echo "## P0批次Skill安装更新 - $(date +%Y-%m-%d)" >> "$INSTALL_DIR/../MEMORY.md"
  echo "成功安装: $SUCCESS 个Skill" >> "$INSTALL_DIR/../MEMORY.md"
  echo "安装列表: ${P0_SKILLS[*]}" >> "$INSTALL_DIR/../MEMORY.md"
fi

exit $FAILED
