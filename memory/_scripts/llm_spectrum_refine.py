#!/usr/bin/env python3
"""产品AI认知推理精评脚本
对精选产品（精品+体验型+全脑型+高价值）进行LLM认知推理评分
使用方法: python3 memory/_scripts/llm_spectrum_refine.py
"""

import json, os, sys
from datetime import datetime, timezone, timedelta

tz_shanghai = timezone(timedelta(hours=8))
now_iso = datetime.now(tz_shanghai).isoformat()

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_products():
    with open(os.path.join(WORKSPACE, 'memory/_data/entities_index.json'), 'r') as f:
        return json.load(f)

def select_refine_candidates(products):
    """选择需要LLM精评的产品候选"""
    candidates = []
    for p in products:
        sp = p.get('spectrum', {})
        # 优先级1: 精品 + 体验型 + 全脑型
        if sp.get('hemisphere') in ('Ⅱ·体验型', 'Ⅰ·全脑型') and p.get('status') == '精品':
            candidates.append(('P1_旗舰', p))
        # 优先级2: simulation_game 类型
        elif p.get('product_type') == 'simulation_game':
            candidates.append(('P2_模拟', p))
        # 优先级3: 高价值标签
        elif p.get('value_label', '').startswith('🍒'):
            candidates.append(('P3_核心', p))
    return candidates

def build_llm_prompt(p):
    """构建单个产品的LLM评分prompt"""
    return f"""你是满意解研究所的产品认知评估师。请从以下五个维度对一个产品进行评分（每个维度 0-100 分，给出具体数字和一句话推理依据）：

产品名称：{p.get('name','?')}
产品描述：{p.get('description','?')}
产品类型：{p.get('product_type','未指定')}
产品用途（JTBD）：{p.get('jtbd_category','?')}
产品标签：{', '.join(p.get('tags',['无']))}

评分维度：
【土·时间轴】这个产品多大程度帮人看得更长远、连接历史与未来？（0=用完即弃，100=穿越周期的智慧）
【金·可行域】这个产品多大程度帮人做结构化分析、选项权衡和资源决策？（0=纯直觉，100=数学化最优解）
【水·身心流】这个产品多大程度关注身体信号、内在状态和决策者自身的身心感知？（0=纯理性，100=身体即仪表盘）
【木·信义观】这个产品多大程度涉及承诺一致性、原则坚守和道德判断？（0=纯功利，100=宁舍利益不舍信义）
【火·直觉阈】这个产品多大程度依赖或激发直觉、创意和顿悟式突破？（0=纯分析，100=纯直觉驱动）

请输出严格的 JSON 格式：
{{
  "product_id": "{p.get('id','')}",
  "scores": {{"土":整数,"金":整数,"水":整数,"木":整数,"火":整数}},
  "reasoning": {{"土":"一句话","金":"一句话","水":"一句话","木":"一句话","火":"一句话"}}
}}"""

def compute_LR(scores):
    L = round((scores['土'] + scores['金']) / 2, 1)
    R = round((scores['水'] + scores['火']) / 2, 1)
    balance = round(1 - abs(L - R) / 100, 2)
    quadrant = 'Ⅰ·全脑型' if L>=50 and R>=50 else ('Ⅱ·体验型' if L<50 and R>=50 else ('Ⅲ·真空型' if L<50 and R<50 else 'Ⅳ·分析型'))
    dims = sorted(scores.items(), key=lambda x:-x[1])
    return L, R, balance, quadrant, dims[0][0], dims[1][0]

def main():
    data = load_products()
    products = data.get('products', [])
    
    candidates = select_refine_candidates(products)
    print(f"🔍 选中 {len(candidates)} 个产品进行LLM精评")
    
    # 按优先级排序
    candidates.sort(key=lambda x: x[0])
    
    # 输出前20个最高优先级的产品信息（供手动/半自动LLM评分）
    print(f"\n{'='*70}")
    print(f"优先级排序（前20）:")
    print(f"{'='*70}")
    
    for rank, (priority, p) in enumerate(candidates[:20]):
        sp = p.get('spectrum', {})
        old_scores = sp.get('five_elements', {})
        print(f"\n{rank+1}. [{priority}] {p['id']} {p['name'][:40]}")
        print(f"   类型:{p.get('product_type')} | JTBD:{p.get('jtbd_category')} | 状态:{p.get('status')}")
        print(f"   当前评分: L={sp.get('L')} R={sp.get('R')} | {sp.get('hemisphere')}")
        print(f"   五维: 土{old_scores.get('土_时间轴','-')} 金{old_scores.get('金_可行域','-')} 水{old_scores.get('水_身心流','-')} 木{old_scores.get('木_信义观','-')} 火{old_scores.get('火_直觉阈','-')}")
        
        # 保存prompt
        prompt = build_llm_prompt(p)
        prompt_file = os.path.join(WORKSPACE, f"memory/_data/llm_prompts/{p['id']}_prompt.txt")
        os.makedirs(os.path.dirname(prompt_file), exist_ok=True)
        with open(prompt_file, 'w') as f:
            f.write(prompt)
    
    print(f"\n{'='*70}")
    print(f"✅ 已生成 {min(20, len(candidates))} 个 LLM 评分 prompt")
    print(f"   文件位置: memory/_data/llm_prompts/")
    print(f"   下一步: 用 LLM 逐批精评 → 差异检测 → 写入索引")
    
    # 统计概要
    priorities = {}
    for pri, _ in candidates:
        priorities[pri] = priorities.get(pri, 0) + 1
    print(f"\n   优先级分布: {priorities}")

if __name__ == '__main__':
    main()
