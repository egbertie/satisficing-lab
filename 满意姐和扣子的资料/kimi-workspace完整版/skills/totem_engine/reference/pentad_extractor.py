"""
外援代码: 五元组提取器
来源: external_assistance_request_v1.0.md
状态: 保持原样，未经修改
"""
import re
import json
from typing import Dict, List, Optional

# jieba为可选依赖
try:
    import jieba
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False

class PentadExtractor:
    """
    五元组提取器完整实现
    约束适配：CPU only, <5s/案例, ~5000 tokens
    """
    def __init__(self, llm_api_call, token_budget=5000):
        """
        llm_api_call: 函数签名 (prompt: str) -> str
        """
        self.llm_call = llm_api_call
        self.token_budget = token_budget
        self.rules = RuleEngine()

    def extract(self, case_text: str, verbose=False) -> Dict:
        """主入口：提取五元组"""
        # 步骤1: 规则预处理（<100ms）
        hints = self.rules.pre_extract(case_text)
        # 步骤2: 构建优化提示（控制token）
        prompt = self._build_prompt(case_text, hints, self.token_budget)
        # 步骤3: LLM提取（占主要时间）
        try:
            response = self.llm_call(prompt)
            structured = self._parse_json(response)
        except Exception as e:
            structured = self._fallback_extract(case_text, hints)
        # 步骤4: 验证与增强
        final = self._post_process(structured, case_text, hints)
        if verbose:
            final['_meta'] = {'hints': hints, 'prompt_tokens': len(prompt)}
        return final

    def _build_prompt(self, text: str, hints: dict, budget: int) -> str:
        """构建token受限的提示"""
        # 简化策略：如果文本过长，先提取关键段落
        if len(text) > 2000:  # 约500 tokens
            text = self._extract_key_paragraphs(text, hints)
        template = f"""提取商业案例的五元组结构。线索：{json.dumps(hints, ensure_ascii=False)}
案例：{text}
严格按JSON输出：
{{"situation":"...","decision_framework":"...","judgment":"...","outcome":"...","reflection":"..."}}
"""
        return template

    def _fallback_extract(self, text: str, hints: dict) -> dict:
        """当LLM失败时的降级策略：基于规则组装"""
        return {
            'situation': hints.get('situation', ['IMPLICIT'])[0] if hints.get('situation') else "IMPLICIT",
            'decision_framework': hints.get('decision_framework', ['IMPLICIT'])[0] if hints.get('decision_framework') else "IMPLICIT",
            'judgment': hints.get('judgment', ['IMPLICIT'])[0] if hints.get('judgment') else "IMPLICIT",
            'outcome': hints.get('outcome', ['IMPLICIT'])[0] if hints.get('outcome') else "IMPLICIT",
            'reflection': hints.get('reflection', ['IMPLICIT'])[0] if hints.get('reflection') else "IMPLICIT",
            '_method': 'rule_fallback'
        }

    def _post_process(self, data: dict, text: str, hints: dict) -> dict:
        """后处理：清洗、验证、增强"""
        # 清洗：移除markdown代码块标记
        for k, v in data.items():
            if isinstance(v, str):
                data[k] = v.strip().strip('`').strip()
        # 验证：确保没有 hallucination（关键名词必须在原文）
        key_terms = set(re.findall(r'[\u4e00-\u9fa5]{2,6}', text))  # 2-6字词组
        for field in ['situation', 'judgment', 'outcome']:
            if field in data and data[field] != "IMPLICIT":
                field_terms = set(re.findall(r'[\u4e00-\u9fa5]{2,6}', data[field]))
                # 如果提取的内容与原文共享<30%词汇，标记为可疑
                if len(field_terms) > 0 and len(field_terms & key_terms) / len(field_terms) < 0.3:
                    data[f'_{field}_warning'] = 'low_term_overlap'
        # 增强：如果反思缺失但有"后来/结果"段落，尝试组装
        if data.get('reflection') == "IMPLICIT" and hints.get('reflection'):
            data['reflection'] = hints['reflection'][0]
            data['_reflection_source'] = 'rule_supplemented'
        return data

    def _parse_json(self, text: str) -> dict:
        """鲁棒JSON解析"""
        # 尝试直接解析
        try:
            return json.loads(text)
        except:
            # 提取JSON子串
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise ValueError("Invalid JSON format")

    def _extract_key_paragraphs(self, text: str, hints: dict) -> str:
        """提取关键段落（简化版）"""
        # 基于线索提取相关段落
        paragraphs = text.split('\n')
        key_paragraphs = []
        for p in paragraphs:
            for field, matches in hints.items():
                for m in matches:
                    if m in p and p not in key_paragraphs:
                        key_paragraphs.append(p)
                        break
        # 如果太少，补充开头和结尾
        if len(key_paragraphs) < 3:
            key_paragraphs = paragraphs[:2] + key_paragraphs + paragraphs[-2:]
        return '\n'.join(key_paragraphs[:5])  # 最多5段


class RuleEngine:
    """规则引擎实现"""
    PATTERNS = {
        'situation': [
            r'([^。，；]*?(?:背景|来自|基于|处于|面临)[^。，；]*[。，；])',
            r'^([^。]*?(?:创始人|CEO|项目|公司)[^。]*[。])'
        ],
        'decision_framework': [
            r'([^。]*?(?:通过|借助|使用|采用|参考|基于)[^。]*?(?:方法|理论|框架|标准|介绍)[^。]*[。])'
        ],
        'judgment': [
            r'([^。]*?(?:决定|选择|确定|聘请|任命|合作|签约)[^。]*[。])',
            r'([^。]*?(?:经过.*?(?:讨论|协商|评估|考察))[^。]*[。])'
        ],
        'outcome': [
            r'((?:结果|最终|后来| outcome|result)[^。]*[。])',
            r'([^。]*?(?:成功|失败|融资|退出|解散|盈利|亏损)[^。]*[。])'
        ],
        'reflection': [
            r'([^。]*?(?:反思|复盘|总结|教训|启示|意识到|应该)[^。]*[。])',
            r'([^。]*?(?:如果|要是|后悔|庆幸)[^。]*[。])'
        ]
    }

    def pre_extract(self, text: str) -> dict:
        hints = {}
        for field, patterns in self.PATTERNS.items():
            matches = []
            for p in patterns:
                found = re.findall(p, text)
                matches.extend([m.strip() for m in found if len(m) > 5])
            hints[field] = matches[:2]
        return hints
