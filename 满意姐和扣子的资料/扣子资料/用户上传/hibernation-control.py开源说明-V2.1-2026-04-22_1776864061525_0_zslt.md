# hibernation-control.py 开源说明

> **文件**: `skills/hibernation-protocol/hibernation-control.py`  
> **版本**: V2.1（蓝军彻底重写版）  
> **生效日期**: 2026-04-10  
> **开源日期**: 2026-04-22  
> **性质**: 满意解研究所五级运行模式控制器  
> **开源范围**: 全量代码 + 使用说明 + 实施路径**

---

## 一、工具定位

**hibernation-control.py** 是满意解研究所的**AI Agent运行模式中枢**。

它的核心使命：**根据Token消耗状态和用户交互频率，自动在五种运行模式之间切换**，实现Token经济学的动态治理——在"全力输出"和"生存保护"之间找到满意解。

---

## 二、核心功能

| 功能 | 说明 |
|------|------|
| **五级模式管理** | L0正常 → L1高耗能 → L2休眠 → L3静默 → L4深度静默 |
| **自动降级** | 根据无交互时间和Token档位自动降级 |
| **手动控制** | 支持用户强制进入任意模式 |
| **Gate控制** | 拦截/放行cron任务，防止静默期后台Token消耗 |
| **Cron动态节流** | 不同模式对应不同cron检查频率 |
| **前置检查** | 进入静默前自动执行C1-C6检查清单 |
| **唤醒恢复** | 唤醒时自动恢复被禁用的cron任务 |

---

## 三、五级运行模式详解

| 级别 | 名称 | 图标 | 触发条件 | 子代理 | 心跳间隔 | Cron策略 |
|------|------|------|----------|--------|----------|----------|
| **L0** | 正常模式 | 🌅 | 默认 / Token>50% | 允许 | 30min | 全部运行 |
| **L1** | 高耗能模式 | 🚀 | 用户指令"全力输出" | 优先级放行 | 60min | 保活+主线 |
| **L2** | 休眠模式 | 🌙 | 无交互>10min / Token20-50% | 禁止 | 30min | 保活任务 |
| **L3** | 静默模式 | 🤫 | 无交互>30min / Token10-20% | 禁止 | 120min | 保活任务 |
| **L4** | 深度静默 | 🪦 | 用户指令 / Token<10% | 禁止 | 720min | 仅生存 |

---

## 四、使用场景

### 场景1：日常自动运行
```bash
# 由cron每30分钟自动执行
python3 skills/hibernation-protocol/hibernation-control.py auto-check
```
**用途**: 系统自动根据Token状态和无交互时间调整运行模式。

### 场景2：用户强制进入高耗能模式
```bash
python3 skills/hibernation-protocol/hibernation-control.py turbo --reason "紧急任务"
```
**用途**: 需要全力输出时，临时解除限制。

### 场景3：用户强制进入深度静默
```bash
python3 skills/hibernation-protocol/hibernation-control.py deep-silent --reason "Token紧急"
```
**用途**: Token低于10%时，强制进入生存模式。

### 场景4：手动唤醒
```bash
python3 skills/hibernation-protocol/hibernation-control.py wake
```
**用途**: 从任何静默状态恢复。

### 场景5：查看当前状态
```bash
python3 skills/hibernation-protocol/hibernation-control.py status
```

### 场景6：任务Gate检查
```bash
python3 skills/hibernation-protocol/hibernation-control.py gate --job-id xxx --job-name "daily-backup"
# 返回码: 0=允许, 1=禁止, 2=允许但极简, 3=turbo_focus
```

---

## 五、降级规则（核心算法）

```
优先级（从高到低）:
1. 用户手动 turbo → 维持turbo（直到超时）
2. 用户手动 deep-silent → 维持deep-silent
3. Token >= 90% 或 L4 → 强制deep-silent（绝对阈值）
4. Token 70-90% 或 L3 → 强制silent（绝对阈值）
5. pace_ratio > 1.60 → deep-silent（相对超支严重）
6. pace_ratio > 1.30 → silent（相对超支较快）
7. 无交互 > 120分钟 → deep-silent
8. 无交互 > 30分钟 → silent
9. 无交互 > 10分钟 → hibernating
10. 默认 → normal
```

---

## 六、关键设计决策

| 决策 | 说明 |
|------|------|
| **五级光谱** | 从二级(awake/hibernating)升级到五级，更精细的Token控制 |
| **双阈值机制** | 绝对阈值（Token%）+相对阈值（pace_ratio），双重保护 |
| **用户意图优先** | 手动turbo/deep-silent优先于自动规则 |
| **C1-C6前置检查** | 进入静默前必须确认记忆已保存、Git已提交 |
| **Cron动态节流** | 不同模式自动调整cron检查频率，减少agentTurn消耗 |
| **保活任务白名单** | 备份/检查/磁盘扫描等核心任务任何模式都运行 |

---

## 七、实施路径

### Step 1: 部署
```bash
# 确保目录结构
mkdir -p /path/to/workspace/skills/hibernation-protocol/
mkdir -p /path/to/workspace/memory

# 复制脚本
cp hibernation-control.py /path/to/workspace/skills/hibernation-protocol/
```

### Step 2: 配置Cron
```bash
# 添加自动检查任务（每30分钟）
openclaw cron add --name "hibernation-check" \
  --cron "*/30 * * * *" \
  --command "python3 skills/hibernation-protocol/hibernation-control.py auto-check"
```

### Step 3: 初始化状态
```bash
python3 skills/hibernation-protocol/hibernation-control.py status
```

### Step 4: 集成到任务脚本
在每个cron任务开头添加：
```bash
# 检查当前模式是否允许执行
python3 skills/hibernation-protocol/hibernation-control.py gate --job-id "YOUR_JOB_ID" --job-name "YOUR_JOB_NAME"
EXIT_CODE=$?
if [ $EXIT_CODE -eq 1 ]; then
  echo "当前模式禁止执行，跳过"
  exit 0
fi
```

### Step 5: 测试各级别切换
```bash
# 测试turbo
python3 skills/hibernation-protocol/hibernation-control.py turbo
python3 skills/hibernation-protocol/hibernation-control.py status

# 测试唤醒
python3 skills/hibernation-protocol/hibernation-control.py wake
python3 skills/hibernation-protocol/hibernation-control.py status
```

---

## 八、前置检查清单（C1-C6）

进入任何静默模式前，自动检查：

| 检查项 | 说明 |
|--------|------|
| **C1** | 当日session日志已写入（memory/YYYY-MM-DD.md） |
| **C2** | MEMORY.md指针已同步 |
| **C3** | TASK_MASTER.md已更新 |
| **C4** | 代码资产存在（有.py文件） |
| **C5** | Git已快照（git status通过） |
| **C6** | 恢复验证（session_log + task_master存在） |

---

## 九、满意解研究所实践案例

**2026-04-10 Token危机事件**:
- Token消耗达到临界值
- hibernation-control自动将系统降级到L4深度静默
- 只保留保活任务（备份、检查）
- 阻止了后台自动化任务的Token消耗
- 为用户争取了整改时间

**2026-04-22 当前状态**:
- 系统处于L0正常模式
- Token档位：L1（正常）
- 最后交互：~0分钟前
- 所有cron正常运行

---

## 十、扩展建议

| 扩展方向 | 说明 |
|----------|------|
| **添加Webhook通知** | 模式切换时通知用户 |
| **添加仪表盘** | 可视化展示当前模式和Token状态 |
| **添加预测模型** | 基于历史数据预测Token耗尽时间 |
| **添加成本估算** | 每次模式切换时估算节省的Token |

---

## 十一、完整代码

> 由于代码较长（约500行），详见同目录 `hibernation-control.py` 源文件。
> 核心模块：
> - `resolve_level()`: 降级决策算法
> - `level_gate()`: 任务拦截/放行逻辑
> - `auto_check()`: 自动检测主函数
> - `enter_level()`: 进入指定级别
> - `wake()`: 唤醒恢复
> - `pre_hibernation_checklist()`: C1-C6前置检查

---

> **开源说明**: 本工具是满意解研究所Token经济学的核心基础设施。它不完美，但"足够好"——用500行代码解决了AI Agent长期运行中最棘手的Token治理问题。  
> **作者**: 蓝军 Skeptor-7 设计并彻底重写  
> **License**: 内部开源，仅供满意解研究所及相关方使用

---

*2026-04-22 于满意解研究所*
