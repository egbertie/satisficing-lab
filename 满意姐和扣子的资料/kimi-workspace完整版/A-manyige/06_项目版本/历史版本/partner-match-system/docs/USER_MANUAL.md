# 用户手册

## 欢迎使用 Entanglement Partner Matching System

量子纠缠合伙人匹配决策系统帮助硬件初创企业家找到真正契合的合伙人。

---

## 快速入门

### 1. 启动系统

```bash
# 进入项目目录
cd partner-match-system

# 运行演示
python3 examples/demo.py

# 启动Web界面
cd ui
python3 -m http.server 8080
```

### 2. 创建合伙人档案

#### 基本信息
- **姓名**: 合伙人的姓名
- **ID**: 唯一标识符

#### 认知风格评估
- **分析型 (analytical)**: 0-1，越高越倾向逻辑分析
- **细节导向 (detail_oriented)**: 0-1，越高越关注细节
- **风险容忍 (risk_tolerance)**: 0-1，越高越愿意承担风险
- **独立性 (independent)**: 0-1，越高越倾向独立决策

#### 叙事身份
- **生命故事访谈**: 关键决策点和转折点
- **共享意义建构**: 对模糊情境的解释

#### 伦理价值
- **义利情境测试**: 在利益与道义间的选择

### 3. 执行匹配

```python
from core.entanglement_system import EntanglementMatchingSystem, PartnerProfile

system = EntanglementMatchingSystem()

# 创建档案
partner_a = PartnerProfile(
    name="李明",
    id="p001",
    cognitive_profile={
        'analytical': 0.7,
        'detail_oriented': 0.8,
        'risk_tolerance': 0.6,
        'independent': 0.7
    }
)

partner_b = PartnerProfile(
    name="王芳",
    id="p002",
    cognitive_profile={
        'analytical': 0.4,
        'detail_oriented': 0.4,
        'risk_tolerance': 0.7,
        'independent': 0.6
    }
)

# 匹配
result = system.comprehensive_match(partner_a, partner_b)
```

---

## 解读报告

### 综合兼容度

- **90%+**: 高度匹配，建议深入合作
- **70-89%**: 良好匹配，关注建议优化点
- **50-69%**: 中等匹配，需要更多磨合
- **<50%**: 谨慎考虑，可能存在根本性差异

### 六维评估

#### 量子纠缠度
反映认知模式的深层共振。
- 高: 潜意识层面高度协调
- 低: 需要建立更多共同语言

#### 涌现稳定性
预测长期合作的稳定程度。
- 高: 系统倾向于稳定吸引子
- 低: 可能出现频繁的模式切换

#### 身体共鸣
基于生物数据的潜意识协调。
- 高: 自然的互动节奏
- 低: 建议加强非语言沟通

#### 认知多样性
评估是否处于最优差异区。
- 高: 差异创造创新张力
- 低: 可能过于相似或过于不同

### 未来演化预测

系统预测6个月、1年、3年的合作演化：

- **成功率**: 基于当前状态的概率预测
- **关键挑战**: 各阶段需要关注的重点

### 优化建议

按优先级排序的行动建议：
- **高优先级**: 必须立即关注
- **中优先级**: 建议制定计划
- **机会**: 可以利用的优势

---

## 六幕沉浸式评估

### 序幕：身份解构
回顾关键人生决策，挖掘深层叙事身份。

**准备**: 
- 思考3-5个改变人生轨迹的决策
- 准备描述这些决策如何塑造了你

### 第一幕：量子纠缠
完成量子化评估，构建认知波函数。

**特色**: 
- 问题之间存在非经典关联
- 回答会改变后续问题的权重

### 第二幕：模拟共生
AI代理模拟100个虚拟协作场景。

**观察重点**:
- 主导协作模式（同步/互补/冲突/创造）
- 吸引子景观

### 第三幕：身体对话
视频深度对话，实时生物数据分析。

**需要准备**:
- 30-60分钟连续时间
- 安静的对话环境
- 可选：智能手表用于HRV监测

### 第四幕：未来投影
共同完成模糊商业场景决策。

**目标**:
- 观察共享意义建构过程
- 评估叙事身份兼容性

### 终章：匹配报告
生成动态匹配景观和演化预测。

---

## 最佳实践

### 评估前准备

1. **心态准备**
   - 保持开放和诚实
   - 不要试图"正确回答"
   - 关注真实反应而非社会期望

2. **环境准备**
   - 选择不被打扰的时间
   - 确保网络稳定（视频对话）
   - 准备好纸笔记录想法

3. **合伙人准备**
   - 双方了解评估目的
   - 同意数据使用方式
   - 建立互信氛围

### 评估后行动

1. **讨论报告**
   - 与合伙人一起审阅结果
   - 关注建议而非分数
   - 识别共同改进空间

2. **制定计划**
   - 根据建议优先级排序
   - 设定具体行动项
   - 定期检查进度

3. **持续跟踪**
   - 使用动态仪表盘追踪变化
   - 定期重新评估（建议每季度）
   - 记录实际合作体验

---

## 常见问题

### Q: 评估结果是否固定不变？
**A**: 不是。系统支持动态更新，随着两人实际合作，可以重新评估获得更准确的结果。

### Q: 分数低是否意味着不适合合作？
**A**: 不一定。分数反映的是当前状态的兼容性，许多差距可以通过沟通和磨合来弥补。关注具体建议而非总分。

### Q: 如何处理分歧？
**A**: 参考报告中"冲突风险"和"沟通建议"部分。高冲突风险不意味着不能合作，而是需要建立更好的冲突管理机制。

### Q: 系统如何保护隐私？
**A**: 所有数据本地处理，支持区块链存证（可选）。生物数据仅用于即时分析，不长期存储。

---

## 进阶使用

### 自定义评估

```python
# 添加自定义问题
from core.entanglement_system import QuantumQuestion

question = QuantumQuestion(
    id='custom_1',
    text='你如何处理创业中的不确定性？',
    dimension='uncertainty_tolerance'
)

system.quantum_engine.register_question(question)
```

### 批量评估

```python
# 评估多个候选人
from core.entanglement_system import EntanglementMatchingSystem

system = EntanglementMatchingSystem()
candidates = [partner_b, partner_c, partner_d]

results = []
for candidate in candidates:
    result = system.comprehensive_match(partner_a, candidate)
    results.append({
        'candidate': candidate.name,
        'score': result['overall_compatibility']
    })

# 排序
results.sort(key=lambda x: x['score'], reverse=True)
```

### 集成第三方数据

```python
# 添加HRV数据
from core.entanglement_system import BiomarkerData

biomarker = BiomarkerData(
    timestamp=time.time(),
    hr=72,
    hrv=55,
    voice_pitch=120,
    voice_tremor=0.1
)

partner_a.biomarker_data.append(biomarker)
```

---

## 技术支持

### 问题反馈
如遇技术问题，请提供：
1. 错误信息截图
2. 操作步骤描述
3. 环境信息（Python版本、操作系统）

### 更新日志

#### V1.1 (2026-03-15)
- 六层架构完整实现
- 沉浸式Web界面
- 可视化模块
- 演示脚本和测试套件

---

**祝找到最佳合伙人，共创成功！**
