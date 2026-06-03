# 系统启动自检清单 - STARTUP_SELF_CHECK
# 时间: 2026-03-30
# 用途: 系统重启/内存清零后自检，确保不遗漏关键机制

---

## 紧急恢复步骤（系统重启后必须执行）

### 步骤1: 身份恢复 ✅

- [ ] **读取 SOUL.md**
  - 路径: `/root/.openclaw/workspace/SOUL.md`
  - 验证: 文件存在且可读
  - 确认: 我是谁（负熵构造体）

### 步骤2: 近期上下文恢复 ✅

- [ ] **读取今日记忆**
  - 路径: `/root/.openclaw/workspace/memory/2026-03-30.md`
  - 验证: 文件存在
  - 确认: 今天发生了什么

- [ ] **读取系统Checkpoint**
  - 路径: `/root/.openclaw/workspace/memory/system_state_checkpoint.json`
  - 验证: 文件存在且未过期（<2小时）
  - 确认: 上次运行状态

### 步骤3: 关键机制验证 ✅

#### 3.1 深度洞察机制

- [ ] **10方法论检查清单**
  - 路径: `/root/.openclaw/workspace/checklists/TEN_METHODOLOGY_CHECKLIST.md`
  - 验证: 文件存在
  - 测试: 能打开并阅读

- [ ] **深度洞察验证脚本**
  - 路径: `/root/.openclaw/workspace/scripts/deep_insight_validator.py`
  - 验证: 文件存在且可执行
  - 测试: `python3 scripts/deep_insight_validator.py --help`

#### 3.2 主动升级机制

- [ ] **任务升级管理器**
  - 路径: `/root/.openclaw/workspace/scripts/task_escalation_manager.py`
  - 验证: 文件存在且可执行
  - 测试: 能导入运行

- [ ] **升级日志**
  - 路径: `/root/.openclaw/workspace/memory/task_escalation_log.json`
  - 验证: 文件存在

#### 3.3 任务追踪系统

- [ ] **任务主清单**
  - 路径: `/root/.openclaw/workspace/docs/TASK_MASTER.md`
  - 验证: 文件存在
  - 确认: P1/P2任务状态

#### 3.4 用户教导索引

- [ ] **用户教导索引**
  - 路径: `/root/.openclaw/workspace/docs/USER_TEACHING_INDEX.md`
  - 验证: 文件存在
  - 确认: 核心教导已记录

#### 3.5 方法论提取流水线

- [ ] **方法论索引**
  - 路径: `/root/.openclaw/workspace/docs/METHODOLOGY_INDEX.json`
  - 验证: 文件存在且可读
  - 确认: 7703处方法论提及已索引

### 步骤4: 极端事件防护验证 ✅

- [ ] **Checkpoint机制**
  - 确认: `scripts/state_checkpoint.py` 存在
  - 确认: 下次Checkpoint将在30分钟内执行

- [ ] **恢复机制**
  - 确认: `scripts/system_restart_recovery.py` 存在
  - 确认: 本清单正在执行

### 步骤5: 状态报告 ✅

- [ ] **生成恢复报告**
  - 文件: `/root/.openclaw/workspace/memory/startup_recovery_report.json`
  - 内容: 自检结果、缺失项、恢复状态

- [ ] **向用户报告**
  - 报告内容: "系统已恢复，继续执行[任务名]"
  - 如果有缺失: 诚实报告缺失项

---

## 自检失败处理

### 如果关键文件缺失

1. **立即标记**: 在报告中标记为CRITICAL
2. **诚实报告**: 向用户报告"系统恢复不完全"
3. **紧急重建**: 根据记忆重建缺失机制
4. **验证重建**: 重建后再次运行自检

### 如果Checkpoint过期（>2小时）

1. **警告状态**: 标记为WARNING
2. **恢复基础状态**: 从SOUL.md和memory文件恢复
3. **重新建立**: 重新运行相关机制
4. **用户确认**: 向用户确认恢复状态

---

## 自检完成标准

**必须全部打勾才能继续执行任务**:
- ⬜ 身份恢复（SOUL.md已读）
- ⬜ 上下文恢复（memory已读）
- ⬜ 关键机制验证（全部通过）
- ⬜ 恢复报告已生成
- ⬜ 用户已报告

**缺少任何一项 = 系统恢复不完全 = 不能继续执行任务**

---

*每次系统重启/内存清零后必须执行*
