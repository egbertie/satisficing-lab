#!/usr/bin/env python3
################################################################################
# 对话Token优化器 - 实时优化建议生成器
# 用途: 监控对话上下文，提供压缩/摘要建议
################################################################################

import json
import sys
from typing import List, Dict, Optional
from datetime import datetime

class ConversationOptimizer:
    """对话优化器"""
    
    TOKEN_THRESHOLDS = {
        "warning": 0.7,    # 70% 预警
        "critical": 0.85,  # 85% 严重
        "emergency": 0.95  # 95% 紧急
    }
    
    def __init__(self, log_file: str = "/tmp/conversation_optimizer.log"):
        self.log_file = log_file
        self.session_stats = {
            "start_time": datetime.now().isoformat(),
            "turn_count": 0,
            "total_tokens": 0,
            "compressions_suggested": 0
        }
    
    def analyze_context(self, context_length: int, token_budget: int) -> Dict:
        """分析上下文状态"""
        usage_ratio = context_length / token_budget if token_budget > 0 else 0
        
        status = "normal"
        action = None
        priority = "low"
        
        if usage_ratio >= self.TOKEN_THRESHOLDS["emergency"]:
            status = "emergency"
            action = "force_compact"
            priority = "critical"
        elif usage_ratio >= self.TOKEN_THRESHOLDS["critical"]:
            status = "critical"
            action = "suggest_compact"
            priority = "high"
        elif usage_ratio >= self.TOKEN_THRESHOLDS["warning"]:
            status = "warning"
            action = "prepare_compact"
            priority = "medium"
        
        return {
            "usage_ratio": round(usage_ratio, 2),
            "context_length": context_length,
            "token_budget": token_budget,
            "remaining": token_budget - context_length,
            "status": status,
            "action": action,
            "priority": priority
        }
    
    def generate_recommendations(self, analysis: Dict) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if analysis["status"] == "emergency":
            recommendations.append("🚨 立即执行/compaction——Token即将耗尽")
            recommendations.append("   使用深度标记[快速]或[简要]继续对话")
            recommendations.append("   或新开会话来重置上下文")
        
        elif analysis["status"] == "critical":
            recommendations.append("⚠️ Token使用已达85%，建议压缩上下文")
            recommendations.append("   可执行的优化:")
            recommendations.append("   1. 使用 /compact 压缩对话历史")
            recommendations.append("   2. 使用[简要]标记获取精简回答")
            recommendations.append("   3. 总结当前进展后开启新会话")
        
        elif analysis["status"] == "warning":
            recommendations.append("💡 Token使用达70%，可考虑优化")
            recommendations.append("   预防性措施:")
            recommendations.append("   - 使用深度标记控制回复长度")
            recommendations.append("   - 批量提问代替逐轮确认")
        
        return recommendations
    
    def estimate_savings(self, strategy: str) -> Dict:
        """估算各种策略的节省效果"""
        savings = {
            "depth_markers": {"effort": "low", "savings": "30-50%", "recommendation": "推荐"},
            "batch_questions": {"effort": "low", "savings": "20-40%", "recommendation": "推荐"},
            "compact_context": {"effort": "medium", "savings": "60-80%", "recommendation": "临界点使用"},
            "new_session": {"effort": "high", "savings": "95%", "recommendation": "紧急情况"}
        }
        return savings.get(strategy, {})
    
    def generate_report(self) -> str:
        """生成优化报告"""
        report_lines = [
            "=" * 50,
            "📊 对话Token优化报告",
            "=" * 50,
            f"会话开始: {self.session_stats['start_time']}",
            f"对话轮数: {self.session_stats['turn_count']}",
            f"累计Token: {self.session_stats['total_tokens']}",
            f"建议压缩: {self.session_stats['compressions_suggested']} 次",
            "-" * 50,
            "💡 优化策略建议:",
            "-" * 50,
        ]
        
        for strategy, info in self.estimate_savings("depth_markers").items():
            report_lines.append(f"  [{strategy}] 节省: {info.get('savings', 'N/A')} | 推荐度: {info.get('recommendation', 'N/A')}")
        
        report_lines.append("=" * 50)
        return "\n".join(report_lines)


def main():
    """命令行入口"""
    if len(sys.argv) < 3:
        optimizer = ConversationOptimizer()
        print(optimizer.generate_report())
        sys.exit(0)
    
    context_length = int(sys.argv[1])
    token_budget = int(sys.argv[2])
    
    optimizer = ConversationOptimizer()
    analysis = optimizer.analyze_context(context_length, token_budget)
    recommendations = optimizer.generate_recommendations(analysis)
    
    result = {
        "analysis": analysis,
        "recommendations": recommendations,
        "timestamp": datetime.now().isoformat()
    }
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
