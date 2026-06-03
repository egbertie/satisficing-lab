"""
适配器层: 将外援代码接入四层架构
实现TotemAgent抽象接口，内部调用外援实现
"""
from typing import List, Dict, Any
import sys
import os

# 添加reference目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'reference'))

from layers.architecture import (
    TotemAgent, Perspective, Scenario,
    PentadExtractor as PentadExtractorProtocol,
    HerbertSimonAgent as SimonProtocol,
    FiveTotemSystem
)

# 导入外援实现
from reference.pentad_extractor import PentadExtractor as ExternalPentadExtractor
from reference.simon_agent import HerbertSimonAgent as ExternalSimonAgent
from reference.five_totems_part1 import (
    LiuYuxiAgent as ExternalLiuYuxi,
    GuanZizaiAgent as ExternalGuanZizai,
    SimonTotemAdapter as ExternalSimonAdapter
)
from reference.five_totems_part2 import (
    ConfuciusAgent as ExternalConfucius,
    HuiNengAgent as ExternalHuiNeng,
    ConflictResolver as ExternalConflictResolver
)


class LiuYuxiTotemAdapter(TotemAgent):
    """刘禹锡(土)图腾适配器"""
    
    @property
    def name(self) -> str:
        return "刘禹锡"
    
    @property
    def element(self) -> str:
        return "土"
    
    @property
    def dimensions(self) -> List[str]:
        return ["品德匹配", "团队凝聚", "长期信任"]
    
    def __init__(self):
        self._impl = ExternalLiuYuxi()
    
    def evaluate(self, scenario: Scenario) -> Perspective:
        # 从scenario提取必要参数
        founder_values = scenario.founder_profile.get('values', [])
        # 取第一个候选人进行评估（五图腾评估单个候选人）
        if not scenario.candidates:
            return Perspective(
                totem_name=self.name,
                dimension="品德匹配",
                score=0.5,
                analysis="无候选人可评估",
                recommendation="需等待",
                confidence=0.0
            )
        
        candidate = scenario.candidates[0]
        result = self._impl.evaluate(founder_values, candidate)
        
        return Perspective(
            totem_name=self.name,
            dimension=result['dimension'],
            score=result['score'],
            analysis=result['analysis'],
            recommendation=result['recommendation'],
            confidence=0.8 if result['score'] > 0.6 else 0.6
        )


class SimonTotemWrapper(TotemAgent):
    """司马贺(金)图腾适配器"""
    
    @property
    def name(self) -> str:
        return "司马贺"
    
    @property
    def element(self) -> str:
        return "金"
    
    @property
    def dimensions(self) -> List[str]:
        return ["理性决策", "约束分析", "满意解"]
    
    def __init__(self):
        self._adapter = ExternalSimonAdapter()
    
    def evaluate(self, scenario: Scenario) -> Perspective:
        if not scenario.candidates:
            return Perspective(
                totem_name=self.name,
                dimension="满意解",
                score=0.5,
                analysis="无候选人可评估",
                recommendation="需等待",
                confidence=0.0
            )
        
        # 构建scenario dict
        scenario_dict = {
            'scenario': scenario.context,
            'constraints': scenario.constraints,
            'founder_profile': scenario.founder_profile,
            'candidates': scenario.candidates,
            'risk_preference': scenario.founder_profile.get('risk_preference', 'moderate')
        }
        
        # 评估第一个候选人
        candidate = scenario.candidates[0]
        result = self._adapter.evaluate(scenario_dict, candidate)
        
        return Perspective(
            totem_name=self.name,
            dimension=result['dimension'],
            score=result['score'],
            analysis=result['analysis'],
            recommendation=result['recommendation'],
            confidence=0.85 if result['score'] > 0.7 else 0.7
        )


class GuanZizaiTotemAdapter(TotemAgent):
    """观自在(水)图腾适配器"""
    
    @property
    def name(self) -> str:
        return "观自在"
    
    @property
    def element(self) -> str:
        return "水"
    
    @property
    def dimensions(self) -> List[str]:
        return ["直觉洞察", "压力应对", "内心自由"]
    
    def __init__(self):
        self._impl = ExternalGuanZizai()
    
    def evaluate(self, scenario: Scenario) -> Perspective:
        if not scenario.candidates:
            return Perspective(
                totem_name=self.name,
                dimension="直觉洞察",
                score=0.5,
                analysis="无候选人可评估",
                recommendation="需等待",
                confidence=0.0
            )
        
        result = self._impl.evaluate(scenario.founder_profile, scenario.candidates[0])
        
        return Perspective(
            totem_name=self.name,
            dimension=result['dimension'],
            score=result['score'],
            analysis=result['analysis'],
            recommendation=result['recommendation'],
            confidence=0.75 if result['score'] > 0.5 else 0.6
        )


class ConfuciusTotemAdapter(TotemAgent):
    """孔子(木)图腾适配器"""
    
    @property
    def name(self) -> str:
        return "孔子"
    
    @property
    def element(self) -> str:
        return "木"
    
    @property
    def dimensions(self) -> List[str]:
        return ["仁义礼智信", "伦理评估", "长期信任"]
    
    def __init__(self):
        self._impl = ExternalConfucius()
    
    def evaluate(self, scenario: Scenario) -> Perspective:
        if not scenario.candidates:
            return Perspective(
                totem_name=self.name,
                dimension="五常伦理",
                score=0.5,
                analysis="无候选人可评估",
                recommendation="需等待",
                confidence=0.0
            )
        
        founder_values = scenario.founder_profile.get('values', [])
        result = self._impl.evaluate(founder_values, scenario.candidates[0])
        
        return Perspective(
            totem_name=self.name,
            dimension=result['dimension'],
            score=result['score'],
            analysis=result['analysis'],
            recommendation=result['recommendation'],
            confidence=0.8 if result['score'] > 0.6 else 0.65
        )


class HuiNengTotemAdapter(TotemAgent):
    """慧能(火)图腾适配器"""
    
    @property
    def name(self) -> str:
        return "六祖慧能"
    
    @property
    def element(self) -> str:
        return "火"
    
    @property
    def dimensions(self) -> List[str]:
        return ["创新突破", "压力转化", "顿悟能力"]
    
    def __init__(self):
        self._impl = ExternalHuiNeng()
    
    def evaluate(self, scenario: Scenario) -> Perspective:
        if not scenario.candidates:
            return Perspective(
                totem_name=self.name,
                dimension="顿悟创新",
                score=0.5,
                analysis="无候选人可评估",
                recommendation="需等待",
                confidence=0.0
            )
        
        result = self._impl.evaluate(scenario.founder_profile, scenario.candidates[0])
        
        return Perspective(
            totem_name=self.name,
            dimension=result['dimension'],
            score=result['score'],
            analysis=result['analysis'],
            recommendation=result['recommendation'],
            confidence=0.75 if result['score'] > 0.7 else 0.6
        )


class IntegratedFiveTotemSystem:
    """
    集成的五图腾系统
    组合五个图腾适配器 + 冲突消解器
    """
    def __init__(self):
        self.totems = {
            'liuyuxi': LiuYuxiTotemAdapter(),
            'simon': SimonTotemWrapper(),
            'guanzizai': GuanZizaiTotemAdapter(),
            'confucius': ConfuciusTotemAdapter(),
            'huineng': HuiNengTotemAdapter()
        }
        self.resolver = ExternalConflictResolver()
    
    def evaluate(self, scenario: Scenario) -> Dict[str, Any]:
        """
        运行五图腾评估 + 冲突消解
        返回综合结果
        """
        # 收集五个图腾的观点
        perspectives = {}
        evaluations = {}
        
        for key, totem in self.totems.items():
            perspective = totem.evaluate(scenario)
            perspectives[key] = perspective
            evaluations[key] = {
                'score': perspective.score,
                'analysis': perspective.analysis,
                'recommendation': perspective.recommendation
            }
        
        # 运行冲突消解
        scenario_dict = {
            'context': scenario.context,
            'constraints': scenario.constraints
        }
        resolution = self.resolver.resolve(evaluations, scenario_dict)
        
        return {
            'perspectives': perspectives,
            'consensus': resolution,
            'final_score': resolution['consensus_score'],
            'conflicts': resolution['conflicts_detected']
        }
