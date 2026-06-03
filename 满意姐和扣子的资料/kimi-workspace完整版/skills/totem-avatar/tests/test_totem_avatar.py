#!/usr/bin/env python3
"""
Totem Avatar System - 测试套件
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from totem_avatar import (
    TotemAvatar, TotemRouter, TotemSession, TotemType,
    TOTEM_PROMPTS, TOTEM_DISPLAY_NAMES, TOTEM_KNOWLEDGE
)


class TestTotemRouter(unittest.TestCase):
    """图腾路由器测试"""
    
    def setUp(self):
        self.router = TotemRouter()
    
    def test_detect_simon_activation(self):
        """测试司马贺激活检测"""
        test_cases = [
            "[激活司马贺] 这个问题怎么决策？",
            "[激活simon] 合伙人选择",
            "用司马贺的视角看看这个问题",
            "司马贺怎么看这个决策？"
        ]
        
        for tc in test_cases:
            result = self.router.detect_totem(tc)
            self.assertEqual(result, TotemType.SIMON, f"Failed for: {tc}")
    
    def test_detect_confucius_activation(self):
        """测试孔子激活检测"""
        test_cases = [
            "[激活孔子] 这个合作合适吗？",
            "用孔子的视角分析一下"
        ]
        
        for tc in test_cases:
            result = self.router.detect_totem(tc)
            self.assertEqual(result, TotemType.CONFUCIUS)
    
    def test_detect_huineng_activation(self):
        """测试慧能激活检测"""
        test_cases = [
            "[激活六祖慧能] 压力很大",
            "[激活慧能] 如何突破？"
        ]
        
        for tc in test_cases:
            result = self.router.detect_totem(tc)
            self.assertEqual(result, TotemType.HUINENG)
    
    def test_no_activation(self):
        """测试无激活指令"""
        result = self.router.detect_totem("这个问题怎么解决？")
        self.assertIsNone(result)
    
    def test_remove_activation_cmd(self):
        """测试去除激活指令"""
        test_cases = [
            ("[激活司马贺] 问题", "问题"),
            ("用司马贺的视角看看这个问题", "看看这个问题"),
            ("普通问题", "普通问题")
        ]
        
        for input_text, expected in test_cases:
            result = self.router._remove_activation_cmd(input_text)
            self.assertEqual(result, expected)


class TestTotemSession(unittest.TestCase):
    """图腾会话测试"""
    
    def test_session_creation(self):
        """测试会话创建"""
        session = TotemSession(
            session_id="test_session",
            totem_type=TotemType.SIMON
        )
        
        self.assertEqual(session.totem_type, TotemType.SIMON)
        self.assertEqual(len(session.history), 0)
    
    def test_add_exchange(self):
        """测试添加对话记录"""
        session = TotemSession(
            session_id="test_session",
            totem_type=TotemType.SIMON
        )
        
        session.add_exchange("用户问题", "图腾回答")
        
        self.assertEqual(len(session.history), 2)
        self.assertEqual(session.history[0]["role"], "user")
        self.assertEqual(session.history[1]["role"], "totem")
    
    def test_history_limit(self):
        """测试历史记录限制（最多10条=5轮）"""
        session = TotemSession(
            session_id="test_session",
            totem_type=TotemType.SIMON
        )
        
        # 添加6轮对话（12条记录）
        for i in range(6):
            session.add_exchange(f"问题{i}", f"回答{i}")
        
        # 应该只保留最近5轮（10条）
        self.assertEqual(len(session.history), 10)


class TestTotemAvatar(unittest.TestCase):
    """图腾数字替身主类测试"""
    
    def setUp(self):
        self.avatar = TotemAvatar()
    
    def test_invoke_simon(self):
        """测试调用司马贺"""
        result = self.avatar.invoke("[激活司马贺] 合伙人怎么选？")
        
        self.assertEqual(result["totem"], "simon")
        self.assertEqual(result["totem_name"], "司马贺")
        self.assertIn("system_prompt", result)
        self.assertIn("user_prompt", result)
        
        # 验证system_prompt包含核心概念
        self.assertIn("满意解", result["system_prompt"])
        self.assertIn("有限理性", result["system_prompt"])
    
    def test_invoke_with_history(self):
        """测试带历史的调用"""
        # 第一轮对话
        self.avatar.invoke("[激活司马贺] 问题1", user_id="user1")
        
        # 第二轮对话（应该有历史）
        result = self.avatar.invoke("追问1", user_id="user1")
        
        # user_prompt应该包含历史
        self.assertIn("对话历史", result["user_prompt"])
    
    def test_knowledge_context(self):
        """测试知识上下文构建"""
        result = self.avatar.invoke("[激活司马贺] 测试")
        
        # 验证知识上下文
        self.assertIn("经典引用", result["knowledge_context"])


class TestTotemPrompts(unittest.TestCase):
    """图腾Prompt测试"""
    
    def test_all_totems_have_prompts(self):
        """测试所有图腾都有prompt"""
        for totem_type in TotemType:
            self.assertIn(totem_type, TOTEM_PROMPTS)
            self.assertIsNotNone(TOTEM_PROMPTS[totem_type])
            self.assertGreater(len(TOTEM_PROMPTS[totem_type]), 100)
    
    def test_simon_prompt_content(self):
        """测试司马贺prompt内容"""
        prompt = TOTEM_PROMPTS[TotemType.SIMON]
        
        # 应包含核心要素
        self.assertIn("赫伯特·西蒙", prompt)
        self.assertIn("满意解", prompt)
        self.assertIn("有限理性", prompt)
        self.assertIn("司马贺视角分析", prompt)
        self.assertIn("金句", prompt)
    
    def test_display_names(self):
        """测试显示名称"""
        self.assertEqual(TOTEM_DISPLAY_NAMES[TotemType.SIMON], "司马贺")
        self.assertEqual(TOTEM_DISPLAY_NAMES[TotemType.CONFUCIUS], "孔子")
        self.assertEqual(TOTEM_DISPLAY_NAMES[TotemType.HUINENG], "六祖慧能")


class TestTotemKnowledge(unittest.TestCase):
    """图腾知识库测试"""
    
    def test_simon_knowledge(self):
        """测试司马贺知识库"""
        knowledge = TOTEM_KNOWLEDGE["simon"]
        
        self.assertIn("classic_quotes", knowledge)
        self.assertIn("key_concepts", knowledge)
        
        # 验证有经典引用
        quotes = knowledge["classic_quotes"]
        self.assertGreater(len(quotes), 0)
        
        # 验证引用结构
        for quote in quotes:
            self.assertIn("text", quote)
            self.assertIn("source", quote)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_workflow(self):
        """测试完整工作流"""
        avatar = TotemAvatar()
        
        # 步骤1: 用户激活司马贺并提问
        result1 = avatar.invoke(
            "[激活司马贺] 我在选择合伙人，候选人A技术很强但价值观有偏差，怎么办？",
            user_id="test_user"
        )
        
        self.assertEqual(result1["totem"], "simon")
        self.assertIn("system_prompt", result1)
        
        # 步骤2: 模拟保存响应
        avatar.save_response(
            "test_user",
            "[激活司马贺] 我在选择合伙人...",
            "这是司马贺的分析回答..."
        )
        
        # 步骤3: 用户追问
        result2 = avatar.invoke(
            "那候选人B呢？技术一般但价值观很合",
            user_id="test_user"
        )
        
        # 应该有历史记录
        self.assertIn("对话历史", result2["user_prompt"])
    
    def test_multi_totem_switching(self):
        """测试多图腾切换"""
        avatar = TotemAvatar()
        
        # 激活司马贺
        result1 = avatar.invoke("[激活司马贺] 问题1", user_id="user2")
        self.assertEqual(result1["totem"], "simon")
        
        # 切换到慧能
        result2 = avatar.invoke("[激活慧能] 问题2", user_id="user2")
        self.assertEqual(result2["totem"], "huineng")
        
        # 无激活指令时保持慧能
        result3 = avatar.invoke("追问", user_id="user2")
        self.assertEqual(result3["totem"], "huineng")


if __name__ == '__main__':
    unittest.main(verbosity=2)
