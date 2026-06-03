# QPMS 量子感知引擎算法效度验证报告
**生成时间**: 2026-04-06 12:27

## 一、ECBM 躯体信号模块验证
```json
{
  "sample_size": 50,
  "anxiety_stability_r": -0.245,
  "defense_stability_r": -0.439,
  "openness_stability_r": 0.454,
  "interpretation": {
    "anxiety": "负相关（焦虑信号越高，团队稳定性越低）",
    "defense": "负相关（防御信号越高，团队稳定性越低）",
    "openness": "正相关（开放信号越高，团队稳定性越高）"
  },
  "note": "预期中等效应量 r=0.30-0.40；本框架使用合成数据演示计算流程，真实研究需替换为实际采集数据。"
}
```

## 二、REPA 伦理对齐模块验证
```json
{
  "sample_size": 100,
  "cohens_d": 3.704,
  "spearman_rho": -0.581,
  "auc_roc": 0.838,
  "ece": 0.064,
  "brier_score": 0.165,
  "threshold_check": {
    "cohens_d_target": ">0.5",
    "spearman_rho_target": ">0.4",
    "auc_roc_target": ">0.75",
    "ece_target": "<0.1"
  },
  "note": "预期：区分效度 d>0.5，排序效度 ρ>0.4，预测效度 AUC>0.75，校准误差 ECE<0.1。"
}
```

## 三、ETDS 涌现匹配模块验证
```json
{
  "sample_size": 80,
  "etds_outcome_r": 0.955,
  "ability_outcome_r": 0.047,
  "advantage_scenarios": [
    "价值观冲突情境：ETDS 相对优势显著（捕捉隐性张力）",
    "能力不匹配情境：传统规则已覆盖，ETDS 优势有限",
    "外部冲击情境：两者均可预测"
  ],
  "note": "真实研究需通过分样本（价值观冲突子样本 vs 能力不匹配子样本）进行调节效应检验。"
}
```

## 四、偏误控制机制检查清单
```json
{
  "事后偏差防御": {
    "盲法评估设计": "结局标注与躯体信号编码由不知晓对方信息的研究员独立完成",
    "时间切片验证": "按时间排序案例，用前N个训练、预测第N+1个",
    "元认知监控": "记录分析前预测与推理，纳入敏感性分析"
  },
  "过拟合防御": {
    "检测": "样本外验证、交叉验证（k-fold/LOOCV）、置换检验",
    "预防": "正则化（L1/L2）、早停（early stopping）、特征选择",
    "简约性原则": "模型复杂度与样本量匹配"
  }
}
```