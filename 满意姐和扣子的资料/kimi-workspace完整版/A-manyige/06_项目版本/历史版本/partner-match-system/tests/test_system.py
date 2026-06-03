"""
测试套件 - 确保系统的科学性和可靠性
"""

import unittest
import numpy as np
from core.entanglement_system import (
    WaveFunction, QuantumQuestion, QuantumEngine,
    CognitiveAgent, EmergentMatcher,
    EmbodiedAnalyzer, BiomarkerData,
    NarrativeAnalyzer,
    DiversityOptimizer, CognitiveStyle,
    EthicalAligner
)

class TestWaveFunction(unittest.TestCase):
    """测试波函数功能"""
    
    def test_normalization(self):
        """测试波函数归一化"""
        wf = WaveFunction()
        wf.amplitudes = {'a': 0.5, 'b': 0.5, 'c': 0.5}
        wf.normalize()
        
        total_prob = sum(abs(a)**2 for a in wf.amplitudes.values())
        self.assertAlmostEqual(total_prob, 1.0, places=5)
    
    def test_measurement(self):
        """测试测量坍缩"""
        wf = WaveFunction()
        wf.amplitudes = {'high': 0.8, 'low': 0.2}
        wf.normalize()
        
        # 多次测量应该倾向于high
        results = {'high': 0, 'low': 0}
        for _ in range(100):
            state = wf.measure()
            results[state] += 1
        
        self.assertGreater(results['high'], results['low'])
    
    def test_entanglement(self):
        """测试波函数纠缠"""
        wf1 = WaveFunction()
        wf1.amplitudes = {'up': 0.7, 'down': 0.3}
        
        wf2 = WaveFunction()
        wf2.amplitudes = {'left': 0.6, 'right': 0.4}
        
        entangled = wf1.entangle_with(wf2, strength=0.5)
        
        # 纠缠态应该有联合状态
        self.assertEqual(len(entangled.amplitudes), 4)
        self.assertIn('up⊗left', entangled.amplitudes)


class TestCognitiveAgent(unittest.TestCase):
    """测试认知代理"""
    
    def setUp(self):
        self.agent = CognitiveAgent(
            name="Test Agent",
            cognitive_profile={
                'analytical': 0.7,
                'intuitive': 0.3,
                'risk_tolerance': 0.6,
                'detail_focus': 0.8,
                'decision_speed': 0.5
            }
        )
    
    def test_decision_making(self):
        """测试决策功能"""
        scenario = {'type': 'risky', 'complexity': 0.7}
        decision = self.agent.make_decision(scenario)
        
        self.assertIn('decision', decision)
        self.assertIn('timestamp', decision)
        self.assertIsInstance(decision['decision'], float)
    
    def test_collaboration_influence(self):
        """测试协作影响计算"""
        partner = CognitiveAgent(
            name="Partner",
            cognitive_profile={
                'analytical': 0.4,
                'intuitive': 0.6,
                'risk_tolerance': 0.7,
                'detail_focus': 0.5,
                'decision_speed': 0.7
            }
        )
        
        influence = self.agent._calculate_partner_influence(partner, {})
        
        self.assertIn('analytical_influence', influence)
        self.assertIn('tension', influence)
        self.assertIn('cognitive_distance', influence)


class TestDiversityOptimizer(unittest.TestCase):
    """测试多样性优化器"""
    
    def setUp(self):
        self.optimizer = DiversityOptimizer()
        self.style_a = CognitiveStyle(
            analytical=0.8, detail_oriented=0.9,
            risk_tolerance=0.3, independent=0.7
        )
        self.style_b = CognitiveStyle(
            analytical=0.4, detail_oriented=0.3,
            risk_tolerance=0.8, independent=0.6
        )
    
    def test_distance_calculation(self):
        """测试认知距离计算"""
        distance = self.optimizer.calculate_cognitive_distance(
            self.style_a, self.style_b
        )
        
        self.assertGreater(distance, 0)
        self.assertLess(distance, 1)
    
    def test_sweet_spot_evaluation(self):
        """测试最优区评估"""
        result = self.optimizer.evaluate_diversity_sweet_spot(
            self.style_a, self.style_b
        )
        
        self.assertIn('cognitive_distance', result)
        self.assertIn('sweet_spot_score', result)
        self.assertIn('in_danger_zone', result)
        self.assertIn('diversity_benefit', result)
        self.assertIn('conflict_risk', result)


class TestEmbodiedAnalyzer(unittest.TestCase):
    """测试身体化分析器"""
    
    def setUp(self):
        self.analyzer = EmbodiedAnalyzer()
        
        # 添加测试数据
        for i in range(5):
            self.analyzer.add_data('A', BiomarkerData(
                timestamp=i,
                hr=70 + i * 2,
                hrv=50 + np.random.randint(-5, 5),
                voice_pitch=120 + np.random.randint(-10, 10),
                voice_tremor=0.1 + np.random.random() * 0.1
            ))
            self.analyzer.add_data('B', BiomarkerData(
                timestamp=i,
                hr=72 + i * 2,
                hrv=48 + np.random.randint(-5, 5),
                voice_pitch=125 + np.random.randint(-10, 10),
                voice_tremor=0.12 + np.random.random() * 0.1
            ))
    
    def test_hrv_synchronization(self):
        """测试HRV同步性计算"""
        sync = self.analyzer.calculate_hrv_synchronization()
        
        self.assertGreaterEqual(sync, 0)
        self.assertLessEqual(sync, 1)


class TestNarrativeAnalyzer(unittest.TestCase):
    """测试叙事分析器"""
    
    def setUp(self):
        self.analyzer = NarrativeAnalyzer()
    
    def test_life_story_analysis(self):
        """测试生命故事分析"""
        transcript = "我的人生转折点发生在25岁那年..."
        result = self.analyzer.analyze_life_story(transcript)
        
        self.assertIn('core_themes', result)
        self.assertIn('narrative_tone', result)
        self.assertIn('turning_points', result)


class TestEthicalAligner(unittest.TestCase):
    """测试伦理对齐器"""
    
    def setUp(self):
        self.aligner = EthicalAligner()
    
    def test_yili_scenario_test(self):
        """测试义利情境测试"""
        choices = [
            {'decision_type': 'yi_first_count'},
            {'decision_type': 'yi_li_balance_count'},
            {'decision_type': 'yi_guides_li_count'}
        ]
        
        result = self.aligner.conduct_yili_scenario_test(choices)
        
        self.assertIn('decision_pattern', result)
        self.assertIn('dominant_ethic', result)
        self.assertIn('ru_shang_alignment', result)


class TestEmergentMatcher(unittest.TestCase):
    """测试涌现式匹配器"""
    
    def setUp(self):
        self.matcher = EmergentMatcher()
        self.agent_a = CognitiveAgent(
            name="Agent A",
            cognitive_profile={
                'analytical': 0.7,
                'intuitive': 0.3,
                'risk_tolerance': 0.5,
                'detail_focus': 0.8,
                'decision_speed': 0.5
            }
        )
        self.agent_b = CognitiveAgent(
            name="Agent B",
            cognitive_profile={
                'analytical': 0.4,
                'intuitive': 0.6,
                'risk_tolerance': 0.7,
                'detail_focus': 0.4,
                'decision_speed': 0.7
            }
        )
    
    def test_partnership_simulation(self):
        """测试合作模拟"""
        result = self.matcher.simulate_partnership(
            self.agent_a, self.agent_b, n_scenarios=20
        )
        
        self.assertIn('collaboration_pattern', result)
        self.assertIn('dominant_mode', result)
        self.assertIn('creativity_index', result)
        self.assertIn('attractors', result)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_pipeline(self):
        """测试完整流程"""
        from core.entanglement_system import (
            EntanglementMatchingSystem, PartnerProfile
        )
        
        system = EntanglementMatchingSystem()
        
        partner_a = PartnerProfile(
            name="Test A",
            id="test_a",
            cognitive_profile={
                'analytical': 0.7,
                'intuitive': 0.3,
                'risk_tolerance': 0.6,
                'detail_focus': 0.8,
                'decision_speed': 0.5
            }
        )
        
        partner_b = PartnerProfile(
            name="Test B",
            id="test_b",
            cognitive_profile={
                'analytical': 0.4,
                'intuitive': 0.6,
                'risk_tolerance': 0.7,
                'detail_focus': 0.5,
                'decision_speed': 0.7
            }
        )
        
        result = system.comprehensive_match(partner_a, partner_b)
        
        self.assertIn('overall_compatibility', result)
        self.assertIn('layer_results', result)
        self.assertIn('predictions', result)
        self.assertIn('recommendations', result)
        
        # 验证各层都有结果
        layers = result['layer_results']
        self.assertIn('quantum_perception', layers)
        self.assertIn('emergent_matching', layers)
        self.assertIn('embodied_cognition', layers)
        self.assertIn('cognitive_diversity', layers)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestWaveFunction))
    suite.addTests(loader.loadTestsFromTestCase(TestCognitiveAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestDiversityOptimizer))
    suite.addTests(loader.loadTestsFromTestCase(TestEmbodiedAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestNarrativeAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestEthicalAligner))
    suite.addTests(loader.loadTestsFromTestCase(TestEmergentMatcher))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')
    success = run_tests()
    sys.exit(0 if success else 1)
