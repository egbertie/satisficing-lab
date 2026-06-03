> 生成时间: 2026-04-05 20:06+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# Consultant Bridge - 外援桥接系统

**版本**: V1.0  
**时间**: 2026-04-05  
**存放**: `skills/consultant_bridge/SKILL.md`

---

## 能力概述

本Skill负责管理系统对外援的完整生命周期：
1. **触发判定**：在什么情况下优先寻求外援
2. **请求生成**：输出标准化、细致化的外援请求单
3. **结果内化**：将外援反馈转化为系统可执行、可追踪、可检索的内部资产
4. **持续学习**：建立不依赖人工输入的迭代循环

支持两类外援：
- **知识外援** (Knowledge Consultant)：理论思考、知识收集、框架梳理
- **技术外援** (Technical Consultant)：技术难题、工程化规范、系统升级

---

## 文件结构

```
skills/consultant_bridge/
├── __init__.py
├── engagement_manager.py      # 触发判定 + 请求单管理 + 内化流程
├── knowledge_consultant.py    # 知识外援专用模板
├── technical_consultant.py    # 技术外援专用模板 + 自评估指南
└── SKILL.md
```

---

## 使用方式

```python
from skills.consultant_bridge import EngagementManager, KnowledgeConsultant, TechnicalConsultant

mgr = EngagementManager()
ctype = mgr.should_escalate({
    "complexity": "P0",
    "domain": "软件工程",
    "internal_attempts": 2,
    "tech_stack": ["Python", "OpenClaw"],
})
print(ctype)  # technical

# 生成知识请求
kc = KnowledgeConsultant()
req = kc.generate_request(
    topic="合伙人信任崩塌的前置信号",
    current_framework="儒商五维 + 前景理论",
    observed_gaps=["缺乏量化指标体系", "没有纵向追踪机制"],
)

# 生成技术请求
tc = TechnicalConsultant()
req = tc.generate_request(
    system_name="满意解研究所AI操作系统",
    current_tech_stack=["Python 3.12", "OpenClaw", "Git"],
    pain_points=["测试覆盖率为0%", "API频繁401", "Skill数量过多缺乏管理"],
    target_state="工程化、可审计、可自愈的共生操作系统",
)
```

---

## 触发规则

### 优先寻求知识外援的场景
- 需要引入新理论或跨学科视角
- 现有框架无法解释观察到的现象
- token预算紧张但需要深度研究
- 需要人类专家的真实经验和直觉判断

### 优先寻求技术外援的场景
- 技术债务积累到需要外部视角评估
- 需要引入新的技术栈或工具链
- 系统性能/安全/可维护性达到瓶颈
- 需要建立可量化的技术评估体系
- P0任务内部尝试≥2次仍未解决

---

## 内化五步法

1. 蓝军审阅：来源独立性 + 逻辑一致性 + 假设检验
2. 满意姐评估：情感/伦理/文化适配性
3. 物理化：可落地的建议 → 代码/文档/SKILL.md更新
4. 归档：理论性内容 → theory-miner/ + 知识图谱链接
5. 索引：在 MEMORY.md 中建立指针

---

## 状态

- 代码实现：✅ 100%
- 测试：通过基础导入和示例运行
- 文档：✅ 本SKILL.md
