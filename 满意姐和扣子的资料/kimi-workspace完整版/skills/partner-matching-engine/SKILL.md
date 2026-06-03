> 生成时间: 2026-04-05 08:19+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# partner-matching-engine - 合伙人匹配引擎

## 描述
基于赫伯特·西蒙满意解理论、儒商五维评估与前景理论风险模型的合伙人匹配决策引擎。不追求"最优解"，而是以可接受的阈值截止搜索，生成可解释的匹配建议。

## 触发条件
- 用户要求进行"合伙人匹配"、"合伙人评估"
- 需要分析创始人与候选人的能力互补性
- 需要从儒商伦理或风险视角评估合伙关系

## 核心算法
1. **SatisficingMatcher** - 满意解匹配：设定阈值，首个满足阈值即停止搜索
2. **ComplementarityScorer** - 能力互补性评估：技术/商业/财务/团队/行业网络等8个维度
3. **ConfucianEthicsEvaluator** - 儒商伦理五维评估：仁、义、礼、智、信
4. **ProspectTheoryRiskScorer** - 前景理论风险兼容：损失厌恶、概率权重、参考点分析
5. **ExplanationGenerator** - 可解释性生成：结构化的匹配报告与风险提示

## 数据模型
- `FounderProfile` - 创始人画像（能力自评、决策风格、风险偏好、价值观）
- `CandidateProfile` - 候选人画像
- `MatchResult` - 匹配结果（综合得分、各维度得分、伦理评分、风险评分、建议）

## 使用方法
```bash
cd skills/partner-matching-engine/scripts
python3 partner_matching.py --help
python3 main.py
```

## 输出示例
引擎会生成结构化的匹配报告，包含：
- 综合匹配得分
- 能力互补雷达图数据
- 儒商伦理评分
- 前景理论风险分析
- 可执行建议与红旗警告

## 依赖
- Python 3.10+
- 仅标准库

## 版本
- 1.0.0
- 作者：满意解研究所
