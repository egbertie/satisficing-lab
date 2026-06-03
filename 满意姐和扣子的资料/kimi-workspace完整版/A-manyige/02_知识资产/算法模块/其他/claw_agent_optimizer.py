# claw_agent_optimizer.py
from __future__ import annotations
import re

class AgentTokenOptimizer:
    """
    针对Agent多轮对话的Token优化器
    实现复利效应：省下的output不会进入下一轮input
    """
    
    def __init__(self):
        self.session_history = []
        self.mode_active = False
    
    def should_batch_tools(self, planned_tools: list) -> bool:
        """
        判断是否应该合并工具调用，减少交互次数
        从实测看可减少33%工具调用
        """
        # 如果都是同类工具（如都是搜索），建议合并
        if len(planned_tools) > 2 and len(set(t['type'] for t in planned_tools)) == 1:
            return True
        return False
    
    def create_batch_prompt(self, tools: list, language: str = "zh") -> str:
        """
        创建批量执行提示词，减少中间响应
        """
        if language == "zh":
            return f"依次行{len(tools)}事，毕后总报结果，勿逐条述。"
        return f"Execute {len(tools)} tasks sequentially. Report final result only. No intermediate chatter."
    
    def compress_context_window(self, history: list, max_tokens: int = 4000) -> list:
        """
        压缩上下文窗口，移除历史中的废话
        """
        compressed = []
        for msg in history:
            if msg['role'] == 'assistant' and self.mode_active:
                # 压缩历史assistant消息
                content = msg['content']
                # 移除过长的解释，保留核心结果
                if len(content) > 200:
                    # 提取代码块、关键数据
                    code_blocks = re.findall(r'```[\s\S]*?```', content)
                    key_data = re.findall(r'\*\*.*?\*\*|result[:：].*?\n', content)
                    content = "\n".join(code_blocks + key_data)
                msg['content'] = content[:500]  # 限制每条历史记录
            compressed.append(msg)
        return compressed[-5:]  # 只保留最近5轮（关键！）
    
    def get_tool_summary_template(self, success: bool, tool_type: str) -> str:
        """
        获取工具调用后的极简状态模板
        """
        templates = {
            ("zh", True): "✓",
            ("zh", False): "✗",
            ("en", True): "OK",
            ("en", False): "FAIL"
        }
        return templates.get(("zh", success), "Done")
