---
# 知识元数据 (5标准化)
knowledge_id: W3-04A57A
title: 行动计划：零Token状态永生系统（务实版）
category: 01_研究报告
source: docs/ACTION_PLAN_Immortal_State_2026-03-26.md
ingested_at: 2026-03-27 17:58:21
word_count: 7607
line_count: 337
week: 3
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 行动计划：零Token状态永生系统（务实版）

> **知识ID**: W3-04A57A  
> **分类**: 01_研究报告  
> **来源**: `docs/ACTION_PLAN_Immortal_State_2026-03-26.md`  
> **入库时间**: 2026-03-27

## 摘要

1. **零Token唤醒** - 纯本地操作，恢复时不消耗API Token

---

## 正文

# 行动计划：零Token状态永生系统（务实版）
## 决策文档 - 请Egbertie选择执行路径

---

## 学习所得核心观点

### 原文方案的优点
1. **零Token唤醒** - 纯本地操作，恢复时不消耗API Token
2. **精确恢复** - 事件溯源可到任意操作点
3. **自动保存** - 无需人工干预，每5分钟自动检查点

### 原文方案的挑战（在我们的环境）
1. **需要OpenClaw底层支持** - 事件Hook、内存持久化等需要修改核心
2. **对话上下文在云端** - Kimi管理对话历史，本地无法直接干预
3. **进程监控权限** - 无法直接监控Claw进程生命周期

### 我们的务实方案
保留核心思想（本地持久化、零Token恢复、自动保存），但用我们**实际可控**的方式实现：

---

## 方案对比矩阵

| 维度 | 方案A：文件级检查点 | 方案B：Git增强版 | 方案C：智能摘要 |
|------|-------------------|-----------------|----------------|
| **Token成本** | 零 | 零 | <500/次 |
| **恢复完整性** | 100%文件 | 最后一次提交 | 上下文摘要 |
| **恢复速度** | 10秒 | 即时 | 1秒 |
| **磁盘占用** | ~1GB（20个检查点） | ~100MB | ~1MB |
| **开发成本** | 低 | 已部署 | 中 |
| **维护成本** | 中 | 低 | 低 |

---

## 推荐：三方案并行（三重保护）

### 保护层次
```
Layer 1: Git自动提交（每2小时）    - 长期历史
Layer 2: 文件检查点（每5分钟）     - 短期快照
Layer 3: 智能摘要（中断时）        - 上下文恢复
```

---

## 具体执行计划

### 立即执行（今天30分钟内完成）

#### 1. 部署文件级检查点系统

**创建检查点脚本**：`scripts/auto-checkpoint.sh`

```bash
#!/bin/bash
# 零Token自动检查点系统

VAULT_DIR="$HOME/.openclaw/immortal-state"
CHECKPOINT_DIR="$VAULT_DIR/checkpoints"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

mkdir -p "$CHECKPOINT_DIR"

# 获取当前会话ID（从环境或生成）
SESSION_ID=${CLAW_SESSION_ID:-"default"}

# 创建检查点
cd "$HOME/.openclaw"
tar czf "$CHECKPOINT_DIR/cpt-${SESSION_ID}-${TIMESTAMP}.tar.gz" \
  --exclude='*.log' \
  --exclude='checkpoints/*' \
  workspace/ \
  2>/dev/null

# 记录元数据
cat > "$CHECKPOINT_DIR/cpt-${SESSION_ID}-${TIMESTAMP}.meta" << EOF
{
  "id": "cpt-${SESSION_ID}-${TIMESTAMP}",
  "timestamp": "$(date -Iseconds)",
  "session": "$SESSION_ID",
  "size": $(stat -f%z "$CHECKPOINT_DIR/cpt-${SESSION_ID}-${TIMESTAMP}.tar.gz" 2>/dev/null || echo 0),
  "files": $(find "$HOME/.openclaw/workspace" -type f 2>/dev/null | wc -l)
}
EOF

# 保留最近20个检查点
ls -t "$CHECKPOINT_DIR"/cpt-*.tar.gz 2>/dev/null | tail -n +21 | xargs rm -f
ls -t "$CHECKPOINT_DIR"/cpt-*.meta 2>/dev/null | tail -n +21 | xargs rm -f

echo "✅ 检查点创建: cpt-${SESSION_ID}-${TIMESTAMP}"
```

**部署到Cron（每5分钟）**：
```bash
*/5 * * * * /bin/bash /root/.openclaw/workspace/scripts/auto-checkpoint.sh >> /tmp/checkpoint.log 2>&1
```

#### 2. 创建中断恢复摘要机制

**创建摘要生成器**：`scripts/generate-resume-summary.py`

```python
#!/usr/bin/env python3
"""
生成恢复摘要 - 零Token上下文恢复
"""

import json
import os
from datetime import datetime

def generate_summary():
    workspace = "/root/.openclaw/workspace"
    memory_dir = f"{workspace}/memory"
    
    summary = {
        "generated_at": datetime.now().isoformat(),
        "active_context": {},
        "recent_files": [],
        "pending_tasks": [],
        "last_memory": None
    }
    
    # 读取今日记忆文件
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = f"{memory_dir}/{today}.md"
    if os.path.exists(memory_file):
        with open(memory_file) as f:
            content = f.read()
            # 提取最近的活动
            if "##" in content:
                last_section = content.split("##")[-1][:500]
                summary["last_memory"] = last_section.strip()
    
    # 列出最近修改的文件
    import subprocess
    result = subprocess.run(
        ["find", workspace, "-type", "f", "-mtime", "-0.01", "-not", "-path", "*/.*"],
        capture_output=True, text=True
    )
    summary["recent_files"] = result.stdout.strip().split("\n")[:10]
    
    # 读取TASK_MASTER.md获取待办
    task_file = f"{workspace}/docs/TASK_MASTER.md"
    if os.path.exists(task_file):
        with open(task_file) as f:
            content = f.read()
            if "### In Progress" in content:
                section = content.split("### In Progress")[1].split("###")[0]
                summary["pending_tasks"] = [
                    line.strip() for line in section.split("\n")
                    if line.strip().startswith("-") or line.strip().startswith("*")
                ][:5]
    
    # 保存摘要
    summary_path = f"{workspace}/.claw-resume-summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"📝 恢复摘要已生成: {summary_path}")
    return summary

if __name__ == "__main__":
    generate_summary()
```

**创建恢复读取脚本**：`scripts/resume-from-summary.sh`

```bash
#!/bin/bash
# 读取恢复摘要，生成Claw可理解的上下文

SUMMARY_FILE="/root/.openclaw/workspace/.claw-resume-summary.json"

if [ -f "$SUMMARY_FILE" ]; then
    echo "📂 检测到上次的恢复摘要"
    echo ""
    echo "=== 上次工作状态 ==="
    
    # 使用Python解析JSON
    python3 -c "
import json
with open('$SUMMARY_FILE') as f:
    s = json.load(f)
    print(f\"生成时间: {s.get('generated_at', 'N/A')}\")
    print()
    if s.get('pending_tasks'):
        print('待办任务:')
        for t in s['pending_tasks'][:3]:
            print(f'  • {t}')
    print()
    if s.get('recent_files'):
        print('最近文件:')
        for f in s['recent_files'][:5]:
            if f.strip():
                print(f'  • {f.split(\"/\")[-1]}')
"
    echo ""
    echo "💡 提示: 如需恢复到具体检查点，运行: openclaw-state restore"
else
    echo "✨ 无恢复摘要，正常启动"
fi
```

#### 3. 增强Git自动提交

**修改现有脚本**，增加触发条件：
```bash
# 在auto-git-commit.sh中添加：
# 如果文件变化超过10个，立即提交（不等待2小时）
CHANGED_FILES=$(git status --short | wc -l)
if [ $CHANGED_FILES -gt 10 ]; then
    echo "文件变化较多($CHANGED_FILES)，立即提交"
    git add -A && git commit -m "auto: checkpoint $(date)" && git push
fi
```

---

### 本周执行（完善体系）

#### 4. 创建检查点管理工具

**脚本**：`scripts/openclaw-state.sh`

```bash
#!/bin/bash
# Claw状态管理工具

COMMAND=$1
CHECKPOINT_DIR="$HOME/.openclaw/immortal-state/checkpoints"

case $COMMAND in
    list)
        echo "📂 可用检查点:"
        ls -lt "$CHECKPOINT_DIR"/*.meta 2>/dev/null | head -10 | while read line; do
            echo "  $line"
        done
        ;;
    restore)
        CHECKPOINT=$2
        if [ -z "$CHECKPOINT" ]; then
            # 使用最新的
            CHECKPOINT=$(ls -t "$CHECKPOINT_DIR"/cpt-*.tar.gz 2>/dev/null | head -1)
        fi
        if [ -f "$CHECKPOINT" ]; then
            echo "🔄 恢复检查点: $CHECKPOINT"
            cd /tmp && tar xzf "$CHECKPOINT"
            rsync -av /tmp/.openclaw/workspace/ "$HOME/.openclaw/workspace/"
            echo "✅ 恢复完成"
        else
            echo "❌ 检查点不存在: $CHECKPOINT"
        fi
        ;;
    clean)
        echo "🧹 清理旧检查点..."
        ls -t "$CHECKPOINT_DIR"/cpt-*.tar.gz 2>/dev/null | tail -n +21 | xargs rm -vf
        ls -t "$CHECKPOINT_DIR"/cpt-*.meta 2>/dev/null | tail -n +21 | xargs rm -vf
        echo "✅ 清理完成"
        ;;
    *)
        echo "用法: openclaw-state {list|restore [checkpoint]|clean}"
        ;;
esac
```

#### 5. 集成到HEARTBEAT

修改`HEARTBEAT.md`，增加：
```yaml
immortal_state_checks:
  - check_checkpoint_health: "每4小时验证检查点可恢复性"
  - generate_resume_summary: "每次心跳生成恢复摘要"
  - clean_old_checkpoints: "每周清理旧检查点"
```

---

## 预期效果

### Token节省估算

| 场景 | 传统方式 | 新系统 | 节省 |
|------|---------|--------|------|
| 对话中断恢复 | 5000-10000 Token（重建上下文） | 零Token（本地恢复） | 100% |
| 工作重复 | 每次重复消耗相同Token | 零Token（从检查点继续） | 100% |
| 调试重复 | 重复执行相同操作 | 零Token（恢复状态） | 100% |

### 体验提升

- **中断恢复**：从"重新开始"到"10秒恢复"
- **上下文重建**：从"人工回忆"到"自动摘要"
- **文件保护**：三重备份（Git+检查点+实时）

---

## 决策请求

请决策以下问题：

### Q1：执行范围
- [ ] **方案A**：仅部署文件级检查点（最简单，磁盘占用1GB）
- [ ] **方案B**：仅优化Git提交（已部署，增强触发条件）
- [ ] **方案C**：仅开发智能摘要（最轻量，体验好）
- [ ] **方案D**：三方案并行（推荐，三重保护）

### Q2：检查点频率
- [ ] **每5分钟**（推荐，最多丢失5分钟工作）
- [ ] **每10分钟**（平衡，磁盘占用减半）
- [ ] **每30分钟**（保守，可能丢失较多工作）

### Q3：保留数量
- [ ] **保留20个**（约1GB，1.5小时历史）
- [ ] **保留50个**（约2.5GB，4小时历史）
- [ ] **保留100个**（约5GB，8小时历史）

### Q4：立即执行
- [ ] **立即部署**（我今天完成）
- [ ] **本周执行**（按优先级排队）
- [ ] **暂缓**（先完成其他任务）

---

## 风险与缓解

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| 磁盘空间不足 | 中 | 检查点失败 | 设置上限，自动清理 |
| 检查点损坏 | 低 | 无法恢复 | 定期验证，多版本保留 |
| 恢复摘要不准确 | 中 | 上下文丢失 | 多源信息（Git+文件+内存） |
| Cron未执行 | 低 | 无检查点 | 心跳检测补救 |

---

*等待你的决策...*
