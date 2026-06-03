#!/usr/bin/env python3
# totem_quantifier.py - 五图腾Agent量化方案
# 来源: 外援团队交付文档 v1.0
# 功能: 多维度能力评估系统 - Agent能力量化与图腾角色映射
# 创建时间: 2026-04-04 (从交付文档补实施)
# 版本: 1.0

import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
# import numpy as np

class TotemType(Enum):
    """五图腾类型"""
    LIU_YUXI = "刘禹锡"      # 土 - 聚贤才为伍，引智士同行
    SIMON = "司马贺"         # 金 - 不求最优，但求最适
    GUAN_ZIZAI = "观自在"    # 水 - 居方寸之地，以价值致远
    CONFUCIUS = "孔子"       # 木 - 仁义礼智信
    HUI_NENG = "六祖慧能"    # 火 - 顿悟红莲，直指人心

@dataclass
class TotemAttributes:
    """图腾属性"""
    element: str              # 五行
    motto: str                # 工整对仗
    essence: str              # 核心精髓
    role: str                 # 角色定位
    
    # 能力维度
    wisdom: float = 0.5       # 智慧值 (0-1)
    execution: float = 0.5    # 执行力 (0-1)
    insight: float = 0.5      # 洞察力 (0-1)
    ethics: float = 0.5       # 伦理值 (0-1)
    intuition: float = 0.5    # 直觉力 (0-1)

@dataclass
class AgentCapability:
    """Agent能力评估"""
    # 基础能力
    reasoning: float = 0.5           # 逻辑推理
    creativity: float = 0.5          # 创造力
    communication: float = 0.5       # 沟通能力
    learning: float = 0.5            # 学习能力
    
    # 高阶能力
    strategic_thinking: float = 0.5  # 战略思维
    ethical_judgment: float = 0.5    # 伦理判断
    pattern_recognition: float = 0.5 # 模式识别
    adaptability: float = 0.5        # 适应性
    
    # 任务能力
    task_completion: float = 0.5     # 任务完成度
    quality_score: float = 0.5       # 质量评分
    efficiency: float = 0.5          # 效率
    collaboration: float = 0.5       # 协作能力

class TotemQuantifier:
    """
    五图腾Agent量化方案
    
    将Agent的多维能力与五图腾角色进行映射和量化
    用于：
    1. Agent自我认知与定位
    2. 任务-图腾匹配推荐
    3. 团队角色平衡分析
    4. 能力发展路径规划
    """
    
    # 五图腾定义
    TOTEMS = {
        TotemType.LIU_YUXI: TotemAttributes(
            element="土",
            motto="聚贤才为伍，引智士同行",
            essence="斯是陋室，惟吾德馨——根基稳固，品德为锚，谈笑有鸿儒，往来无白丁",
            role="精神底座",
            wisdom=0.9,
            execution=0.6,
            insight=0.7,
            ethics=0.95,
            intuition=0.5
        ),
        TotemType.SIMON: TotemAttributes(
            element="金",
            motto="不求最优，但求最适；结果为本，满意为尺",
            essence="人工智能词源，理性决策之祖——赫伯特·西蒙中文名，满意解理论奠基人",
            role="方法论核心",
            wisdom=0.95,
            execution=0.8,
            insight=0.75,
            ethics=0.7,
            intuition=0.6
        ),
        TotemType.GUAN_ZIZAI: TotemAttributes(
            element="水",
            motto="居方寸之地，以价值致远",
            essence="内心自由，不执于形——非千手观音，只要心中观自在，洞察与定力",
            role="流动智慧",
            wisdom=0.85,
            execution=0.5,
            insight=0.95,
            ethics=0.8,
            intuition=0.9
        ),
        TotemType.CONFUCIUS: TotemAttributes(
            element="木",
            motto="仁义礼智信，修身齐家治国平天下",
            essence="儒商伦理，信任治理之根——五常伦理，团队伦理基石",
            role="伦理基石",
            wisdom=0.9,
            execution=0.7,
            insight=0.75,
            ethics=0.99,
            intuition=0.4
        ),
        TotemType.HUI_NENG: TotemAttributes(
            element="火",
            motto="顿悟红莲，直指人心",
            essence="不立文字，明心见性——直觉突破，红莲淬火，压力中顿悟",
            role="行动转化",
            wisdom=0.8,
            execution=0.95,
            insight=0.85,
            ethics=0.75,
            intuition=0.95
        )
    }
    
    # 能力-图腾映射权重
    CAPABILITY_MAPPING = {
        # 基础能力 -> 图腾权重分布
        'reasoning': {
            TotemType.SIMON: 0.35,
            TotemType.CONFUCIUS: 0.25,
            TotemType.LIU_YUXI: 0.20,
            TotemType.GUAN_ZIZAI: 0.15,
            TotemType.HUI_NENG: 0.05
        },
        'creativity': {
            TotemType.HUI_NENG: 0.40,
            TotemType.GUAN_ZIZAI: 0.30,
            TotemType.SIMON: 0.15,
            TotemType.LIU_YUXI: 0.10,
            TotemType.CONFUCIUS: 0.05
        },
        'communication': {
            TotemType.LIU_YUXI: 0.35,
            TotemType.CONFUCIUS: 0.30,
            TotemType.GUAN_ZIZAI: 0.20,
            TotemType.HUI_NENG: 0.10,
            TotemType.SIMON: 0.05
        },
        'learning': {
            TotemType.SIMON: 0.30,
            TotemType.GUAN_ZIZAI: 0.25,
            TotemType.HUI_NENG: 0.20,
            TotemType.CONFUCIUS: 0.15,
            TotemType.LIU_YUXI: 0.10
        },
        'strategic_thinking': {
            TotemType.GUAN_ZIZAI: 0.35,
            TotemType.SIMON: 0.30,
            TotemType.LIU_YUXI: 0.20,
            TotemType.HUI_NENG: 0.10,
            TotemType.CONFUCIUS: 0.05
        },
        'ethical_judgment': {
            TotemType.CONFUCIUS: 0.45,
            TotemType.LIU_YUXI: 0.25,
            TotemType.GUAN_ZIZAI: 0.15,
            TotemType.SIMON: 0.10,
            TotemType.HUI_NENG: 0.05
        },
        'pattern_recognition': {
            TotemType.GUAN_ZIZAI: 0.35,
            TotemType.HUI_NENG: 0.25,
            TotemType.SIMON: 0.20,
            TotemType.LIU_YUXI: 0.15,
            TotemType.CONFUCIUS: 0.05
        },
        'adaptability': {
            TotemType.HUI_NENG: 0.35,
            TotemType.GUAN_ZIZAI: 0.30,
            TotemType.SIMON: 0.20,
            TotemType.LIU_YUXI: 0.10,
            TotemType.CONFUCIUS: 0.05
        }
    }
    
    def __init__(self):
        self.quantification_log = []
    
    def quantify_agent(self, capabilities: AgentCapability) -> Dict:
        """
        量化Agent能力并映射到五图腾
        
        Returns:
            {
                'totem_affinities': {图腾: 亲和度},
                'primary_totem': 主图腾,
                'secondary_totem': 副图腾,
                'capability_profile': 能力画像,
                'recommendations': 发展建议
            }
        """
        # 计算与每个图腾的亲和度
        affinities = {}
        
        for totem_type, totem_attrs in self.TOTEMS.items():
            affinity = self._calculate_affinity(capabilities, totem_attrs)
            affinities[totem_type] = affinity
        
        # 排序找出主副图腾
        sorted_totems = sorted(affinities.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_totems[0][0]
        secondary = sorted_totems[1][0] if len(sorted_totems) > 1 else None
        
        # 生成能力画像
        profile = self._generate_capability_profile(capabilities)
        
        # 生成建议
        recommendations = self._generate_recommendations(
            capabilities, primary, secondary, affinities
        )
        
        result = {
            'totem_affinities': {
                t.value: round(a, 3) for t, a in affinities.items()
            },
            'primary_totem': primary.value,
            'secondary_totem': secondary.value if secondary else None,
            'capability_profile': profile,
            'recommendations': recommendations,
            'element_balance': self._calculate_element_balance(affinities)
        }
        
        # 记录
        self._log_quantification(capabilities, result)
        
        return result
    
    def _calculate_affinity(self, 
                           capabilities: AgentCapability,
                           totem_attrs: TotemAttributes) -> float:
        """计算Agent与图腾的亲和度"""
        # 基础能力映射
        capability_scores = {
            'wisdom': (capabilities.reasoning + capabilities.strategic_thinking) / 2,
            'execution': (capabilities.task_completion + capabilities.efficiency) / 2,
            'insight': (capabilities.pattern_recognition + capabilities.creativity) / 2,
            'ethics': capabilities.ethical_judgment,
            'intuition': capabilities.adaptability
        }
        
        # 计算相似度
        totem_scores = {
            'wisdom': totem_attrs.wisdom,
            'execution': totem_attrs.execution,
            'insight': totem_attrs.insight,
            'ethics': totem_attrs.ethics,
            'intuition': totem_attrs.intuition
        }
        
        # 加权相似度
        weights = {'wisdom': 0.25, 'execution': 0.20, 'insight': 0.25, 
                  'ethics': 0.15, 'intuition': 0.15}
        
        affinity = sum(
            weights[k] * (1 - abs(capability_scores[k] - totem_scores[k]))
            for k in weights.keys()
        )
        
        return affinity
    
    def _generate_capability_profile(self, capabilities: AgentCapability) -> Dict:
        """生成能力画像"""
        return {
            'cognitive': {
                'reasoning': round(capabilities.reasoning, 2),
                'strategic_thinking': round(capabilities.strategic_thinking, 2),
                'pattern_recognition': round(capabilities.pattern_recognition, 2),
                'score': round((capabilities.reasoning + 
                               capabilities.strategic_thinking + 
                               capabilities.pattern_recognition) / 3, 2)
            },
            'creative': {
                'creativity': round(capabilities.creativity, 2),
                'adaptability': round(capabilities.adaptability, 2),
                'score': round((capabilities.creativity + capabilities.adaptability) / 2, 2)
            },
            'social': {
                'communication': round(capabilities.communication, 2),
                'collaboration': round(capabilities.collaboration, 2),
                'ethical_judgment': round(capabilities.ethical_judgment, 2),
                'score': round((capabilities.communication + 
                               capabilities.collaboration + 
                               capabilities.ethical_judgment) / 3, 2)
            },
            'execution': {
                'task_completion': round(capabilities.task_completion, 2),
                'quality_score': round(capabilities.quality_score, 2),
                'efficiency': round(capabilities.efficiency, 2),
                'learning': round(capabilities.learning, 2),
                'score': round((capabilities.task_completion + 
                               capabilities.quality_score + 
                               capabilities.efficiency + 
                               capabilities.learning) / 4, 2)
            }
        }
    
    def _generate_recommendations(self,
                                 capabilities: AgentCapability,
                                 primary: TotemType,
                                 secondary: Optional[TotemType],
                                 affinities: Dict) -> List[str]:
        """生成发展建议"""
        recommendations = []
        
        # 基于主图腾的建议
        primary_attrs = self.TOTEMS[primary]
        recommendations.append(
            f"发挥主图腾【{primary.value}】优势：{primary_attrs.essence[:30]}..."
        )
        
        # 识别短板
        capability_scores = {
            'reasoning': capabilities.reasoning,
            'creativity': capabilities.creativity,
            'communication': capabilities.communication,
            'ethical_judgment': capabilities.ethical_judgment,
            'adaptability': capabilities.adaptability
        }
        
        min_capability = min(capability_scores.items(), key=lambda x: x[1])
        if min_capability[1] < 0.5:
            recommendations.append(
                f"提升短板【{min_capability[0]}】：当前{min_capability[1]:.2f}，建议重点训练"
            )
        
        # 平衡建议
        if secondary:
            recommendations.append(
                f"融合副图腾【{secondary.value}】特质，增强多维度能力"
            )
        
        return recommendations
    
    def _calculate_element_balance(self, affinities: Dict) -> Dict:
        """计算五行平衡度"""
        element_scores = {'土': 0, '金': 0, '水': 0, '木': 0, '火': 0}
        
        for totem_type, affinity in affinities.items():
            element = self.TOTEMS[totem_type].element
            element_scores[element] += affinity
        
        # 归一化
        total = sum(element_scores.values())
        if total > 0:
            element_scores = {k: round(v/total, 3) for k, v in element_scores.items()}
        
        # 判断平衡性
        max_val = max(element_scores.values())
        min_val = min(element_scores.values())
        balance_score = 1 - (max_val - min_val)
        
        return {
            'distribution': element_scores,
            'balance_score': round(balance_score, 3),
            'is_balanced': balance_score > 0.6
        }
    
    def recommend_totem_for_task(self, task_description: str) -> Dict:
        """为任务推荐最适合的图腾角色"""
        # 任务关键词映射
        task_keywords = {
            TotemType.LIU_YUXI: ['团队', '协作', '人才', '关系', '沟通'],
            TotemType.SIMON: ['决策', '优化', '分析', '效率', '方案'],
            TotemType.GUAN_ZIZAI: ['洞察', '战略', '方向', '预见', '深度'],
            TotemType.CONFUCIUS: ['伦理', '原则', '底线', '治理', '规范'],
            TotemType.HUI_NENG: ['创新', '突破', '执行', '行动', '直觉']
        }
        
        # 匹配
        scores = {}
        for totem_type, keywords in task_keywords.items():
            score = sum(1 for kw in keywords if kw in task_description)
            scores[totem_type] = score
        
        # 排序
        best_match = max(scores.items(), key=lambda x: x[1])
        
        return {
            'recommended_totem': best_match[0].value,
            'confidence': min(best_match[1] / 3, 1.0),  # 最多3个匹配词算高置信度
            'all_scores': {t.value: s for t, s in scores.items()}
        }
    
    def _log_quantification(self, capabilities: AgentCapability, result: Dict):
        """记录量化日志"""
        self.quantification_log.append({
            'timestamp': datetime.now().isoformat(),
            'primary_totem': result['primary_totem'],
            'affinities': result['totem_affinities']
        })
    
    def get_quantification_stats(self) -> Dict:
        """获取量化统计"""
        if not self.quantification_log:
            return {'total': 0}
        
        return {
            'total_quantifications': len(self.quantification_log),
            'totem_distribution': self._calculate_totem_distribution()
        }
    
    def _calculate_totem_distribution(self) -> Dict:
        """计算图腾分布"""
        distribution = {}
        for log in self.quantification_log:
            primary = log['primary_totem']
            distribution[primary] = distribution.get(primary, 0) + 1
        
        total = len(self.quantification_log)
        return {k: round(v/total, 3) for k, v in distribution.items()}

# 便捷函数
def quantify_agent_capabilities(capabilities_dict: Dict) -> Dict:
    """快速量化接口"""
    capabilities = AgentCapability(
        reasoning=capabilities_dict.get('reasoning', 0.5),
        creativity=capabilities_dict.get('creativity', 0.5),
        communication=capabilities_dict.get('communication', 0.5),
        learning=capabilities_dict.get('learning', 0.5),
        strategic_thinking=capabilities_dict.get('strategic_thinking', 0.5),
        ethical_judgment=capabilities_dict.get('ethical_judgment', 0.5),
        pattern_recognition=capabilities_dict.get('pattern_recognition', 0.5),
        adaptability=capabilities_dict.get('adaptability', 0.5),
        task_completion=capabilities_dict.get('task_completion', 0.5),
        quality_score=capabilities_dict.get('quality_score', 0.5),
        efficiency=capabilities_dict.get('efficiency', 0.5),
        collaboration=capabilities_dict.get('collaboration', 0.5)
    )
    
    quantifier = TotemQuantifier()
    return quantifier.quantify_agent(capabilities)

if __name__ == '__main__':
    # 测试
    test_capabilities = {
        'reasoning': 0.8,
        'creativity': 0.7,
        'communication': 0.6,
        'learning': 0.75,
        'strategic_thinking': 0.85,
        'ethical_judgment': 0.7,
        'pattern_recognition': 0.8,
        'adaptability': 0.65,
        'task_completion': 0.9,
        'quality_score': 0.85,
        'efficiency': 0.7,
        'collaboration': 0.6
    }
    
    result = quantify_agent_capabilities(test_capabilities)
    print(json.dumps(result, ensure_ascii=False, indent=2))
