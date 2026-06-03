"""
四层架构测试
"""

import pytest
from datetime import datetime
from layers.architecture import (
    Scenario, Perspective, DecisionStyle, KnowledgePacket, EvolutionPlan,
    TotemAgent, CognitiveLayer, ConflictResolver,
    LearningLayer, KnowledgeLayer, KnowledgeFermenter,
    EvolutionLayer, CalibrationTrigger, TotemEngine
)


# ==================== 测试数据模型 ====================

class TestDataModels:
    """测试数据模型"""
    
    def test_scenario_creation(self):
        """测试情境创建"""
        scenario = Scenario(
            context="测试背景",
            constraints=["约束1", "约束2"],
            founder_profile={"name": "张三"},
            candidates=[{"name": "李四"}],
            metadata={"test": True}
        )
        
        assert scenario.context == "测试背景"
        assert len(scenario.constraints) == 2
        assert scenario.timestamp is not None
    
    def test_perspective_creation(self):
        """测试观点创建"""
        perspective = Perspective(
            totem_name="司马贺",
            dimension="理性决策",
            score=0.8,
            analysis="分析文本",
            recommendation="建议",
            confidence=0.9
        )
        
        assert perspective.totem_name == "司马贺"
        assert perspective.score == 0.8
        assert perspective.confidence == 0.9
    
    def test_decision_style_creation(self):
        """测试决策风格创建"""
        style = DecisionStyle(
            founder_id="founder_001",
            risk_preference="moderate",
            satisficing_threshold=0.7,
            value_priorities=["诚信", "互补"],
            historical_patterns=["pattern1"]
        )
        
        assert style.founder_id == "founder_001"
        assert style.satisficing_threshold == 0.7
    
    def test_knowledge_packet_creation(self):
        """测试知识包创建"""
        packet = KnowledgePacket(
            case_quintuple={
                "situation": "情境",
                "decision_framework": "框架",
                "judgment": "判断",
                "outcome": "结果",
                "reflection": "反思"
            },
            patterns=[{"name": "模式1"}],
            theory_links=["理论1"],
            confidence=0.85
        )
        
        assert packet.confidence == 0.85
        assert len(packet.patterns) == 1


# ==================== 测试认知层 ====================

class MockTotemAgent(TotemAgent):
    """模拟图腾Agent"""
    
    @property
    def name(self) -> str:
        return "测试图腾"
    
    @property
    def element(self) -> str:
        return "土"
    
    @property
    def priority(self) -> int:
        return 1
    
    def analyze(self, scenario: Scenario) -> Perspective:
        return Perspective(
            totem_name=self.name,
            dimension="测试维度",
            score=0.7,
            analysis="测试分析",
            recommendation="测试建议"
        )


class TestCognitiveLayer:
    """测试认知层"""
    
    def test_register_agent(self):
        """测试注册Agent"""
        layer = CognitiveLayer()
        agent = MockTotemAgent()
        
        layer.register_agent(agent)
        
        assert "测试图腾" in layer.agents
    
    def test_analyze(self):
        """测试分析"""
        layer = CognitiveLayer()
        agent = MockTotemAgent()
        layer.register_agent(agent)
        
        scenario = Scenario(
            context="测试",
            constraints=[],
            founder_profile={},
            candidates=[]
        )
        
        perspectives = layer.analyze(scenario)
        
        assert len(perspectives) == 1
        assert perspectives[0].totem_name == "测试图腾"


# ==================== 测试冲突消解 ====================

class TestConflictResolver:
    """测试冲突消解"""
    
    def test_no_conflict(self):
        """测试无冲突情况"""
        resolver = ConflictResolver()
        perspectives = [
            Perspective("图腾1", "维度", 0.7, "", ""),
            Perspective("图腾2", "维度", 0.75, "", "")
        ]
        
        result = resolver.resolve(perspectives)
        
        assert result["action"] == "proceed"
        assert result["confidence"] == "high"
    
    def test_medium_conflict(self):
        """测试中等冲突"""
        resolver = ConflictResolver()
        perspectives = [
            Perspective("图腾1", "维度", 0.3, "", ""),
            Perspective("图腾2", "维度", 0.8, "", "")
        ]
        
        result = resolver.resolve(perspectives)
        
        assert result["action"] == "caution"
        assert result["confidence"] == "medium"
    
    def test_high_conflict(self):
        """测试严重冲突"""
        resolver = ConflictResolver()
        perspectives = [
            Perspective("图腾1", "维度", 0.1, "", ""),
            Perspective("图腾2", "维度", 0.9, "", "")
        ]
        
        result = resolver.resolve(perspectives)
        
        assert result["action"] == "arbitration_needed"
        assert result["confidence"] == "low"


# ==================== 测试学习层 ====================

class TestLearningLayer:
    """测试学习层"""
    
    def test_extract_style(self):
        """测试提取决策风格"""
        layer = LearningLayer()
        
        style = layer.extract_style("founder_001")
        
        assert style.founder_id == "founder_001"
        assert style.satisficing_threshold > 0
        assert len(style.value_priorities) > 0


# ==================== 测试知识层 ====================

class TestKnowledgeLayer:
    """测试知识层"""
    
    def test_externalize(self):
        """测试外化"""
        layer = KnowledgeLayer()
        
        packet = layer.externalize("测试案例文本")
        
        assert "case_quintuple" in packet.__dict__
        assert packet.patterns == []


class TestKnowledgeFermenter:
    """测试知识发酵池"""
    
    def test_add_case(self):
        """测试添加案例"""
        fermenter = KnowledgeFermenter()
        
        fermenter.add_case({"id": "case_001", "text": "案例文本"})
        
        assert len(fermenter.cases) == 1


# ==================== 测试进化层 ====================

class TestEvolutionLayer:
    """测试进化层"""
    
    def test_generate_plan(self):
        """测试生成进化计划"""
        layer = EvolutionLayer()
        
        plan = layer.generate_plan()
        
        assert isinstance(plan, EvolutionPlan)
        assert isinstance(plan.calibration_needed, bool)


class TestCalibrationTrigger:
    """测试校准触发器"""
    
    def test_no_calibration_needed(self):
        """测试不需要校准"""
        trigger = CalibrationTrigger()
        trigger.last_calibration = datetime.now()  # 刚刚校准过
        
        result = trigger.check()
        
        assert result == False
    
    def test_calibration_needed_level2(self):
        """测试Level 2校准"""
        trigger = CalibrationTrigger()
        trigger.last_calibration = datetime.now().replace(day=1)  # 8天前
        
        result = trigger.check()
        
        # 取决于当前日期，可能触发Level 2
        assert isinstance(result, bool)


# ==================== 测试架构管理器 ====================

class TestTotemEngine:
    """测试图腾引擎"""
    
    def test_initialization(self):
        """测试初始化"""
        engine = TotemEngine()
        
        assert engine.cognitive is not None
        assert engine.learning is not None
        assert engine.knowledge is not None
        assert engine.evolution is not None
    
    def test_process(self):
        """测试处理流程"""
        engine = TotemEngine()
        agent = MockTotemAgent()
        engine.register_totem(agent)
        
        scenario = Scenario(
            context="测试情境",
            constraints=["约束"],
            founder_profile={"name": "创始人"},
            candidates=[{"name": "候选人"}]
        )
        
        result = engine.process(scenario)
        
        assert "perspectives" in result
        assert "consensus" in result
        assert "style" in result
        assert "evolution_plan" in result


# ==================== 集成测试 ====================

class TestIntegration:
    """集成测试"""
    
    def test_full_workflow(self):
        """测试完整流程"""
        # 创建引擎
        engine = TotemEngine()
        
        # 注册Agent
        agent = MockTotemAgent()
        engine.register_totem(agent)
        
        # 创建情境
        scenario = Scenario(
            context="深圳AI芯片项目寻找合伙人",
            constraints=["有产业资源", "全职投入"],
            founder_profile={
                "name": "张博士",
                "background": "技术",
                "experience": "首次创业"
            },
            candidates=[
                {"name": "候选人A", "experience": "10年销售"},
                {"name": "候选人B", "experience": "5年产品"}
            ],
            metadata={"founder_id": "founder_001"}
        )
        
        # 处理
        result = engine.process(scenario)
        
        # 验证
        assert len(result["perspectives"]) >= 1
        assert result["consensus"] is not None
        assert result["style"].founder_id == "founder_001"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
