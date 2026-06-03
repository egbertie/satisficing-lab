#!/bin/bash
# P0批次Skill批量安装脚本
# 执行时间: 2026-03-14 23:00
# 安装数量: 9个Skill

set -e  # 遇错即停

LOG_FILE="/root/.openclaw/workspace/logs/p0_install_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$(dirname "$LOG_FILE")"

echo "===============================================" | tee -a "$LOG_FILE"
echo "    P0批次 Skill 批量安装"
echo "===============================================" | tee -a "$LOG_FILE"
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "日志文件: $LOG_FILE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# P0批次技能列表
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

# 依赖检查
echo "【步骤1】依赖检查..." | tee -a "$LOG_FILE"
echo "  - 检查clawhub命令..." | tee -a "$LOG_FILE"
if ! command -v clawhub &> /dev/null; then
  echo "  ✗ 未找到clawhub命令" | tee -a "$LOG_FILE"
  echo "  请确保OpenClaw CLI已正确安装" | tee -a "$LOG_FILE"
  exit 1
fi
echo "  ✓ clawhub可用" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 安装统计
TOTAL=${#P0_SKILLS[@]}
SUCCESS=0
FAILED=0
SKIPPED=0

echo "【步骤2】开始安装 ${TOTAL} 个Skill..." | tee -a "$LOG_FILE"
echo "-----------------------------------------------" | tee -a "$LOG_FILE"

for i in "${!P0_SKILLS[@]}"; do
  skill="${P0_SKILLS[$i]}"
  num=$((i + 1))
  
  echo "" | tee -a "$LOG_FILE"
  echo "[$num/$TOTAL] 安装: $skill" | tee -a "$LOG_FILE"
  echo "  时间: $(date '+%H:%M:%S')" | tee -a "$LOG_FILE"
  
  # 检查是否已安装
  if [ -d "/root/.openclaw/workspace/skills/$skill" ]; then
    echo "  ⚠ 已存在，跳过" | tee -a "$LOG_FILE"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi
  
  # 执行安装
  if clawhub install "$skill" >> "$LOG_FILE" 2>>1; then
    echo "  ✓ 安装成功" | tee -a "$LOG_FILE"
    SUCCESS=$((SUCCESS + 1))
    
    # 验证安装
    if [ -d "/root/.openclaw/workspace/skills/$skill" ]; then
      echo "  ✓ 目录验证通过" | tee -a "$LOG_FILE"
    else
      echo "  ⚠ 目录验证失败" | tee -a "$LOG_FILE"
    fi
  else
    echo "  ✗ 安装失败" | tee -a "$LOG_FILE"
    FAILED=$((FAILED + 1))
  fi
  
  # 安装间隔，避免触发限流
  if [ $num -lt $TOTAL ]; then
    echo "  等待5秒..." | tee -a "$LOG_FILE"
    sleep 5
  fi
done

echo "" | tee -a "$LOG_FILE"
echo "===============================================" | tee -a "$LOG_FILE"
echo "    安装完成统计"
echo "===============================================" | tee -a "$LOG_FILE"
echo "总计: $TOTAL" | tee -a "$LOG_FILE"
echo "成功: $SUCCESS" | tee -a "$LOG_FILE"
echo "失败: $FAILED" | tee -a "$LOG_FILE"
echo "跳过: $SKIPPED" | tee -a "$LOG_FILE"
echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "===============================================" | tee -a "$LOG_FILE"

# 后续步骤提示
echo "" | tee -a "$LOG_FILE"
echo "【后续步骤】" | tee -a "$LOG_FILE"
echo "1. 验证安装: ls -la /root/.openclaw/workspace/skills/" | tee -a "$LOG_FILE"
echo "2. 功能测试: 对每个skill执行基本命令测试" | tee -a "$LOG_FILE"
echo "3. 更新MEMORY.md信赖清单" | tee -a "$LOG_FILE"
echo "4. 更新skill-update-log.md" | tee -a "$LOG_FILE"

if [ $FAILED -gt 0 ]; then
  echo "" | tee -a "$LOG_FILE"
  echo "⚠ 注意: $FAILED 个Skill安装失败，请查看日志处理" | tee -a "$LOG_FILE"
  exit 1
fi

echo "" | tee -a "$LOG_FILE"
echo "✓ P0批次安装完成" | tee -a "$LOG_FILE"
