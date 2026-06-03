"""
research_lib.py
Conversation Researcher 共享库
"""

from typing import Dict, List, Any, Optional
import json
from dataclasses import dataclass

@dataclass
class ResearchConfig:
    """研究配置"""
    min_sources: int = 3
    max_sources: int = 10
    freshness: str = "py"
    include_content: bool = True
    timeout_ms: int = 30000

@dataclass
class ValidationConfig:
    """验证配置"""
    min_cross_validation: int = 3
    consensus_threshold: float = 0.6

class SourceAssessor:
    """来源评估器"""
    
    AUTHORITY_DOMAINS = {
        'academic': ['.edu', 'arxiv.org', 'ieee.org', 'acm.org', 'nature.com', 'science.org'],
        'official': ['.gov', '.mil', 'un.org', 'worldbank.org'],
        'major_media': ['bbc.com', 'reuters.com', 'apnews.com', 'nytimes.com', 'washingtonpost.com'],
        'industry': ['github.com', 'stackoverflow.com', 'medium.com', 'techcrunch.com'],
    }
    
    @classmethod
    def assess(cls, url: str) -> tuple:
        """
        评估来源权威性
        返回: (category, score)
        """
        url_lower = url.lower()
        
        for category, domains in cls.AUTHORITY_DOMAINS.items():
            if any(d in url_lower for d in domains):
                scores = {
                    'academic': 0.95,
                    'official': 0.9,
                    'major_media': 0.85,
                    'industry': 0.75
                }
                return category, scores.get(category, 0.5)
        
        if 'wikipedia' in url_lower:
            return 'reference', 0.7
        
        return 'unknown', 0.5

class ConsensusCalculator:
    """共识度计算器"""
    
    @staticmethod
    def calculate(sources: List[Any]) -> float:
        """
        计算多源共识度
        基于来源数量、权威性、一致性
        """
        if not sources:
            return 0.0
        
        # 基础分：来源数量 (最多1.0)
        count_score = min(len(sources) / 5, 1.0)
        
        # 权威性平均分
        authority_score = sum(getattr(s, 'authority', 0.5) for s in sources) / len(sources)
        
        # 综合评分
        return round((count_score * 0.4 + authority_score * 0.6), 2)

class ReportFormatter:
    """报告格式化器"""
    
    @staticmethod
    def format_stars(score: float, max_stars: int = 5) -> str:
        """将分数转换为星级"""
        filled = int(score * max_stars)
        return "★" * filled + "☆" * (max_stars - filled)
    
    @staticmethod
    def truncate(text: str, max_len: int = 100) -> str:
        """截断文本"""
        if len(text) <= max_len:
            return text
        return text[:max_len-3] + "..."
