# 知识复活系统 (Knowledge Resurrection)

> **定位**: 新AI快速接管、理解并活化已有知识资产的系统
> **触发词**: "复活" / "接管" / "新AI启动" / "继承记忆"
> **编号**: SANSHENG-SKILL-005
> **五维映射**: 土(根基) + 水(流动) + 木(生长)

---

## 一、Why

当新AI接手时，面临三大挑战：
1. **信息过载**: 1000+文件，不知道从哪里开始
2. **上下文缺失**: 不知道"为什么这样决定"
3. **能力断层**: 有文档但无法执行

知识复活系统 = 让新AI在30分钟内"活过来"，具备基本工作能力。

---

## 二、What

### 2.1 核心能力

| 能力 | 说明 | 输出 |
|:-----|:-----|:-----|
| 记忆读取 | 读取memory/MEMORY.md/TASK_MASTER | 当前状态快照 |
| 环境感知 | 扫描workspace结构、Git状态、脚本可用性 | 环境健康报告 |
| 知识注入 | 快速加载核心知识（P0优先） | 核心知识摘要 |
| 能力验证 | 运行关键脚本验证可操作性 | 能力验证报告 |
| 交接确认 | 向人类汇报接管状态 | 交接报告 |

### 2.2 复活六阶段（C1-C6）

直接复用HEARTBEAT.md的C1-C6标准：
- C1: memory读取
- C2: MEMORY.md同步
- C3: TASK_MASTER更新
- C4: 代码运行验证
- C5: Git快照
- C6: 重启自检

---

## 三、How

```bash
# 一键复活检查
python3 scripts/resurrect-check.py /path/to/workspace

# 知识注入（加载P0核心）
python3 scripts/knowledge-inject.py --level P0 --max-items 5

# 能力验证（运行关键脚本）
python3 scripts/capability-verify.py --scripts key-scripts.txt
```

---

*知识复活系统版本: V1.0*
*满意解研究所·三生万物·技能系列*
