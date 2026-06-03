#!/usr/bin/env python3
# pentad_extractor.py - 五元组提取器算法
# 来源: 外援团队交付文档 v1.0
# 功能: 双层混合提取系统 - 规则引擎 + LLM精准提取 + 置信度校验
# 创建时间: 2026-04-04 (从交付文档补实施)
# 版本: 1.0

import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Pentad:
    """五元组数据结构: 情境-框架-判断-结果-反思"""
    situation: str      # 情境
    framework: str      # 框架
    judgment: str       # 判断
    result: str         # 结果
    reflection: str     # 反思
    confidence: float   # 置信度
    source_text: str    # 原始文本

class RuleEngine:
    """规则引擎：快速结构化预处理"""
    
    # 五元组关键词模式
    PATTERNS = {
        'situation': [
            r'当时|情境|背景|环境|条件|面临|遇到|问题|挑战',
            r'situation|context|background'
        ],
        'framework': [
            r'框架|模型|理论|方法|思路|角度|视角|维度',            r'framework|model|theory|method|approach'
        ],
        'judgment': [
            r'判断|决策|选择|认为|觉得|评估|分析',
            r'judgment|decision|choice|evaluate'
        ],
        'result': [
            r'结果|结局|成果|效果|产出|影响|后果',
            r'result|outcome|consequence|impact'
        ],
        'reflection': [
            r'反思|总结|教训|经验|体会|感悟|改进',
            r'reflection|lesson|insight|improve'
        ]
    }
    
    def pre_extract(self, case_text: str) -> Dict[str, List[str]]:
        """
        第一层：规则引擎快速结构化
        返回: 各维度的关键词位置和候选片段
        """
        hints = {
            'situation_hints': [],
            'framework_hints': [],
            'judgment_hints': [],
            'result_hints': [],
            'reflection_hints': []
        }
        
        # 分段处理
        paragraphs = case_text.split('\n')
        
        for i, para in enumerate(paragraphs):
            para_lower = para.lower()
            
            for dimension, patterns in self.PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, para, re.IGNORECASE):
                        hints[f'{dimension}_hints'].append({
                            'paragraph_idx': i,
                            'text': para[:200],  # 前200字符
                            'matched_pattern': pattern
                        })
                        break
        
        return hints
    
    def calculate_rule_confidence(self, hints: Dict) -> float:
        """基于规则匹配计算基础置信度"""
        total_hints = sum(len(v) for v in hints.values())
        # 至少每个维度有一个hints才算高置信度
        if total_hints >= 5:
            return 0.6
        elif total_hints >= 3:
            return 0.4
        else:
            return 0.2

class ConsistencyValidator:
    """一致性校验器：防止漂移"""
    
    def validate(self, pentad: Pentad) -> Tuple[bool, float, List[str]]:
        """
        校验五元组的完整性和一致性
        返回: (是否通过, 置信度得分, 问题列表)
        """
        issues = []
        score = 1.0
        
        # 检查空值
        for field, value in [
            ('situation', pentad.situation),
            ('framework', pentad.framework),
            ('judgment', pentad.judgment),
            ('result', pentad.result),
            ('reflection', pentad.reflection)
        ]:
            if not value or len(value) < 10:
                issues.append(f"{field} 内容过短或为空")
                score -= 0.1
        
        # 检查逻辑一致性
        # 情境应该包含时间/地点/人物等要素
        if not any(kw in pentad.situation for kw in ['时间', '地点', '人物', '当时', '在']):
            issues.append("situation 缺少时空要素")
            score -= 0.05
        
        # 判断应该有明确的决策点
        if not any(kw in pentad.judgment for kw in ['决定', '选择', '判断', '认为']):
            issues.append("judgment 缺少决策标记")
            score -= 0.05
        
        return len(issues) == 0, max(0, score), issues

class PentadExtractor:
    """
    五元组提取器：情境-框架-判断-结果-反思
    设计原则：规则保下限，LLM追上限，校验防漂移
    """
    
    def __init__(self, llm_client=None, token_budget: int = 5000):
        self.llm = llm_client
        self.token_budget = token_budget
        self.rules_engine = RuleEngine()
        self.validator = ConsistencyValidator()
        self.extraction_log = []
    
    def extract(self, case_text: str) -> Dict:
        """
        三层提取流程：
        1. 规则引擎快速结构化
        2. LLM精准提取（带规则提示）
        3. 一致性校验与补全
        """
        # 第一层：规则引擎快速结构化
        rule_hints = self.rules_engine.pre_extract(case_text)
        rule_confidence = self.rules_engine.calculate_rule_confidence(rule_hints)
        
        # 第二层：LLM精准提取（带规则提示）
        if self.llm:
            structured = self.llm_extract(case_text, rule_hints)
        else:
            # 无LLM时，使用规则提取作为fallback
            structured = self._rule_based_extract(case_text, rule_hints)
        
        # 第三层：一致性校验与补全
        pentad = Pentad(
            situation=structured.get('situation', ''),
            framework=structured.get('framework', ''),
            judgment=structured.get('judgment', ''),
            result=structured.get('result', ''),
            reflection=structured.get('reflection', ''),
            confidence=0.0,
            source_text=case_text[:500]
        )
        
        is_valid, validation_score, issues = self.validator.validate(pentad)
        
        # 综合置信度
        final_confidence = (rule_confidence * 0.3 + 
                           structured.get('llm_confidence', 0.5) * 0.5 +
                           validation_score * 0.2)
        
        pentad.confidence = final_confidence
        
        # 记录
        self._log_extraction(case_text, pentad, issues)
        
        return {
            'pentad': {
                'situation': pentad.situation,
                'framework': pentad.framework,
                'judgment': pentad.judgment,
                'result': pentad.result,
                'reflection': pentad.reflection,
                'confidence': final_confidence
            },
            'validation': {
                'is_valid': is_valid,
                'score': validation_score,
                'issues': issues
            },
            'rule_hints': rule_hints
        }
    
    def llm_extract(self, case_text: str, rule_hints: Dict) -> Dict:
        """LLM精准提取（简化版，实际需要接入LLM API）"""
        # 构造prompt
        prompt = self._construct_prompt(case_text, rule_hints)
        
        if self.llm:
            # 实际调用LLM
            try:
                response = self.llm.complete(prompt, max_tokens=self.token_budget)
                return self._parse_llm_response(response)
            except Exception as e:
                # LLM失败，回退到规则提取
                return self._rule_based_extract(case_text, rule_hints)
        else:
            return self._rule_based_extract(case_text, rule_hints)
    
    def _construct_prompt(self, case_text: str, rule_hints: Dict) -> str:
        """构造提取prompt"""
        return f"""请从以下案例中，提取"五元组"（情境-框架-判断-结果-反思）：

案例文本：
{case_text[:2000]}

提取规则：
1. 情境(situation): 描述当时的环境、背景、面临的问题
2. 框架(framework): 使用的思考框架、模型、理论
3. 判断(judgment): 做出的决策、选择、评估
4. 结果(result): 最终的产出、影响、后果
5. 反思(reflection): 事后总结、教训、改进方向

规则提示（辅助定位）：
- 情境可能在段落: {[h['paragraph_idx'] for h in rule_hints.get('situation_hints', [])][:3]}
- 判断可能在段落: {[h['paragraph_idx'] for h in rule_hints.get('judgment_hints', [])][:3]}

请以JSON格式输出，包含confidence字段（0-1）。
"""
    
    def _parse_llm_response(self, response: str) -> Dict:
        """解析LLM响应"""
        try:
            # 尝试提取JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # 解析失败，返回空结构
        return {
            'situation': '',
            'framework': '',
            'judgment': '',
            'result': '',
            'reflection': '',
            'llm_confidence': 0.5
        }
    
    def _rule_based_extract(self, case_text: str, rule_hints: Dict) -> Dict:
        """基于规则的fallback提取"""
        paragraphs = case_text.split('\n')
        
        result = {
            'situation': '',
            'framework': '',
            'judgment': '',
            'result': '',
            'reflection': '',
            'llm_confidence': 0.3  # 规则提取置信度较低
        }
        
        # 提取各维度
        for dimension in ['situation', 'framework', 'judgment', 'result', 'reflection']:
            hints = rule_hints.get(f'{dimension}_hints', [])
            if hints:
                # 取第一个匹配的段落
                idx = hints[0]['paragraph_idx']
                if idx < len(paragraphs):
                    result[dimension] = paragraphs[idx][:300]
        
        return result
    
    def _log_extraction(self, source: str, pentad: Pentad, issues: List[str]):
        """记录提取日志"""
        self.extraction_log.append({
            'timestamp': datetime.now().isoformat(),
            'source_length': len(source),
            'pentad_confidence': pentad.confidence,
            'validation_issues': issues
        })
    
    def get_stats(self) -> Dict:
        """获取提取统计"""
        if not self.extraction_log:
            return {'total': 0, 'avg_confidence': 0}
        
        total = len(self.extraction_log)
        avg_confidence = sum(log['pentad_confidence'] for log in self.extraction_log) / total
        
        return {
            'total': total,
            'avg_confidence': avg_confidence,
            'high_confidence_rate': sum(1 for log in self.extraction_log 
                                       if log['pentad_confidence'] > 0.8) / total
        }

# 便捷函数
def extract_pentad(case_text: str) -> Dict:
    """快速提取五元组"""
    extractor = PentadExtractor()
    return extractor.extract(case_text)

if __name__ == '__main__':
    # 测试
    test_case = """
    当时公司面临严重的现金流问题（情境），我决定采用满意解理论而非追求最优解（框架），
    快速选择了短期融资方案（判断），最终缓解了资金压力（结果）。
    这次经历让我明白，在危机时刻，足够好的决策比完美的决策更重要（反思）。
    """
    
    result = extract_pentad(test_case)
    print(json.dumps(result, ensure_ascii=False, indent=2))
