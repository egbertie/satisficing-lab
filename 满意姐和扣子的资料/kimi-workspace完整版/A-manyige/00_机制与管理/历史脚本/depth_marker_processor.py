#!/usr/bin/env python3
################################################################################
# 深度标记协议处理器 - 用户意图快速识别
# 用途: 解析用户输入的深度标记，自动调整响应策略
################################################################################

import sys
import json
import re
from typing import Dict, Tuple, Optional

class DepthMarkerProcessor:
    """深度标记处理器"""
    
    MARKERS = {
        "[快速]": {"depth": "minimal", "max_tokens": 200, "style": "one_liner"},
        "[快]": {"depth": "minimal", "max_tokens": 200, "style": "one_liner"},
        "[简要]": {"depth": "brief", "max_tokens": 800, "style": "bullet_points"},
        "[简]": {"depth": "brief", "max_tokens": 800, "style": "bullet_points"},
        "[标准]": {"depth": "normal", "max_tokens": 2000, "style": "full_paragraph"},
        "[详细]": {"depth": "detailed", "max_tokens": 4000, "style": "comprehensive"},
        "[详]": {"depth": "detailed", "max_tokens": 4000, "style": "comprehensive"},
        "[深度]": {"depth": "deep", "max_tokens": 8000, "style": "analytical"},
        "[深]": {"depth": "deep", "max_tokens": 8000, "style": "analytical"},
        "[战略]": {"depth": "strategic", "max_tokens": 10000, "style": "framework"},
    }
    
    def __init__(self):
        self.default_config = {
            "depth": "normal",
            "max_tokens": 2000,
            "style": "full_paragraph",
            "marker_found": None
        }
    
    def process(self, user_input: str) -> Tuple[str, Dict]:
        """
        处理用户输入，提取深度标记
        
        Returns:
            (cleaned_input, config)
        """
        config = self.default_config.copy()
        cleaned_input = user_input.strip()
        
        for marker, marker_config in self.MARKERS.items():
            if marker in user_input:
                config.update(marker_config)
                config["marker_found"] = marker
                cleaned_input = cleaned_input.replace(marker, "").strip()
                break
        
        return cleaned_input, config
    
    def get_response_guidance(self, config: Dict) -> str:
        """根据配置生成响应指导"""
        depth = config.get("depth", "normal")
        style = config.get("style", "full_paragraph")
        max_tokens = config.get("max_tokens", 2000)
        
        guidance = {
            "minimal": "一句话回答，最多10个字。",
            "brief": "要点式回答，3-5个bullet points。",
            "normal": "正常段落回答，完整但不过度展开。",
            "detailed": "详细回答，包含 reasoning 和细节。",
            "deep": "深度分析，多维度拆解，结构化输出。",
            "strategic": "战略框架，系统性思考，方法论导向。"
        }
        
        return f"[{depth.upper()}] {guidance.get(depth, guidance['normal'])} Token预算: {max_tokens}"


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("Usage: depth_marker_processor.py '<user_input>'")
        sys.exit(1)
    
    user_input = sys.argv[1]
    processor = DepthMarkerProcessor()
    cleaned_input, config = processor.process(user_input)
    
    result = {
        "original": user_input,
        "cleaned": cleaned_input,
        "config": config,
        "guidance": processor.get_response_guidance(config)
    }
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
