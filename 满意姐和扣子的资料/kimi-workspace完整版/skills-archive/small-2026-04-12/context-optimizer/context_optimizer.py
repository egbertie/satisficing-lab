#!/usr/bin/env python3
"""
Context Optimizer - 上下文优化器
智能对话压缩与记忆分层管理
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

WORKSPACE = Path("/root/.openclaw/workspace")
OPTIMIZER_DB = WORKSPACE / "memory" / "context-optimizer-db.json"

class ContextOptimizer:
    """上下文优化器"""
    
    def __init__(self, token_limit: int = 8000):
        self.token_limit = token_limit
        self.db_path = OPTIMIZER_DB
        self.compressions = self._load_db()
    
    def _load_db(self) -> Dict:
        if self.db_path.exists():
            with open(self.db_path, 'r') as f:
                return json.load(f)
        return {"compressions": [], "layers": {"short": [], "medium": [], "long": []}}
    
    def _save_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.db_path, 'w') as f:
            json.dump(self.compressions, f, indent=2)
    
    def estimate_tokens(self, text: str) -> int:
        """估算token数量（粗略：1token≈4字符）"""
        return len(text) // 4
    
    def should_compress(self, current_tokens: int) -> bool:
        """判断是否需要压缩"""
        return current_tokens > self.token_limit * 0.8
    
    def compress(self, context: str, strategy: str = "summary") -> str:
        """压缩上下文"""
        if strategy == "summary":
            # 简单摘要：取前200字符+...+后100字符
            if len(context) > 300:
                return context[:200] + "\n...[压缩内容]...\n" + context[-100:]
        return context
    
    def archive_layer(self, layer: str, data: Dict):
        """归档到记忆分层"""
        if layer in self.compressions["layers"]:
            self.compressions["layers"][layer].append({
                "data": data,
                "timestamp": datetime.now().isoformat()
            })
            self._save_db()
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "token_limit": self.token_limit,
            "total_compressions": len(self.compressions["compressions"]),
            "archive_sizes": {k: len(v) for k, v in self.compressions["layers"].items()}
        }

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("="*60)
        print("🧪 Context Optimizer S5/S7 验证")
        print("="*60)
        
        optimizer = ContextOptimizer()
        
        # S7: 对抗测试
        print("\n[S7] 对抗测试...")
        
        # 测试1: 空文本压缩
        result = optimizer.compress("")
        assert result == "", "空文本应返回空"
        print("  ✅ 空文本压缩测试通过")
        
        # 测试2: 超长文本
        long_text = "A" * 10000
        result = optimizer.compress(long_text)
        assert len(result) < len(long_text), "应压缩"
        print("  ✅ 超长文本压缩测试通过")
        
        # 测试3: 无效策略
        result = optimizer.compress("test", strategy="invalid")
        assert result == "test", "无效策略应返回原文"
        print("  ✅ 无效策略测试通过")
        
        # 测试4: Token估算
        tokens = optimizer.estimate_tokens("Hello World")
        assert tokens >= 0, "Token数应非负"
        print("  ✅ Token估算测试通过")
        
        # S5: 自我验证
        print("\n[S5] 自我验证...")
        status = optimizer.get_status()
        assert status["token_limit"] == 8000, "默认限制应为8000"
        print("  ✅ 状态统计正确")
        
        print("\n" + "="*60)
        print("✅ S5/S7验证通过")
        print("="*60)
        return 0
    else:
        optimizer = ContextOptimizer()
        print(f"Context Optimizer 初始化完成")
        print(f"Token限制: {optimizer.get_status()['token_limit']}")
        return 0

if __name__ == "__main__":
    sys.exit(main())
