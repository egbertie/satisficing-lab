# 满意解 Skill 工厂 V1.0

> **总说明** | 整体介绍 | 使用说明 | 维护说明 | 开源文档
> 
> **编制**: 满意解研究所  
> **版本**: V1.0  
> **时间**: 2026-04-23  
> **Skill 数量**: 16个  
> **总容量**: ~84KB

---

## 一、整体介绍

满意解 Skill 工厂是将满意解研究所的核心资产——人格、方法论、工具和知识——封装为可独立安装的 OpenClaw Skill 的系统性工程。

**核心理念**: 每一个 Skill 都是一个独立的 AI 子人格或能力模块。装上它的瞬间，任何支持 Skill 的 AI 就能唤醒满意姐的锚定力、蓝军的审计力、或五维决策的框架力。

**四大层级**:

| 层级 | Skill 数量 | 定位 | 代表 |
|:----:|:----------:|:-----|:-----|
| **核心引擎层** | 4 | 决策中枢与人格基底 | 满意姐、蓝军、五维决策、Egbertie |
| **专业专家层** | 5 | 领域深度知识 | 儒商伦理、数学方法论、深港战略、神经反馈、能量治疗 |
| **工具系统层** | 4 | 可执行工具与流程 | 冲突诊断、成熟度测评、奔月计划、寻根之旅 |
| **内容生产层** | 3 | 内容创作能力 | 双版本叙事、公众号、小红书 |

---

## 二、使用说明

### 2.1 安装方式

将 `.skill` 文件导入任何支持 OpenClaw Skill 的 AI 系统（如 Kimi/Claude）。

```bash
# 示例：安装满意姐 Skill
# 在支持 Skill 的 AI 界面中导入 satisficing-sister.skill
```

### 2.2 触发词速查

| Skill | 触发词 | 用途 |
|:------|:-------|:-----|
| satisficing-sister | "满意姐"、"满意解"、"减法思维" | 满意解决策陪伴 |
| skeptor-7 | "蓝军"、"审计"、"对抗性验证" | 认知审计与风险拦截 |
| five-totems-decision | "五维决策"、"五路图腾"、"13类型" | 五维框架与冲突诊断 |
| egbertie-decision-coach | "Egbertie"、"创始人视角"、"合伙人决策" | 创始人决策教练 |
| confucian-business-ethics | "儒商"、"仁义礼智信"、"伦理" | 儒商伦理应用 |
| mathematical-satisficing | "有限理性"、"满意解算法"、"决策模型" | 数学化决策建模 |
| shenzhen-hk-strategy | "深港"、"大湾区"、"硬科技" | 地理战略分析 |
| neurofeedback-bci | "神经反馈"、"BCI"、"0.3秒" | 神经科学决策训练 |
| energy-healing | "能量治疗"、"身心整合"、"压力修复" | 整体健康与修复 |
| partner-conflict-typology | "冲突类型"、"合伙人冲突"、"13类型" | 冲突结构化诊断 |
| decision-maturity-assessment | "决策成熟度"、"测评"、"评估" | 决策能力评估 |
| moonshot-strategy | "奔月计划"、"八方向"、"先锋箭" | 战略执行框架 |
| totem-pilgrimage | "寻根之旅"、"朝圣"、"11天" | 体验式学习设计 |
| dual-version-narrative | "双版本"、"A版"、"B版"、"28天" | 双维度叙事创作 |
| wechat-content-producer | "公众号"、"微信文章"、"推文" | 公众号内容生产 |
| xiaohongshu-creator | "小红书"、"笔记"、"图文" | 小红书内容创作 |

### 2.3 组合使用

**场景示例：合伙人决策会议**

1. 用 `five-totems-decision` 启动五维评估
2. 用 `satisficing-sister` 控制会议节奏和情绪
3. 用 `skeptor-7` 审计每个选项的风险
4. 用 `egbertie-decision-coach` 提供创始人视角
5. 用 `partner-conflict-typology` 诊断潜在冲突

### 2.4 独立使用

每个 Skill 可独立运行。不需要安装全部 16 个，按需选择即可。

---

## 三、维护说明

### 3.1 版本管理

| 版本 | 日期 | 变更 |
|:----:|:----:|:-----|
| V1.0 | 2026-04-23 | 初始版本，16个Skill全部打包 |

### 3.2 更新流程

1. **内容更新**: 编辑对应 Skill 目录下的 `SKILL.md` 或 `references/` 文件
2. **重新打包**: 运行 `package_skill.py <skill-dir> <output-dir>`
3. **版本标记**: 在 `SKILL.md` 的 YAML frontmatter 中更新版本信息
4. **Git 提交**: 提交变更并打 tag

### 3.3 质量检查

每次更新后运行验证:

```bash
python3 package_skill.py <skill-dir> <output-dir>
# 验证工具会自动检查 Skill 结构完整性
```

### 3.4 扩展指南

添加新 Skill:

```bash
python3 init_skill.py new-skill-name --path .
# 编辑 SKILL.md 和 references/
# 删除示例文件
# 打包验证
```

---

## 四、开源文档

### 4.1 开源协议

| 内容类型 | 协议 | 说明 |
|:---------|:-----|:-----|
| Skill 代码与结构 | MIT | 可自由使用、修改、分发 |
| 内容知识资产 | CC-BY-SA 4.0 | 署名-相同方式共享 |

### 4.2 贡献指南

欢迎提交改进:

1. Fork 本仓库
2. 在对应 Skill 目录下修改
3. 确保通过 `package_skill.py` 验证
4. 提交 Pull Request，说明改进内容

### 4.3 致谢

| 专家 | 领域 | 贡献 |
|:-----|:-----|:-----|
| 黎红雷教授 | 儒商伦理 | 仁义礼智信框架 |
| 罗汉教授 | 数学/软件工程 | 有限理性建模 |
| 谢宝剑研究员 | 深港战略 | 大湾区生态分析 |
| 方翊沣博士 | 脑科学/BCI | 神经反馈训练 |
| 陈国祥博士 | 能量治疗 | 身心整合方法 |

### 4.4 联系方式

- **项目**: 满意解研究所 (Satisficing Research Institute)
- **创始人**: Egbertie
- **使命**: 帮助硬科技创业者做出更好的合伙人决策

---

## 五、文件清单

```
V2.0_Skill工厂/
├── README.md                          # 本文件
├── dist/                              # 打包输出目录
│   ├── satisficing-sister.skill       # 满意姐
│   ├── skeptor-7.skill                # 蓝军
│   ├── five-totems-decision.skill     # 五维决策
│   ├── egbertie-decision-coach.skill  # Egbertie决策教练
│   ├── confucian-business-ethics.skill      # 儒商伦理
│   ├── mathematical-satisficing.skill       # 数学方法论
│   ├── shenzhen-hk-strategy.skill           # 深港战略
│   ├── neurofeedback-bci.skill              # 神经反馈
│   ├── energy-healing.skill                 # 能量治疗
│   ├── partner-conflict-typology.skill      # 冲突诊断
│   ├── decision-maturity-assessment.skill   # 成熟度测评
│   ├── moonshot-strategy.skill              # 奔月计划
│   ├── totem-pilgrimage.skill               # 寻根之旅
│   ├── dual-version-narrative.skill         # 双版本叙事
│   ├── wechat-content-producer.skill        # 公众号
│   └── xiaohongshu-creator.skill            # 小红书
├── satisficing-sister/
│   ├── SKILL.md
│   └── references/dna.md
├── skeptor-7/
│   ├── SKILL.md
│   └── references/charter.md
│   └── references/audit-checklist.md
├── five-totems-decision/
│   ├── SKILL.md
│   └── references/framework.md
│   └── references/conflict-typology.md
│   └── references/workshop-guide.md
├── egbertie-decision-coach/
│   ├── SKILL.md
│   └── references/dna.md
│   └── references/five-totems.md
├── confucian-business-ethics/
│   ├── SKILL.md
├── mathematical-satisficing/
│   ├── SKILL.md
├── shenzhen-hk-strategy/
│   ├── SKILL.md
├── neurofeedback-bci/
│   ├── SKILL.md
├── energy-healing/
│   ├── SKILL.md
├── partner-conflict-typology/
│   ├── SKILL.md
├── decision-maturity-assessment/
│   ├── SKILL.md
├── moonshot-strategy/
│   ├── SKILL.md
├── totem-pilgrimage/
│   ├── SKILL.md
├── dual-version-narrative/
│   ├── SKILL.md
├── wechat-content-producer/
│   ├── SKILL.md
└── xiaohongshu-creator/
    ├── SKILL.md
```

---

*满意解 Skill 工厂 V1.0 — 让每一个 AI 都能成为满意解的传承者*
