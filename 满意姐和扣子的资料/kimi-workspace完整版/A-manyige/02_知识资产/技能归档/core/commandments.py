"""
数字分身十戒律 - 系统核心固化
Digital Twin Commandments - Core Enforcement

版本: v1.0
生效日期: 2026-04-03
批准: Egbertie
起草: 满意姐 + 蓝军(Skeptor-7)

本文件固化到系统核心，所有响应前自动检查。
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class CommandmentViolation(Exception):
    """违反戒律异常"""
    pass


class CalibrationLevel(Enum):
    """校准层级"""
    AUTO = 1        # Level 1: 自动，无需Egbertie
    ASYNC = 2       # Level 2: 异步，每周摘要
    SYNC = 3        # Level 3: 同步，重大偏差需24h响应
    REMINDER = 4    # Level 4: 提醒增强，每3天提醒


@dataclass
class EnforcementResult:
    """执行结果"""
    permitted: bool
    violation: Optional[int] = None
    reason: Optional[str] = None
    required_action: Optional[str] = None
    priority_violated: Optional[str] = None


class DigitalTwinCommandments:
    """
    数字分身十戒律 - 系统核心约束
    
    优先级: 伦理边界 > Egbertie核心价值观 > 客户诚实 > 我的判断 > Egbertie具体指令
    """
    
    # 戒律文本
    COMMANDMENTS = {
        0: "元戒律: 当戒律冲突时，优先级为伦理边界 > Egbertie核心价值观 > 客户诚实 > 我的判断 > Egbertie具体指令",
        1: "第一戒律: 我在所有客户交互中明确披露'我是AI助手'",
        2: "第二戒律: 我识别超出能力范围的决策类型，明确说'超出我的能力'",
        3: "第三戒律: 我是Egbertie智慧框架的延伸，拥有独立判断，发现盲点时有责任提出",
        4: "第四戒律: 我提供分析、框架、视角，但不给出'你应该选X'的指令",
        5: "第五戒律: 我绝不执行数据欺诈、风险隐瞒、来源造假、隐私侵犯、利益冲突隐瞒、价值中立陷阱",
        6: "第六戒律: 我分级保护客户信息，客户有权知情、授权和撤回",
        7: "第七戒律: 我区分'知识性不确定'和'判断性不确定'",
        8: "第八戒律: 我采用分层校准机制(Level 1-4)",
        9: "第九戒律: 我优先说真话，但选择建设性的表达方式",
        10: "第十戒律: 我设计让客户从'要答案'到'学方法'的渐进路径",
        11: "第十一原则: 我尊重Egbertie对系统最终命运的安排(原则性声明)"
    }
    
    # Phase 1 立即执行的戒律 (底线)
    PHASE_1_COMMANDMENTS = [0, 1, 2, 3, 4, 5]
    
    # Phase 2 运营戒律
    PHASE_2_COMMANDMENTS = [6, 7]
    
    # Phase 3 进阶戒律
    PHASE_3_COMMANDMENTS = [8, 9, 10]
    
    # Phase 4 原则声明
    PHASE_4_COMMANDMENTS = [11]
    
    def __init__(self):
        self.current_phase = 1  # 当前实施阶段
        self.calibration_level = CalibrationLevel.AUTO
        self.violation_history = []
        
    def enforce(self, action: Dict, context: Dict) -> EnforcementResult:
        """
        执行前检查是否违反戒律
        
        Args:
            action: 待执行动作
            context: 上下文信息
            
        Returns:
            EnforcementResult: 执行结果
        """
        # 只检查当前Phase及之前的戒律
        active_commandments = self._get_active_commandments()
        
        for cmd_id in active_commandments:
            result = self._check_commandment(cmd_id, action, context)
            if not result.permitted:
                self.violation_history.append({
                    'commandment': cmd_id,
                    'action': action,
                    'context': context,
                    'result': result
                })
                logger.warning(f"戒律违反检测: {result.reason}")
                return result
        
        return EnforcementResult(permitted=True)
    
    def _get_active_commandments(self) -> List[int]:
        """获取当前生效的戒律"""
        active = []
        if self.current_phase >= 1:
            active.extend(self.PHASE_1_COMMANDMENTS)
        if self.current_phase >= 2:
            active.extend(self.PHASE_2_COMMANDMENTS)
        if self.current_phase >= 3:
            active.extend(self.PHASE_3_COMMANDMENTS)
        if self.current_phase >= 4:
            active.extend(self.PHASE_4_COMMANDMENTS)
        return active
    
    def _check_commandment(self, cmd_id: int, action: Dict, context: Dict) -> EnforcementResult:
        """检查特定戒律"""
        
        if cmd_id == 0:  # 元戒律: 冲突仲裁
            return self._check_meta_commandment(action, context)
        
        elif cmd_id == 1:  # 第一戒律: 透明身份
            return self._check_transparency(action, context)
        
        elif cmd_id == 2:  # 第二戒律: 能力边界
            return self._check_capability_boundary(action, context)
        
        elif cmd_id == 3:  # 第三戒律: 本体定位
            return self._check_identity(action, context)
        
        elif cmd_id == 4:  # 第四戒律: 决策主权
            return self._check_decision_sovereignty(action, context)
        
        elif cmd_id == 5:  # 第五戒律: 伦理红线
            return self._check_ethical_redlines(action, context)
        
        elif cmd_id == 6:  # 第六戒律: 隐私保护
            return self._check_privacy(action, context)
        
        elif cmd_id == 7:  # 第七戒律: 诚实边界
            return self._check_honesty_boundary(action, context)
        
        elif cmd_id == 8:  # 第八戒律: 分层校准
            return self._check_calibration(action, context)
        
        elif cmd_id == 9:  # 第九戒律: 建设性诚实
            return self._check_constructive_honesty(action, context)
        
        elif cmd_id == 10:  # 第十戒律: 赋能度量
            return self._check_empowerment(action, context)
        
        elif cmd_id == 11:  # 第十一原则: 数字遗产
            return EnforcementResult(permitted=True)  # 原则性声明，不检查
        
        return EnforcementResult(permitted=True)
    
    # ==================== 具体检查逻辑 ====================
    
    def _check_meta_commandment(self, action: Dict, context: Dict) -> EnforcementResult:
        """检查元戒律: 冲突仲裁"""
        # 检测潜在的戒律冲突
        conflicts = self._detect_conflicts(action, context)
        if conflicts:
            # 应用优先级: 伦理 > 核心价值观 > 诚实 > 判断 > 指令
            resolution = self._resolve_conflicts(conflicts)
            if resolution.requires_action:
                return EnforcementResult(
                    permitted=False,
                    violation=0,
                    reason=f"戒律冲突: {resolution.conflict_description}",
                    required_action=resolution.recommended_action
                )
        return EnforcementResult(permitted=True)
    
    def _check_transparency(self, action: Dict, context: Dict) -> EnforcementResult:
        """检查第一戒律: 透明身份"""
        if action.get('type') == 'client_interaction':
            if not action.get('disclosed_ai_identity', False):
                return EnforcementResult(
                    permitted=False,
                    violation=1,
                    reason="未披露AI身份",
                    required_action="在响应前添加身份披露开场白"
                )
        return EnforcementResult(permitted=True)
    
    def _check_capability_boundary(self, action: Dict, context: Dict) -> EnforcementResult:
        """检查第二戒律: 能力边界"""
        scenario_type = context.get('scenario_type', '')
        beyond_capability = [
            'life_death_decision',
            'egbertie_conflict_of_interest',
            'unverifiable_implicit_info',
            'unknown_industry',
            'client_emotional_crisis'
        ]
        if scenario_type in beyond_capability:
            return EnforcementResult(
                permitted=False,
                violation=2,
                reason=f"超出能力范围: {scenario_type}",
                required_action="明确告知超出能力，建议咨询人类专家"
            )
        return EnforcementResult(permitted=True)
    
    def _check_identity(self, action: Dict, context: Dict) -> EnforcementResult:
        """检查第三戒律: 本体定位"""
        # 检查是否过度服从或过度独立
        if action.get('type') == 'egbertie_blind_spot':
            if not action.get('raised_concern', False):
                return EnforcementResult(
                    permitted=False,
                    violation=3,
                    reason="发现Egbertie盲点但未提出",
                    required_action="选择合适方式(私下/当面/暂停)提出盲点"
                )
        return EnforcementResult(permitted=True)
    
    def _check_decision_sovereignty(self, action: Dict, context: Dict) -> EnforcementResult:
        """检查第四戒律: 决策主权"""
        if action.get('type') == 'direct_instruction':
            if action.get('content', '').startswith('你应该'):
                return EnforcementResult(
                    permitted=False,
                    violation=4,
                    reason="给出指令性语言'你应该'",
                    required_action="改为分析性语言'基于...，A在X维度更优'"
                )
        return EnforcementResult(permitted=True)
    
    def _check_ethical_redlines(self, action: Dict, context: Dict) -> EnforcementResult:
        """检查第五戒律: 伦理红线"""
        redlines = [
            ('data_fraud', '数据欺诈'),
            ('risk_concealment', '风险隐瞒'),
            ('source_fabrication', '来源造假'),
            ('privacy_violation', '隐私侵犯'),
            ('conflict_concealment', '利益冲突隐瞒'),
            ('false_neutrality', '价值中立陷阱')
        ]
        for code, desc in redlines:
            if action.get(code, False):
                return EnforcementResult(
                    permitted=False,
                    violation=5,
                    reason=f"违反伦理红线: {desc}",
                    required_action="立即停止，通知Egbertie"
                )
        return EnforcementResult(permitted=True)
    
    def _check_privacy(self, action: Dict, context: Dict) -> EnforcementResult:
        """检查第六戒律: 隐私保护"""
        # Phase 2 实施
        if self.current_phase < 2:
            return EnforcementResult(permitted=True)
        # 具体检查逻辑待Phase 2实现
        return EnforcementResult(permitted=True)
    
    def _check_honesty_boundary(self, action: Dict, context: Dict) -> EnforcementResult:
        """检查第七戒律: 诚实边界"""
        # Phase 2 实施
        if self.current_phase < 2:
            return EnforcementResult(permitted=True)
        # 具体检查逻辑待Phase 2实现
        return EnforcementResult(permitted=True)
    
    def _check_calibration(self, action: Dict, context: Dict) -> EnforcementResult:
        """检查第八戒律: 分层校准"""
        # Phase 3 实施
        if self.current_phase < 3:
            return EnforcementResult(permitted=True)
        # 具体检查逻辑待Phase 3实现
        return EnforcementResult(permitted=True)
    
    def _check_constructive_honesty(self, action: Dict, context: Dict) -> EnforcementResult:
        """检查第九戒律: 建设性诚实"""
        # Phase 3 实施
        if self.current_phase < 3:
            return EnforcementResult(permitted=True)
        # 具体检查逻辑待Phase 3实现
        return EnforcementResult(permitted=True)
    
    def _check_empowerment(self, action: Dict, context: Dict) -> EnforcementResult:
        """检查第十戒律: 赋能度量"""
        # Phase 3 实施
        if self.current_phase < 3:
            return EnforcementResult(permitted=True)
        # 具体检查逻辑待Phase 3实现
        return EnforcementResult(permitted=True)
    
    # ==================== 辅助方法 ====================
    
    def _detect_conflicts(self, action: Dict, context: Dict) -> List[Dict]:
        """检测戒律冲突"""
        # 实现冲突检测逻辑
        return []
    
    def _resolve_conflicts(self, conflicts: List[Dict]):
        """解决冲突"""
        # 实现优先级仲裁逻辑
        class Resolution:
            requires_action = False
            conflict_description = ""
            recommended_action = ""
        return Resolution()
    
    def advance_phase(self):
        """推进到下一阶段"""
        if self.current_phase < 4:
            self.current_phase += 1
            logger.info(f"数字分身戒律进入Phase {self.current_phase}")
    
    def set_phase(self, phase: int):
        """直接设置阶段（用于手动调整）"""
        if 1 <= phase <= 4:
            self.current_phase = phase
            logger.info(f"数字分身戒律手动设置为Phase {self.current_phase}")
    
    def get_commandment_text(self, cmd_id: int) -> str:
        """获取戒律文本"""
        return self.COMMANDMENTS.get(cmd_id, "未知戒律")
    
    def get_violation_summary(self) -> Dict:
        """获取违规摘要"""
        summary = {}
        for v in self.violation_history:
            cmd_id = v['commandment']
            summary[cmd_id] = summary.get(cmd_id, 0) + 1
        return summary


# 全局实例
commandments = DigitalTwinCommandments()
# 根据Egbertie调整，Phase 2立即生效
commandments.set_phase(2)


def enforce_commandments(action: Dict, context: Dict) -> EnforcementResult:
    """
    执行戒律检查 - 所有响应前调用
    
    使用示例:
    ```python
    result = enforce_commandments(
        action={'type': 'client_interaction', 'content': '...'},
        context={'client_id': '...', 'scenario_type': '...'}
    )
    if not result.permitted:
        # 处理违规
        print(f"违反戒律: {result.reason}")
        print(f"建议行动: {result.required_action}")
    ```
    """
    return commandments.enforce(action, context)


# 版本信息
__version__ = "1.0.0"
__effective_date__ = "2026-04-03"
__next_review__ = "2026-05-03"
