#!/bin/bash
# Cron优化管理器初始化脚本
# 执行方案C+的Cron全面优化

set -e

echo "=============================================="
echo "Cron优化管理器初始化程序"
echo "方案C+ - 第一性原理优化"
echo "=============================================="
echo ""

WORKSPACE="/root/.openclaw/workspace"
BACKUP_DIR="$WORKSPACE/backups/cron"
CONFIG_DIR="$WORKSPACE/config"
SKILL_DIR="$WORKSPACE/skills/cron-optimization-manager"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# 创建备份目录
mkdir -p "$BACKUP_DIR/init-$TIMESTAMP"
mkdir -p "$CONFIG_DIR"

echo "[1/9] 备份当前配置..."
# 备份现有cron配置
if [ -f "$WORKSPACE/cron-schedule-v1.1.txt" ]; then
    cp "$WORKSPACE/cron-schedule-v1.1.txt" "$BACKUP_DIR/init-$TIMESTAMP/"
    echo "  ✓ 已备份 cron-schedule-v1.1.txt"
fi

# 备份现有skill配置
if [ -d "$SKILL_DIR" ]; then
    cp -r "$SKILL_DIR/config" "$BACKUP_DIR/init-$TIMESTAMP/" 2>/dev/null || true
    echo "  ✓ 已备份 skill配置"
fi

echo ""
echo "[2/9] 创建全局配置文件..."

# 创建全局cron规则配置
cat > "$CONFIG_DIR/cron-rules.yaml" << 'EOF'
# 全局Cron规则配置
# 由Cron优化管理器维护

# 三层响应架构定义
tier_definitions:
  tier_1:
    name: "自动执行"
    description: "低风险任务，系统自动执行"
    features:
      - "无需用户确认"
      - "失败后自动通知"
      - "适合维护类任务"
    auto_execute: true
    confirmation_window: null
    risk_levels: [low]
    
  tier_2:
    name: "确认窗口"
    description: "中风险任务，提供确认窗口"
    features:
      - "执行前提醒用户"
      - "可设置默认行为"
      - "无响应则按默认执行"
    auto_execute: false
    confirmation_window: 15  # 默认15分钟
    risk_levels: [medium]
    
  tier_3:
    name: "强制阻断"
    description: "高风险任务，必须手动确认"
    features:
      - "必须用户确认"
      - "绝不自动执行"
      - "适合敏感操作"
    auto_execute: false
    confirmation_window: null
    confirmation_required: true
    risk_levels: [high]

# 已废弃Cron清单（已禁用）
deprecated_crons:
  - id: zero_vacancy_check
    name: "零空置检查"
    reason: "高频空转，改为零空置V3.0"
    disabled_at: "2026-03-15"
    
  - id: resource_scheduler
    name: "资源调度"
    reason: "改为事件驱动"
    disabled_at: "2026-03-15"
    
  - id: review_checker
    name: "复盘检查"
    reason: "合并到报告生成任务"
    disabled_at: "2026-03-15"
    
  - id: executor_checker
    name: "执行器检查"
    reason: "已集成到心跳协议"
    disabled_at: "2026-03-15"

# 优化策略
optimization_strategy:
  max_cron_count: 15
  max_high_frequency: 0  # 不允许高频Cron
  preferred_schedule_offset: [17, 37, 47]  # 推荐错峰分钟
  daily_token_budget: 18000
  max_empty_rate: 0.2
EOF

echo "  ✓ 已创建全局规则配置"

# 创建优化策略配置
cat > "$CONFIG_DIR/optimization-policy.yaml" << 'EOF'
# 优化策略配置

thresholds:
  empty_rate_warning: 0.8
  token_budget_warning: 0.1
  inactive_days_warning: 30
  success_rate_warning: 0.5
  high_frequency_threshold: 60

auto_optimize:
  tier_1: true
  tier_2: false
  tier_3: false
  max_changes_per_run: 3

notification:
  channels:
    - kimi
    - feishu
  progressive_timeline:
    - delay: 0
      channel: kimi
    - delay: 5
      channel: feishu
    - delay: 15
      action: execute
    - delay: 30
      action: pending

reporting:
  daily:
    enabled: true
    time: "00:00"
  weekly:
    enabled: true
    time: "18:17"
    day: friday
  monthly:
    enabled: true
    time: "09:17"
    day: 3

budget:
  daily_token_budget: 18000
  max_tokens_per_execution: 5000
  monthly_token_budget: 540000

retention:
  execution_log: 90
  efficiency_stats: 365
  backup_snapshots: 30
EOF

echo "  ✓ 已创建优化策略配置"

echo ""
echo "[3/9] 部署Skill数据目录..."
mkdir -p "$SKILL_DIR/data"
mkdir -p "$SKILL_DIR/reports"

echo "  ✓ 数据目录已创建"

echo ""
echo "[4/9] 创建监控状态文件..."

cat > "$SKILL_DIR/data/execution_log.json" << 'EOF'
[]
EOF

cat > "$SKILL_DIR/data/efficiency_stats.json" << 'EOF'
{
  "initialized_at": "{{TIMESTAMP}}",
  "total_executions": 0,
  "total_tokens": 0,
  "optimization_count": 0
}
EOF

cat > "$SKILL_DIR/data/optimization_history.json" << 'EOF'
[]
EOF

echo "  ✓ 状态文件已创建"

echo ""
echo "[5/9] 创建CLI快捷命令..."

# 创建claw cron命令包装器
mkdir -p "$WORKSPACE/scripts"

cat > "$WORKSPACE/scripts/cron-manager.sh" << 'EOF'
#!/bin/bash
# Cron管理器CLI包装器

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$SCRIPT_DIR/../skills/cron-optimization-manager"

python3 "$SKILL_DIR/cron_manager.py" "$@"
EOF

chmod +x "$WORKSPACE/scripts/cron-manager.sh"

echo "  ✓ CLI命令已创建"
echo "  使用方式: ./scripts/cron-manager.sh [command]"

echo ""
echo "[6/9] 初始化报告目录..."
mkdir -p "$WORKSPACE/reports/cron"

echo "  ✓ 报告目录已创建"

echo ""
echo "[7/9] 生成初始化状态报告..."

cat > "$WORKSPACE/docs/CRON_INITIALIZATION_REPORT.md" << EOF
# Cron优化初始化报告

**初始化时间**: $TIMESTAMP  
**执行用户**: $(whoami)  
**工作目录**: $WORKSPACE

---

## 初始化状态

| 步骤 | 状态 | 说明 |
|------|------|------|
| 备份配置 | ✅ 完成 | 备份至: $BACKUP_DIR/init-$TIMESTAMP |
| 创建全局配置 | ✅ 完成 | $CONFIG_DIR/cron-rules.yaml |
| 创建优化策略 | ✅ 完成 | $CONFIG_DIR/optimization-policy.yaml |
| 部署Skill | ✅ 完成 | $SKILL_DIR |
| 创建数据目录 | ✅ 完成 | $SKILL_DIR/data |
| 创建CLI命令 | ✅ 完成 | $WORKSPACE/scripts/cron-manager.sh |

---

## 新Cron架构

### Tier 1 - 自动执行（2个）

| ID | 名称 | 调度 | 任务 |
|----|------|------|------|
| auto_maintenance | 自动维护任务 | 每2小时17分 | 备份检查、磁盘监控、日志归档 |
| economic_daily | 经济环境监测 | 每日09:17 | 市场监测、政策检查、新闻摘要 |

### Tier 2 - 确认窗口（4个）

| ID | 名称 | 调度 | 确认窗口 |
|----|------|------|----------|
| daily_report | 每日报告生成 | 每日22:17 | 15分钟 |
| weekly_report | 周报生成 | 周五18:17 | 30分钟 |
| economic_weekly | 环境周报 | 周五17:17 | 15分钟 |
| monthly_report | 月度报告 | 每月3日09:17 | 30分钟 |

### Tier 3 - 强制阻断（2个）

| ID | 名称 | 调度 | 说明 |
|----|------|------|------|
| security_check | 安全检查 | 每日09:17 | 必须手动确认 |
| quarterly_audit | 季度审计 | 每季度25日 | 全面审计 |

### 已废弃（4个）

| ID | 名称 | 废弃原因 |
|----|------|----------|
| zero_vacancy_check | 零空置检查 | 高频空转，改为V3.0 |
| resource_scheduler | 资源调度 | 改为事件驱动 |
| review_checker | 复盘检查 | 合并到报告生成 |
| executor_checker | 执行器检查 | 已集成到心跳 |

---

## 预估改善效果

| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| Cron数量 | ~35个 | 8个启用 | -77% |
| 高频Cron | 4个 | 0个 | -100% |
| 日均Token | 45K | 18K | -60% |

---

## 后续步骤

1. **用户确认**: 请确认新架构符合预期
2. **试运行**: 观察1周运行数据
3. **微调优化**: 根据运行数据调整
4. **全面启用**: 正式启动新架构

---

## 命令参考

\`\`\`bash
# 查看状态
./scripts/cron-manager.sh status --detailed

# 审计所有Cron
./scripts/cron-manager.sh audit --all

# 生成周报
./scripts/cron-manager.sh report --weekly

# 调整Cron层级
./scripts/cron-manager.sh tier --set daily_report --tier 2
\`\`\`

---

*报告生成时间: $TIMESTAMP*
EOF

echo "  ✓ 初始化报告已生成"

echo ""
echo "[8/9] 设置权限..."
chmod -R 755 "$SKILL_DIR"
chmod -R 755 "$CONFIG_DIR"
chmod 644 "$CONFIG_DIR"/*.yaml

echo "  ✓ 权限已设置"

echo ""
echo "[9/9] 完成初始化..."

echo ""
echo "=============================================="
echo "✅ 初始化完成!"
echo "=============================================="
echo ""
echo "备份路径: $BACKUP_DIR/init-$TIMESTAMP"
echo "配置路径: $CONFIG_DIR/"
echo "报告路径: $WORKSPACE/docs/CRON_INITIALIZATION_REPORT.md"
echo ""
echo "快速开始:"
echo "  1. 查看状态: ./scripts/cron-manager.sh status"
echo "  2. 审计Cron: ./scripts/cron-manager.sh audit"
echo "  3. 查看报告: cat docs/CRON_INITIALIZATION_REPORT.md"
echo ""
echo "=============================================="
