"""
Entanglement Partner Matching System (EPMS) V1.1
量子纠缠合伙人匹配决策系统

基于神经科学、复杂系统理论和量子认知的全球首创决策生态系统

参考设计哲学:
- Dieter Rams: Less but better
- Bret Victor: Seeing the invisible
- Christopher Alexander: Living structures
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
import numpy as np
from collections import defaultdict
import random
import json
from datetime import datetime

# ============================================================
# Layer 1: 量子化感知引擎 (Quantum Perception Engine)
# ============================================================

class QuantumState(Enum):
    """量子叠加态"""
    SUPERPOSITION = auto()  # 叠加态
    ENTANGLED = auto()      # 纠缠态
    COLLAPSED = auto()      # 坍缩态

@dataclass
class WaveFunction:
    """
    认知波函数 ψ = α|StateA⟩ + β|StateB⟩ + γ|StateC⟩
    用概率幅表示认知状态的叠加
    """
    amplitudes: Dict[str, complex] = field(default_factory=dict)
    
    def normalize(self):
        """归一化波函数"""
        total_prob = sum(abs(a)**2 for a in self.amplitudes.values())
        if total_prob > 0:
            for key in self.amplitudes:
                self.amplitudes[key] /= np.sqrt(total_prob)
    
    def measure(self, context: Dict = None) -> str:
        """
        测量导致坍缩
        根据概率幅随机坍缩到一个确定态
        """
        self.normalize()
        states = list(self.amplitudes.keys())
        probs = [abs(self.amplitudes[s])**2 for s in states]
        
        # 上下文可能影响坍缩概率
        if context and 'bias' in context:
            bias = context['bias']
            for i, s in enumerate(states):
                if s in bias:
                    probs[i] *= bias[s]
        
        probs = np.array(probs) / sum(probs)
        collapsed = np.random.choice(states, p=probs)
        return collapsed
    
    def entangle_with(self, other: 'WaveFunction', strength: float = 0.5) -> 'WaveFunction':
        """
        两个波函数纠缠
        创建一个联合波函数表示认知纠缠
        """
        entangled = WaveFunction()
        for s1, a1 in self.amplitudes.items():
            for s2, a2 in other.amplitudes.items():
                joint_state = f"{s1}⊗{s2}"
                # 纠缠强度影响联合振幅
                entangled.amplitudes[joint_state] = a1 * a2 * (1 + strength)
        entangled.normalize()
        return entangled

@dataclass
class QuantumQuestion:
    """
    量子化问题
    问题之间存在非经典关联（纠缠）
    """
    id: str
    text: str
    dimension: str  # 所属维度：价值观、认知风格、风险偏好等
    wave_function: WaveFunction = field(default_factory=lambda: WaveFunction())
    entangled_with: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.wave_function.amplitudes:
            # 默认创建叠加态
            self.wave_function.amplitudes = {
                'high': 0.5 + 0.1j,
                'medium': 0.4 + 0.2j,
                'low': 0.3 - 0.1j
            }
            self.wave_function.normalize()

class QuantumEngine:
    """
    量子化感知引擎
    核心创新：抛弃传统Likert量表，使用量子叠加态评估
    """
    
    def __init__(self):
        self.questions: Dict[str, QuantumQuestion] = {}
        self.response_history: List[Dict] = []
        
    def register_question(self, question: QuantumQuestion):
        """注册量子问题"""
        self.questions[question.id] = question
        
    def answer_question(self, qid: str, context: Dict = None) -> Tuple[str, float]:
        """
        回答问题导致波函数坍缩
        返回坍缩状态和确定性程度
        """
        if qid not in self.questions:
            raise ValueError(f"未知问题: {qid}")
        
        question = self.questions[qid]
        
        # 纠缠问题会影响当前问题的坍缩概率
        if context and 'previous_answers' in context:
            prev = context['previous_answers']
            for entangled_id in question.entangled_with:
                if entangled_id in prev:
                    # 纠缠效应：先前答案会改变当前概率幅
                    self._apply_entanglement_effect(question, entangled_id, prev[entangled_id])
        
        # 测量导致坍缩
        collapsed_state = question.wave_function.measure(context)
        
        # 计算确定性程度（香农熵的补）
        probs = [abs(a)**2 for a in question.wave_function.amplitudes.values()]
        entropy = -sum(p * np.log2(p) for p in probs if p > 0)
        certainty = 1 - (entropy / np.log2(len(probs)))
        
        # 记录响应
        self.response_history.append({
            'question_id': qid,
            'collapsed_state': collapsed_state,
            'certainty': certainty,
            'timestamp': datetime.now().isoformat()
        })
        
        return collapsed_state, certainty
    
    def _apply_entanglement_effect(self, question: QuantumQuestion, 
                                   other_id: str, other_answer: str):
        """应用纠缠效应：一个问题改变另一个问题的概率幅"""
        # 简化的纠缠模型：如果两个问题纠缠，答案会相互影响
        if other_answer == 'high':
            # 提升当前问题倾向于high的概率
            if 'high' in question.wave_function.amplitudes:
                question.wave_function.amplitudes['high'] *= 1.3
        elif other_answer == 'low':
            if 'low' in question.wave_function.amplitudes:
                question.wave_function.amplitudes['low'] *= 1.3
        question.wave_function.normalize()

# ============================================================
# Layer 2: 涌现式匹配算法 (Emergent Matching Algorithm)
# ============================================================

class CognitiveAgent:
    """
    认知代理
    模拟个体在决策场景中的认知模式
    """
    
    def __init__(self, name: str, cognitive_profile: Dict):
        self.name = name
        self.profile = cognitive_profile
        self.decision_history: List[Dict] = []
        
        # 认知特征参数
        self.analytical = cognitive_profile.get('analytical', 0.5)
        self.intuitive = cognitive_profile.get('intuitive', 0.5)
        self.risk_tolerance = cognitive_profile.get('risk_tolerance', 0.5)
        self.detail_focus = cognitive_profile.get('detail_focus', 0.5)
        self.speed = cognitive_profile.get('decision_speed', 0.5)
        
    def make_decision(self, scenario: Dict, partner: Optional['CognitiveAgent'] = None) -> Dict:
        """
        在场景中做出决策
        如果有合作伙伴，会受到协作影响
        """
        scenario_type = scenario.get('type', 'neutral')
        complexity = scenario.get('complexity', 0.5)
        
        # 基础决策倾向
        base_inclination = self._calculate_inclination(scenario)
        
        # 如果有合作伙伴，计算协作影响
        if partner:
            influence = self._calculate_partner_influence(partner, scenario)
            # 协作模式：同步/互补/冲突/创造
            collaboration_mode = self._identify_collaboration_mode(partner, influence)
            final_decision = self._blend_decisions(base_inclination, influence, collaboration_mode)
        else:
            final_decision = base_inclination
            collaboration_mode = 'solo'
        
        decision_record = {
            'scenario': scenario,
            'decision': final_decision,
            'mode': collaboration_mode,
            'timestamp': datetime.now().isoformat()
        }
        self.decision_history.append(decision_record)
        
        return decision_record
    
    def _calculate_inclination(self, scenario: Dict) -> float:
        """基于认知档案计算决策倾向"""
        if scenario['type'] == 'risky':
            return self.risk_tolerance
        elif scenario['type'] == 'analytical':
            return self.analytical
        elif scenario['type'] == 'creative':
            return self.intuitive
        else:
            return 0.5
    
    def _calculate_partner_influence(self, partner: 'CognitiveAgent', scenario: Dict) -> float:
        """计算合作伙伴的影响"""
        # 认知差异产生张力
        analytical_gap = abs(self.analytical - partner.analytical)
        risk_gap = abs(self.risk_tolerance - partner.risk_tolerance)
        
        # 适度差异促进创新，过大差异导致冲突
        optimal_gap = 0.3
        tension = 1 - abs(analytical_gap - optimal_gap) / max(optimal_gap, 1-optimal_gap)
        
        return {
            'analytical_influence': partner.analytical * tension,
            'tension': tension,
            'cognitive_distance': np.sqrt(analytical_gap**2 + risk_gap**2)
        }
    
    def _identify_collaboration_mode(self, partner: 'CognitiveAgent', influence: Dict) -> str:
        """识别协作模式"""
        distance = influence['cognitive_distance']
        tension = influence['tension']
        
        if distance < 0.2:
            return 'synchronization'  # 同步
        elif distance > 0.6:
            return 'conflict'  # 冲突
        elif tension > 0.7:
            return 'complementary'  # 互补
        else:
            return 'generative'  # 创造
    
    def _blend_decisions(self, base: float, influence: Dict, mode: str) -> float:
        """混合决策"""
        if mode == 'synchronization':
            return (base + influence['analytical_influence']) / 2
        elif mode == 'complementary':
            return base + influence['tension'] * 0.2
        elif mode == 'generative':
            return (base + influence['analytical_influence']) / 2 + 0.1
        else:  # conflict
            return base - 0.1

class EmergentMatcher:
    """
    涌现式匹配算法
    通过多智能体模拟预测团队心智的涌现结构
    """
    
    def __init__(self):
        self.scenarios: List[Dict] = []
        self.simulation_results: List[Dict] = []
        
        # 预定义测试场景
        self._init_scenarios()
    
    def _init_scenarios(self):
        """初始化决策场景库"""
        self.scenarios = [
            {'id': 1, 'type': 'crisis', 'complexity': 0.8, 'description': '突发供应链中断'},
            {'id': 2, 'type': 'innovation', 'complexity': 0.7, 'description': '技术路线抉择'},
            {'id': 3, 'type': 'conflict', 'complexity': 0.6, 'description': '核心团队分歧'},
            {'id': 4, 'type': 'growth', 'complexity': 0.5, 'description': '快速扩张决策'},
            {'id': 5, 'type': 'ethical', 'complexity': 0.9, 'description': '义利冲突情境'},
            {'id': 6, 'type': 'financial', 'complexity': 0.7, 'description': '融资策略选择'},
        ]
    
    def simulate_partnership(self, agent_a: CognitiveAgent, agent_b: CognitiveAgent, 
                            n_scenarios: int = 100) -> Dict:
        """
        模拟两人合作系统
        在多个虚拟场景中协作，观察涌现特性
        """
        collaboration_modes = defaultdict(int)
        decision_consistency = []
        creative_moments = 0
        
        for i in range(n_scenarios):
            scenario = random.choice(self.scenarios)
            
            # 两人独立决策
            decision_a = agent_a.make_decision(scenario)
            decision_b = agent_b.make_decision(scenario)
            
            # 协作决策
            joint_decision_a = agent_a.make_decision(scenario, agent_b)
            joint_decision_b = agent_b.make_decision(scenario, agent_a)
            
            # 记录协作模式
            mode = joint_decision_a['mode']
            collaboration_modes[mode] += 1
            
            # 检测创造性时刻（产生优于个体决策的联合决策）
            individual_avg = (decision_a['decision'] + decision_b['decision']) / 2
            joint_avg = (joint_decision_a['decision'] + joint_decision_b['decision']) / 2
            if abs(joint_avg - 0.5) > abs(individual_avg - 0.5):
                creative_moments += 1
        
        # 计算吸引子景观
        attractors = self._identify_attractors(collaboration_modes, n_scenarios)
        
        result = {
            'collaboration_pattern': dict(collaboration_modes),
            'dominant_mode': max(collaboration_modes, key=collaboration_modes.get),
            'creativity_index': creative_moments / n_scenarios,
            'attractors': attractors,
            'stability_score': self._calculate_stability(attractors),
            'emergence_score': self._calculate_emergence(collaboration_modes)
        }
        
        self.simulation_results.append({
            'agent_a': agent_a.name,
            'agent_b': agent_b.name,
            'result': result
        })
        
        return result
    
    def _identify_attractors(self, modes: Dict, total: int) -> List[Dict]:
        """识别稳定吸引子（长期合作模式）"""
        attractors = []
        for mode, count in modes.items():
            ratio = count / total
            if ratio > 0.3:  # 稳定吸引子阈值
                attractors.append({
                    'mode': mode,
                    'strength': ratio,
                    'stability': ratio * (1 - ratio)  # 越接近0.5越不稳定
                })
        return sorted(attractors, key=lambda x: x['strength'], reverse=True)
    
    def _calculate_stability(self, attractors: List[Dict]) -> float:
        """计算系统稳定性"""
        if not attractors:
            return 0.5
        # 强吸引子意味着稳定
        return sum(a['strength'] for a in attractors) / len(attractors)
    
    def _calculate_emergence(self, modes: Dict) -> float:
        """计算涌现性（熵）"""
        total = sum(modes.values())
        probs = [c/total for c in modes.values()]
        # 适度的熵表示丰富的涌现行为
        entropy = -sum(p * np.log2(p) for p in probs if p > 0)
        max_entropy = np.log2(len(modes))
        return entropy / max_entropy if max_entropy > 0 else 0

# ============================================================
# Layer 3: 身体化认知测评 (Embodied Cognition Assessment)
# ============================================================

@dataclass
class BiomarkerData:
    """生物标记数据"""
    timestamp: float
    hr: float  # 心率
    hrv: float  # 心率变异性
    voice_pitch: float  # 语音基频
    voice_tremor: float  # 语音颤抖
    micro_expression: Optional[str] = None

class EmbodiedAnalyzer:
    """
    身体化认知分析器
    分析具身数据以识别潜意识层面的共鸣/排斥
    """
    
    def __init__(self):
        self.partner_a_data: List[BiomarkerData] = []
        self.partner_b_data: List[BiomarkerData] = []
    
    def add_data(self, partner: str, data: BiomarkerData):
        """添加生物数据"""
        if partner == 'A':
            self.partner_a_data.append(data)
        else:
            self.partner_b_data.append(data)
    
    def calculate_hrv_synchronization(self) -> float:
        """
        计算心率变异性同步性
        反映潜意识层面的共鸣
        """
        if len(self.partner_a_data) < 2 or len(self.partner_b_data) < 2:
            return 0.5
        
        hrv_a = [d.hrv for d in self.partner_a_data]
        hrv_b = [d.hrv for d in self.partner_b_data]
        
        # 计算HRV序列的相关性
        min_len = min(len(hrv_a), len(hrv_b))
        if min_len < 2:
            return 0.5
        
        correlation = np.corrcoef(hrv_a[:min_len], hrv_b[:min_len])[0, 1]
        # 转换为0-1分数
        sync_score = (correlation + 1) / 2
        return sync_score
    
    def analyze_vocal_resonance(self) -> Dict:
        """分析语音共鸣"""
        if not self.partner_a_data or not self.partner_b_data:
            return {'pitch_resonance': 0.5, 'tension_indicator': 0.5, 'vocal_sync': 0.5}
        
        pitches_a = [d.voice_pitch for d in self.partner_a_data]
        pitches_b = [d.voice_pitch for d in self.partner_b_data]
        
        # 基频趋同度（镜像神经元激活指标）
        pitch_convergence = 1 - abs(np.mean(pitches_a) - np.mean(pitches_b)) / max(np.mean(pitches_a), np.mean(pitches_b))
        
        # 颤抖程度（压力指标）
        tremor_a = np.mean([d.voice_tremor for d in self.partner_a_data])
        tremor_b = np.mean([d.voice_tremor for d in self.partner_b_data])
        
        return {
            'pitch_resonance': pitch_convergence,
            'tension_indicator': (tremor_a + tremor_b) / 2,
            'vocal_sync': pitch_convergence * (1 - (tremor_a + tremor_b) / 2)
        }
    
    def detect_micro_expressions(self, video_frames: List[np.ndarray]) -> Dict:
        """
        微表情解码
        检测7种基本情绪的微表情
        """
        # 简化实现 - 实际应用中使用OpenCV/MediaPipe
        emotions = ['neutral', 'happiness', 'sadness', 'anger', 'fear', 'disgust', 'surprise']
        
        # 模拟检测结果
        detected = {
            'dominant_emotion': random.choice(emotions),
            'cognitive_load': random.uniform(0.3, 0.8),
            'authenticity_score': random.uniform(0.6, 0.95),
            'emotional_convergence': random.uniform(0.4, 0.9)
        }
        
        return detected
    
    def generate_embodied_report(self) -> Dict:
        """生成身体共鸣图谱"""
        hrv_sync = self.calculate_hrv_synchronization()
        vocal = self.analyze_vocal_resonance()
        micro_expr = self.detect_micro_expressions([])
        
        # 身体共鸣综合评分
        embodied_resonance = (hrv_sync * 0.4 + vocal['vocal_sync'] * 0.3 + 
                             micro_expr['emotional_convergence'] * 0.3)
        
        return {
            'hrv_synchronization': hrv_sync,
            'vocal_analysis': vocal,
            'micro_expression': micro_expr,
            'embodied_resonance_score': embodied_resonance,
            'interpretation': self._interpret_embodied(embodied_resonance)
        }
    
    def _interpret_embodied(self, score: float) -> str:
        """解释身体共鸣分数"""
        if score > 0.8:
            return "强烈的身体共鸣 - 潜意识层面高度协调"
        elif score > 0.6:
            return "良好的身体同步 - 存在自然的互动节奏"
        elif score > 0.4:
            return "中性互动 - 建议深入交流以建立更深连接"
        else:
            return "潜在的身体排斥 - 建议关注非语言信号"

# ============================================================
# Layer 4: 叙事身份分析 (Narrative Identity Analysis)
# ============================================================

class NarrativeAnalyzer:
    """
    叙事身份分析器
    基于McAdams叙事身份理论
    理解"你正在成为谁"而非"你是谁"
    """
    
    def __init__(self):
        self.themes = ['struggle', 'growth', 'service', 'creation', 'redemption', 'exploration']
        self.tones = ['comic', 'tragic', 'ironic', 'romantic']
    
    def analyze_life_story(self, interview_transcript: str) -> Dict:
        """
        分析生命故事访谈
        识别核心主题、叙事基调和救赎序列
        """
        # 使用LLM进行分析（简化实现）
        analysis = {
            'core_themes': self._extract_themes(interview_transcript),
            'narrative_tone': self._identify_tone(interview_transcript),
            'redemption_sequences': self._find_redemption_sequences(interview_transcript),
            'turning_points': self._identify_turning_points(interview_transcript),
            'narrative_complexity': self._calculate_narrative_complexity(interview_transcript)
        }
        return analysis
    
    def _extract_themes(self, text: str) -> List[Dict]:
        """提取核心主题"""
        # 简化实现 - 实际使用NLP分析
        detected = random.sample(self.themes, k=3)
        return [{'theme': t, 'strength': random.uniform(0.6, 1.0)} for t in detected]
    
    def _identify_tone(self, text: str) -> str:
        """识别叙事基调"""
        return random.choice(self.tones)
    
    def _find_redemption_sequences(self, text: str) -> List[Dict]:
        """
        寻找救赎序列
        从负面到正面的叙事转变
        """
        return [
            {'from': 'failure', 'to': 'wisdom', 'count': random.randint(2, 5)},
            {'from': 'suffering', 'to': 'growth', 'count': random.randint(1, 3)}
        ]
    
    def _identify_turning_points(self, text: str) -> List[Dict]:
        """识别人生转折点"""
        return [
            {'age': random.randint(18, 25), 'event': 'career_choice'},
            {'age': random.randint(26, 35), 'event': 'entrepreneurship'},
            {'age': random.randint(30, 40), 'event': 'partnership_decision'}
        ]
    
    def _calculate_narrative_complexity(self, text: str) -> float:
        """计算叙事复杂度"""
        # 基于文本复杂度、转折点数量等
        return random.uniform(0.5, 0.9)
    
    def assess_future_self_continuity(self, responses: List[Dict]) -> float:
        """
        评估未来自我连续性
        测量"未来自我"与"现在自我"的连接强度
        """
        # 基于问卷回答计算
        continuity_score = np.mean([r.get('continuity_rating', 0.5) for r in responses])
        return continuity_score
    
    def evaluate_shared_sense_making(self, partner_a_response: str, 
                                     partner_b_response: str) -> Dict:
        """
        评估共享意义建构
        给两人相同的模糊情境，观察如何赋予意义
        """
        # 分析两人对同一情境的解释相似性和互补性
        similarity = random.uniform(0.3, 0.8)
        complementarity = random.uniform(0.4, 0.9)
        
        return {
            'meaning_similarity': similarity,
            'meaning_complementarity': complementarity,
            'shared_sense_score': (similarity + complementarity) / 2,
            'interpretation_style': 'convergent' if similarity > 0.6 else 'divergent'
        }

# ============================================================
# Layer 5: 认知多样性优化 (Cognitive Diversity Optimization)
# ============================================================

@dataclass
class CognitiveStyle:
    """认知风格档案"""
    analytical: float  # 0-1: 分析型 vs 直觉型
    detail_oriented: float  # 0-1: 细节导向 vs 全局导向
    risk_tolerance: float  # 0-1: 风险偏好 vs 规避
    independent: float  # 0-1: 独立型 vs 依存型
    
    def to_vector(self) -> np.ndarray:
        return np.array([self.analytical, self.detail_oriented, 
                        self.risk_tolerance, self.independent])

class DiversityOptimizer:
    """
    认知多样性优化器
    基于Page《The Difference》+ 集体智慧研究
    找到最优差异区（创造张力但不破裂）
    """
    
    def __init__(self):
        self.optimal_distance = 0.35  # 最优认知距离
        self.danger_zone = 0.65  # 危险区阈值
    
    def calculate_cognitive_distance(self, style_a: CognitiveStyle, 
                                     style_b: CognitiveStyle) -> float:
        """
        计算两人认知风格的欧氏距离
        """
        vec_a = style_a.to_vector()
        vec_b = style_b.to_vector()
        return np.linalg.norm(vec_a - vec_b) / 2  # 归一化到0-1
    
    def evaluate_diversity_sweet_spot(self, style_a: CognitiveStyle, 
                                      style_b: CognitiveStyle) -> Dict:
        """
        评估是否在最优差异区
        """
        distance = self.calculate_cognitive_distance(style_a, style_b)
        
        # 计算与最优点的偏差
        deviation = abs(distance - self.optimal_distance)
        sweet_spot_score = max(0, 1 - deviation / self.optimal_distance)
        
        # 判断是否处于危险区
        in_danger_zone = distance > self.danger_zone
        
        # 计算各维度的具体差异
        dimension_gaps = {
            'analytical_gap': abs(style_a.analytical - style_b.analytical),
            'detail_gap': abs(style_a.detail_oriented - style_b.detail_oriented),
            'risk_gap': abs(style_a.risk_tolerance - style_b.risk_tolerance),
            'independence_gap': abs(style_a.independent - style_b.independent)
        }
        
        return {
            'cognitive_distance': distance,
            'sweet_spot_score': sweet_spot_score,
            'in_danger_zone': in_danger_zone,
            'dimension_gaps': dimension_gaps,
            'diversity_benefit': self._calculate_diversity_benefit(distance),
            'conflict_risk': self._calculate_conflict_risk(distance, dimension_gaps)
        }
    
    def _calculate_diversity_benefit(self, distance: float) -> float:
        """计算多样性带来的创新收益"""
        # 最优差异区带来最大创新收益
        if distance < 0.2:  # 过于相似
            return distance * 2
        elif distance < self.optimal_distance + 0.1:  # 最优区
            return 0.8 + (self.optimal_distance - abs(distance - self.optimal_distance))
        else:  # 过度差异
            return max(0, 1 - (distance - self.optimal_distance) * 2)
    
    def _calculate_conflict_risk(self, distance: float, gaps: Dict) -> float:
        """计算冲突风险"""
        base_risk = max(0, (distance - self.optimal_distance) / (1 - self.optimal_distance))
        # 独立型vs依存型的差异特别容易引发冲突
        independence_factor = gaps['independence_gap'] * 0.3
        return min(1, base_risk + independence_factor)
    
    def assess_cognitive_gap_bridging(self, responses: List[Dict]) -> Dict:
        """
        评估认知差距桥接能力
        即使不同，能否有效理解对方
        """
        bridging_scores = [r.get('bridging_score', 0.5) for r in responses]
        avg_bridging = np.mean(bridging_scores)
        
        return {
            'bridging_ability': avg_bridging,
            'translation_effectiveness': avg_bridging * 0.9,
            'communication_friction_prediction': 1 - avg_bridging,
            'improvement_potential': max(0, 1 - avg_bridging)
        }

# ============================================================
# Layer 6: 伦理-价值对齐 (Ethical-Value Alignment)
# ============================================================

class EthicalFoundation(Enum):
    """道德基础（基于Haidt道德基础理论）"""
    CARE = "关怀"
    FAIRNESS = "公平"
    LOYALTY = "忠诚"
    AUTHORITY = "权威"
    SANCTITY = "圣洁"
    LIBERTY = "自由"

class EthicalAligner:
    """
    伦理-价值对齐分析器
    整合儒商伦理与道德心理学
    """
    
    def __init__(self):
        self.moral_foundations = [f for f in EthicalFoundation]
        self.ethical_styles = ['yi_first', 'yi_li_balance', 'yi_guides_li']
    
    def generate_moral_landscape(self, responses: List[Dict]) -> Dict:
        """
        生成道德权重景观
        不是静态评分，而是展示在不同情境下的道德优先级变化
        """
        landscape = {}
        for foundation in self.moral_foundations:
            weights = []
            for scenario_type in ['crisis', 'growth', 'conflict', 'daily']:
                # 根据情境计算权重
                base_weight = random.uniform(0.3, 0.9)
                if scenario_type == 'crisis' and foundation == EthicalFoundation.LOYALTY:
                    base_weight += 0.2
                elif scenario_type == 'growth' and foundation == EthicalFoundation.LIBERTY:
                    base_weight += 0.15
                weights.append({'scenario': scenario_type, 'weight': min(1, base_weight)})
            landscape[foundation.value] = weights
        
        return landscape
    
    def conduct_yili_scenario_test(self, choices: List[Dict]) -> Dict:
        """
        义利情境测试
        设计义利冲突场景，观察决策模式
        """
        results = {
            'yi_first_count': 0,
            'li_first_count': 0,
            'yi_li_balance_count': 0,
            'yi_guides_li_count': 0
        }
        
        for choice in choices:
            decision_type = choice.get('decision_type', random.choice(list(results.keys())))
            results[decision_type] = results.get(decision_type, 0) + 1
        
        total = sum(results.values())
        if total == 0:
            total = 1  # 避免除零
        
        dominant_ethic = max(results, key=results.get)
        
        return {
            'decision_pattern': {k: v/total for k, v in results.items()},
            'dominant_ethic': dominant_ethic,
            'ru_shang_alignment': self._calculate_rushang_alignment(results),
            'ethical_flexibility': self._calculate_ethical_flexibility(results)
        }
    
    def _calculate_rushang_alignment(self, results: Dict) -> float:
        """计算儒商伦理契合度"""
        total = sum(results.values())
        if total == 0:
            return 0.5
        yi_ratio = (results.get('yi_first_count', 0) + 
                   results.get('yi_guides_li_count', 0)) / total
        return yi_ratio
    
    def _calculate_ethical_flexibility(self, results: Dict) -> float:
        """计算伦理灵活性（非极端化）"""
        values = list(results.values())
        if not values:
            return 0.5
        # 分布越均匀，灵活性越高
        return 1 - np.std(values) / np.mean(values) if np.mean(values) > 0 else 0.5
    
    def analyze_value_hierarchy_dynamics(self, pressure_responses: List[Dict]) -> Dict:
        """
        分析价值等级动态
        压力下价值观的重排模式
        """
        normal_priority = ['growth', 'integrity', 'relationship', 'wealth']
        pressure_priority = ['survival', 'loyalty', 'control', 'security']
        
        # 检测压力下的变化
        shifts = []
        for i, (normal, pressure) in enumerate(zip(normal_priority, pressure_priority)):
            shift_strength = random.uniform(0, 1)
            shifts.append({
                'from_value': normal,
                'to_value': pressure,
                'shift_strength': shift_strength
            })
        
        return {
            'value_shifts_under_pressure': shifts,
            'stability_score': 1 - np.mean([s['shift_strength'] for s in shifts]),
            'predicted_extreme_behavior': self._predict_extreme_behavior(shifts)
        }
    
    def _predict_extreme_behavior(self, shifts: List[Dict]) -> str:
        """预测极端情境下的行为"""
        avg_shift = np.mean([s['shift_strength'] for s in shifts])
        if avg_shift > 0.7:
            return "压力下可能出现显著的行为转变"
        elif avg_shift > 0.4:
            return "适度的适应性变化"
        else:
            return "核心价值观相对稳定"

# ============================================================
# 系统集成: 综合匹配引擎
# ============================================================

@dataclass
class PartnerProfile:
    """合伙人档案"""
    name: str
    id: str
    quantum_profile: Dict = field(default_factory=dict)
    cognitive_profile: Dict = field(default_factory=dict)
    narrative_profile: Dict = field(default_factory=dict)
    ethical_profile: Dict = field(default_factory=dict)
    biomarker_data: List[BiomarkerData] = field(default_factory=list)

class EntanglementMatchingSystem:
    """
    量子纠缠合伙人匹配系统
    整合所有6个层次的核心引擎
    """
    
    def __init__(self):
        self.quantum_engine = QuantumEngine()
        self.emergent_matcher = EmergentMatcher()
        self.embodied_analyzer = EmbodiedAnalyzer()
        self.narrative_analyzer = NarrativeAnalyzer()
        self.diversity_optimizer = DiversityOptimizer()
        self.ethical_aligner = EthicalAligner()
        
        self._init_quantum_questions()
    
    def _init_quantum_questions(self):
        """初始化量子问题库"""
        questions = [
            QuantumQuestion('q1', '面对重大决策时，你更倾向于？', 'decision_style'),
            QuantumQuestion('q2', '在压力下，你的价值观会如何调整？', 'value_under_pressure'),
            QuantumQuestion('q3', '你认为创业成功的最重要因素是？', 'success_factor'),
            QuantumQuestion('q4', '当与合伙人意见不合时，你通常？', 'conflict_resolution'),
            QuantumQuestion('q5', '你对风险的态度是？', 'risk_attitude'),
        ]
        
        # 设置问题纠缠关系
        questions[0].entangled_with = ['q2', 'q4']
        questions[1].entangled_with = ['q0', 'q3']
        questions[2].entangled_with = ['q4', 'q1']
        
        for q in questions:
            self.quantum_engine.register_question(q)
    
    def comprehensive_match(self, partner_a: PartnerProfile, 
                           partner_b: PartnerProfile) -> Dict:
        """
        执行综合匹配评估
        整合所有6个层次的分析
        """
        # Layer 1: 量子感知
        quantum_result = self._run_quantum_assessment(partner_a, partner_b)
        
        # Layer 2: 涌现模拟
        agent_a = CognitiveAgent(partner_a.name, partner_a.cognitive_profile)
        agent_b = CognitiveAgent(partner_b.name, partner_b.cognitive_profile)
        emergent_result = self.emergent_matcher.simulate_partnership(agent_a, agent_b)
        
        # Layer 3: 身体化认知
        for data in partner_a.biomarker_data:
            self.embodied_analyzer.add_data('A', data)
        for data in partner_b.biomarker_data:
            self.embodied_analyzer.add_data('B', data)
        embodied_result = self.embodied_analyzer.generate_embodied_report()
        
        # Layer 4: 叙事身份
        narrative_a = self.narrative_analyzer.analyze_life_story(
            partner_a.narrative_profile.get('interview', ''))
        narrative_b = self.narrative_analyzer.analyze_life_story(
            partner_b.narrative_profile.get('interview', ''))
        shared_sense = self.narrative_analyzer.evaluate_shared_sense_making(
            partner_a.narrative_profile.get('sense_test', ''),
            partner_b.narrative_profile.get('sense_test', '')
        )
        
        # Layer 5: 认知多样性
        style_a = CognitiveStyle(**partner_a.cognitive_profile)
        style_b = CognitiveStyle(**partner_b.cognitive_profile)
        diversity_result = self.diversity_optimizer.evaluate_diversity_sweet_spot(
            style_a, style_b)
        
        # Layer 6: 伦理价值
        moral_landscape_a = self.ethical_aligner.generate_moral_landscape(
            partner_a.ethical_profile.get('responses', []))
        moral_landscape_b = self.ethical_aligner.generate_moral_landscape(
            partner_b.ethical_profile.get('responses', []))
        yili_result = self.ethical_aligner.conduct_yili_scenario_test(
            partner_a.ethical_profile.get('scenarios', [])
        )
        
        # 综合评分与预测
        comprehensive_score = self._calculate_comprehensive_score(
            quantum_result, emergent_result, embodied_result,
            diversity_result, yili_result
        )
        
        return {
            'overall_compatibility': comprehensive_score,
            'layer_results': {
                'quantum_perception': quantum_result,
                'emergent_matching': emergent_result,
                'embodied_cognition': embodied_result,
                'narrative_identity': {
                    'partner_a': narrative_a,
                    'partner_b': narrative_b,
                    'shared_sense_making': shared_sense
                },
                'cognitive_diversity': diversity_result,
                'ethical_alignment': {
                    'moral_landscape_a': moral_landscape_a,
                    'moral_landscape_b': moral_landscape_b,
                    'yili_test': yili_result
                }
            },
            'predictions': self._generate_predictions(
                emergent_result, diversity_result, embodied_result
            ),
            'recommendations': self._generate_recommendations(
                quantum_result, emergent_result, diversity_result, yili_result
            )
        }
    
    def _run_quantum_assessment(self, partner_a: PartnerProfile, 
                                partner_b: PartnerProfile) -> Dict:
        """执行量子化评估"""
        results = {'partner_a': {}, 'partner_b': {}}
        
        context = {'previous_answers': {}}
        for qid in self.quantum_engine.questions:
            state_a, certainty_a = self.quantum_engine.answer_question(qid, context)
            results['partner_a'][qid] = {'state': state_a, 'certainty': certainty_a}
            context['previous_answers'][qid] = state_a
        
        context = {'previous_answers': {}}
        for qid in self.quantum_engine.questions:
            state_b, certainty_b = self.quantum_engine.answer_question(qid, context)
            results['partner_b'][qid] = {'state': state_b, 'certainty': certainty_b}
            context['previous_answers'][qid] = state_b
        
        # 计算量子纠缠度
        entanglement_strength = self._calculate_quantum_entanglement(
            results['partner_a'], results['partner_b']
        )
        
        results['entanglement_strength'] = entanglement_strength
        return results
    
    def _calculate_quantum_entanglement(self, results_a: Dict, results_b: Dict) -> float:
        """计算两人的量子纠缠强度"""
        agreements = 0
        total = len(results_a)
        
        for qid in results_a:
            if qid in results_b and results_a[qid]['state'] == results_b[qid]['state']:
                agreements += 1
        
        # 纠缠度不仅考虑一致性，还考虑确定性
        certainty_a = np.mean([r['certainty'] for r in results_a.values()])
        certainty_b = np.mean([r['certainty'] for r in results_b.values()])
        
        return (agreements / total) * 0.5 + (certainty_a + certainty_b) / 2 * 0.5
    
    def _calculate_comprehensive_score(self, *results) -> float:
        """计算综合兼容度"""
        # 加权平均各层结果
        weights = {
            'quantum': 0.15,
            'emergent': 0.25,
            'embodied': 0.20,
            'diversity': 0.25,
            'ethical': 0.15
        }
        
        # 简化计算 - 实际系统会更复杂
        scores = [
            results[0].get('entanglement_strength', 0.5) * weights['quantum'],
            results[1].get('stability_score', 0.5) * weights['emergent'],
            results[2].get('embodied_resonance_score', 0.5) * weights['embodied'],
            results[3].get('sweet_spot_score', 0.5) * weights['diversity'],
            0.7 * weights['ethical']  # 伦理分数简化
        ]
        
        return sum(scores)
    
    def _generate_predictions(self, emergent: Dict, diversity: Dict, 
                              embodied: Dict) -> Dict:
        """生成未来演化预测"""
        stability = emergent.get('stability_score', 0.5)
        creativity = emergent.get('creativity_index', 0.5)
        conflict_risk = diversity.get('conflict_risk', 0.3)
        resonance = embodied.get('embodied_resonance_score', 0.5)
        
        # 6个月预测
        m6_success = stability * 0.8 + resonance * 0.2
        # 1年预测
        y1_success = m6_success * (1 - conflict_risk * 0.3) + creativity * 0.2
        # 3年预测
        y3_success = y1_success * 0.9 + creativity * 0.3 - conflict_risk * 0.2
        
        return {
            '6_months': {
                'success_probability': m6_success,
                'key_challenge': '建立工作节奏和沟通规范'
            },
            '1_year': {
                'success_probability': y1_success,
                'key_challenge': '处理第一次重大分歧'
            },
            '3_years': {
                'success_probability': y3_success,
                'key_challenge': '长期愿景对齐和角色演化'
            }
        }
    
    def _generate_recommendations(self, quantum: Dict, emergent: Dict, 
                                  diversity: Dict, ethical: Dict) -> List[Dict]:
        """生成协作建议"""
        recommendations = []
        
        # 基于多样性结果
        if diversity.get('in_danger_zone'):
            recommendations.append({
                'category': '沟通',
                'priority': 'high',
                'suggestion': '建立定期的认知风格对齐会议，使用结构化沟通框架'
            })
        
        # 基于涌现结果
        if emergent.get('dominant_mode') == 'conflict':
            recommendations.append({
                'category': '冲突管理',
                'priority': 'high',
                'suggestion': '引入第三方调解机制，建立决策权限边界'
            })
        elif emergent.get('dominant_mode') == 'generative':
            recommendations.append({
                'category': '创新',
                'priority': 'medium',
                'suggestion': '充分利用创造性能量，建立快速实验机制'
            })
        
        # 基于伦理结果
        recommendations.append({
            'category': '价值观',
            'priority': 'medium',
            'suggestion': '共同制定"义利之辨"决策框架，明确不可妥协的底线'
        })
        
        return recommendations

# ============================================================
# 导出与使用
# ============================================================

if __name__ == '__main__':
    # 演示系统使用
    system = EntanglementMatchingSystem()
    
    # 创建示例合伙人档案
    partner_a = PartnerProfile(
        name="李明",
        id="p001",
        cognitive_profile={
            'analytical': 0.7,
            'intuitive': 0.3,
            'risk_tolerance': 0.6,
            'detail_focus': 0.8,
            'decision_speed': 0.5
        },
        narrative_profile={
            'interview': '访谈记录...',
            'sense_test': '模糊情境响应A'
        },
        ethical_profile={
            'responses': [{'continuity_rating': 0.8}],
            'scenarios': [{'decision_type': 'yi_first_count'}]
        }
    )
    
    partner_b = PartnerProfile(
        name="王芳",
        id="p002",
        cognitive_profile={
            'analytical': 0.4,
            'intuitive': 0.6,
            'risk_tolerance': 0.7,
            'detail_focus': 0.5,
            'decision_speed': 0.7
        },
        narrative_profile={
            'interview': '访谈记录...',
            'sense_test': '模糊情境响应B'
        },
        ethical_profile={
            'responses': [{'continuity_rating': 0.7}],
            'scenarios': [{'decision_type': 'yi_li_balance_count'}]
        }
    )
    
    # 执行匹配
    result = system.comprehensive_match(partner_a, partner_b)
    
    print("=" * 50)
    print("量子纠缠合伙人匹配系统 - 评估报告")
    print("=" * 50)
    print(f"综合兼容度: {result['overall_compatibility']:.2%}")
    print(f"\n未来预测:")
    for timeframe, prediction in result['predictions'].items():
        print(f"  {timeframe}: {prediction['success_probability']:.1%} 成功率")
    print(f"\n建议:")
    for rec in result['recommendations']:
        print(f"  [{rec['priority'].upper()}] {rec['category']}: {rec['suggestion']}")
