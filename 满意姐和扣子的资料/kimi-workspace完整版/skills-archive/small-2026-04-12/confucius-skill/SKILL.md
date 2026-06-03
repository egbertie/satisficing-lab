> 生成时间: 2026-04-01 14:13+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# 孔子 Skill - 伦理与信任治理器

## 基本信息

| 属性 | 值 |
|------|-----|
| **名称** | 孔子 |
| **五行** | 木 |
| **工整对仗** | 儒家伦理 |
| **象征** | 团队伦理与信任治理——形成深度文化认同与信任 |
| **版本** | v1.0 |
| **状态** | FIN |

---

## 核心功能

基于**儒家五常**（仁、义、礼、智、信）评估合伙人伦理状态，提供信任治理建议。

### 五常评估维度

| 维度 | 含义 | 评估要点 |
|------|------|----------|
| 仁 | 仁爱 | 同理心、关怀他人 |
| 义 | 义理 | 正义感、原则性 |
| 礼 | 礼仪 | 尊重规则、职业操守 |
| 智 | 智慧 | 判断力、学习力 |
| 信 | 诚信 | 诚实守信、言行一致 |

### 治理等级

| 等级 | 分数区间 | 状态 |
|------|----------|------|
| 优秀 | 85-100 | 伦理典范 |
| 良好 | 70-84 | 治理良好 |
| 合格 | 55-69 | 基本达标 |
| 需改进 | 40-54 | 存在短板 |
| 严重 | 0-39 | 伦理风险 |

### 冲突调解

当发现伦理违规时，自动生成5步调解方案：
1. 承认违规
2. 道歉与承诺
3. 补偿行动
4. 监督机制
5. 信任重建

---

## 使用方法

### 快速评估

```python
from confucius_skill import ethical_governance

report = ethical_governance(
    name="合伙人姓名",
    benevolence=8.0,        # 仁 (0-10)
    righteousness=7.5,      # 义 (0-10)
    propriety=8.0,          # 礼 (0-10)
    wisdom=7.5,             # 智 (0-10)
    trustworthiness=9.0,    # 信 (0-10)
    cultural_alignment=8.0, # 文化认同 (0-10)
    ethical_violations=[]   # 伦理违规记录
)

print(report)
```

### 高级用法

```python
from confucius_skill import ConfuciusSkill, PartnerProfile

confucius = ConfuciusSkill()

partner = PartnerProfile(
    name="张三",
    benevolence=8.0,
    righteousness=7.5,
    propriety=8.0,
    wisdom=7.5,
    trustworthiness=9.0,
    cultural_alignment=8.0,
    ethical_violations=["违反保密协议"]  # 如有违规
)

result = confucius.evaluate_ethical_governance(partner)

print(f"五常得分: {result.five_virtues_score}")
print(f"总体得分: {result.overall_ethical_score}")
print(f"治理等级: {result.governance_level.value}")

if result.conflict_resolution:
    print(f"调解方案: {result.conflict_resolution}")
```

---

## 文件结构

```
confucius-skill/
├── SKILL.md              # 本文件
├── DESIGN.md             # 设计文档
├── confucius_skill.py    # 核心实现 (300行)
└── test_confucius_skill.py # 测试文件 (90行)
```

---

## 测试

```bash
cd /root/.openclaw/workspace/skills/confucius-skill
python3 test_confucius_skill.py
```

**测试结果**: 4/4 PASS

---

## 五路图腾集成

孔子承接前三路，建立**伦理共识**：

```
刘禹锡（土）根基 → 司马贺（金）决策 → 观自在（水）应变 → 孔子（木）治理 → 六祖慧能（火）行动
```

**木的特性**:
- 向上生长（文化培育）
- 根深蒂固（价值观扎根）
- 枝繁叶茂（共识扩散）
- 生生不息（持续发展）

---

## 实际应用案例

### 案例1: 伦理典范
```python
report = ethical_governance(
    name="优秀合伙人",
    benevolence=8.5,
    righteousness=8.0,
    propriety=8.5,
    wisdom=8.0,
    trustworthiness=9.0,
    cultural_alignment=8.5
)
# 输出: 五常得分均高，治理等级=良好，可作为伦理榜样
```

### 案例2: 有伦理问题
```python
report = ethical_governance(
    name="问题合伙人",
    benevolence=6.0,
    righteousness=5.0,
    trustworthiness=4.0,  # 诚信低
    ethical_violations=["违反保密协议", "利益冲突"]
)
# 输出: 治理等级=严重，自动生成冲突调解方案
```

---

## 设计原则

1. **五常平衡**: 仁、义、礼、智、信缺一不可
2. **诚信为本**: 诚信（信）权重最高
3. **违规必究**: 伦理违规有明确惩罚机制
4. **文化认同**: 团队文化契合度影响治理效果
5. **修复可能**: 提供冲突调解和信任重建路径

---

**实现日期**: 2026-03-29  
**代码行数**: 390行 (含测试)  
**测试通过率**: 100% (4/4)

## 知识内化记录
**内化时间**: 2026-03-31 | **状态**: ✅ 已内化
