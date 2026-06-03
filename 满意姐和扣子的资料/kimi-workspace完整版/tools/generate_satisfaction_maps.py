import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 定义一堂风格配色
COLORS = {
    'bg': '#FFF8F0',
    'stage1': '#FFE4B5',      # 浅黄
    'stage2': '#FFCC80',      # 橙黄
    'stage3': '#FFB74D',      # 橙色
    'stage4': '#FF8A65',      # 橙红
    'stage5': '#E57373',      # 红
    'text_dark': '#3E2723',
    'text_mid': '#5D4037',
    'border': '#BF360C',
    'accent': '#FF6F00',
}

def draw_totem_map():
    """五路图腾进阶图"""
    fig, ax = plt.subplots(figsize=(14, 10), facecolor=COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # 标题
    ax.text(7, 9.5, '五路图腾 · 决策进阶地图', fontsize=22, ha='center', 
            fontweight='bold', color=COLORS['text_dark'])
    ax.text(7, 9.0, 'V1.6 满意解决策操作系统', fontsize=12, ha='center', 
            color=COLORS['text_mid'], style='italic')
    
    # 五层金字塔结构
    levels = [
        {'name': '六祖慧能·火', 'subtitle': '直觉突破 / 极限测试', 'color': COLORS['stage5'], 'y': 1.2, 'w': 2.5},
        {'name': '孔子·木', 'subtitle': '伦理校准 / 仁义礼智信', 'color': COLORS['stage4'], 'y': 2.8, 'w': 4.0},
        {'name': '观自在·水', 'subtitle': '状态扫描 / 情绪与上下文', 'color': COLORS['stage3'], 'y': 4.4, 'w': 5.5},
        {'name': '司马贺·金', 'subtitle': '满意解标准 / 量化边界', 'color': COLORS['stage2'], 'y': 6.0, 'w': 7.0},
        {'name': '刘禹锡·土', 'subtitle': '价值根基 / 德馨聚贤', 'color': COLORS['stage1'], 'y': 7.6, 'w': 8.5},
    ]
    
    for i, lv in enumerate(reversed(levels)):
        x_center = 7
        x_left = x_center - lv['w'] / 2
        height = 1.4
        
        # 绘制梯形块
        rect = FancyBboxPatch((x_left, lv['y']), lv['w'], height,
                              boxstyle="round,pad=0.02,rounding_size=0.15",
                              facecolor=lv['color'], edgecolor=COLORS['border'],
                              linewidth=2, alpha=0.95)
        ax.add_patch(rect)
        
        # 主标题
        ax.text(x_center, lv['y'] + height/2 + 0.15, lv['name'], 
                fontsize=14 - i*0.5, ha='center', va='center',
                fontweight='bold', color=COLORS['text_dark'])
        # 副标题
        ax.text(x_center, lv['y'] + height/2 - 0.25, lv['subtitle'], 
                fontsize=9, ha='center', va='center',
                color=COLORS['text_mid'])
        
        # 箭头和循环标注
        if i < 4:
            ax.annotate('', xy=(x_center, lv['y'] + height), 
                       xytext=(x_center, lv['y'] + height + 0.2),
                       arrowprops=dict(arrowstyle='->', color=COLORS['accent'], lw=2))
    
    # 右侧关键问题
    questions = [
        "价值根基\n'五年后还会对吗？'",
        "满意解标准\n'是不是在等完美信息？'",
        "状态扫描\n'谁的情绪被推起来了？'",
        "伦理校准\n'十年后经得起考验吗？'",
        "直觉突破\n'心里那个直觉敢说吗？'"
    ]
    
    for i, q in enumerate(questions):
        y_pos = 7.6 + 1.4 * (4 - i) / 2 + 0.35
        ax.text(12.5, y_pos, q, fontsize=8, ha='center', va='center',
                color=COLORS['text_mid'], style='italic',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                         edgecolor=COLORS['border'], alpha=0.8, linewidth=1))
        # 连线
        ax.plot([11.0, 11.5], [y_pos, y_pos], color=COLORS['accent'], lw=1, alpha=0.6)
    
    # 底部：旋转箭头表示循环
    ax.annotate('', xy=(10.5, 1.0), xytext=(3.5, 1.0),
               arrowprops=dict(arrowstyle='->', color=COLORS['accent'], lw=2.5,
                              connectionstyle="arc3,rad=-0.3"))
    ax.text(7, 0.3, '土生金 → 金生水 → 水生木 → 木生火 → 火生土（循环校准）', 
            fontsize=10, ha='center', color=COLORS['accent'], fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/root/.openclaw/workspace/A-manyige/项目版本/V1.6/设计资产/五路图腾进阶地图-V1.0.png', 
                dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()
    print("五路图腾进阶地图已生成")


def draw_conflict_stage_map():
    """12类型冲突阶段分布图"""
    fig, ax = plt.subplots(figsize=(16, 11), facecolor=COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 11)
    ax.axis('off')
    
    # 标题
    ax.text(8, 10.4, '满意解 · 12类型合伙人冲突阶段分布图', fontsize=20, ha='center',
            fontweight='bold', color=COLORS['text_dark'])
    ax.text(8, 9.9, '从风险预兆 → 冲突爆发 → 调解路径的全景导航', fontsize=11, ha='center',
            color=COLORS['text_mid'], style='italic')
    
    # 三大阶段横条（顶部）
    stages = [
        {'name': '预判阶段', 'desc': '股权/能力/动机/节奏的潜在错配', 'color': COLORS['stage1'], 'x': 1, 'w': 4.5},
        {'name': '起盘阶段', 'desc': '从蜜月期到第一次重大分歧', 'color': COLORS['stage3'], 'x': 5.8, 'w': 4.5},
        {'name': '增长阶段', 'desc': '规模化带来的权力与价值观冲突', 'color': COLORS['stage5'], 'x': 10.6, 'w': 4.5},
    ]
    
    for st in stages:
        rect = FancyBboxPatch((st['x'], 8.5), st['w'], 1.0,
                              boxstyle="round,pad=0.02,rounding_size=0.15",
                              facecolor=st['color'], edgecolor=COLORS['border'],
                              linewidth=2.5, alpha=0.9)
        ax.add_patch(rect)
        ax.text(st['x'] + st['w']/2, 9.15, st['name'], fontsize=13, ha='center', 
                va='center', fontweight='bold', color=COLORS['text_dark'])
        ax.text(st['x'] + st['w']/2, 8.75, st['desc'], fontsize=8, ha='center',
                va='center', color=COLORS['text_mid'])
    
    # 箭头连接
    for i in range(2):
        ax.annotate('', xy=(stages[i+1]['x'] - 0.1, 9.0),
                   xytext=(stages[i]['x'] + stages[i]['w'] + 0.1, 9.0),
                   arrowprops=dict(arrowstyle='->', color=COLORS['accent'], lw=2))
    
    # 12类型卡片矩阵
    conflict_types = [
        # 预判阶段 (Type 1,2,3,4)
        {'type': 'Type01', 'name': '能力互补型股权黑洞', 'stage': 0, 'row': 0, 'risk': '高'},
        {'type': 'Type02', 'name': '股权均分下的决策僵局', 'stage': 0, 'row': 1, 'risk': '高'},
        {'type': 'Type03', 'name': '资源承诺幻灭后的信任崩塌', 'stage': 0, 'row': 2, 'risk': '中高'},
        {'type': 'Type04', 'name': '愿景一致但节奏冲突', 'stage': 0, 'row': 3, 'risk': '中'},
        # 起盘阶段 (Type 5,6,7,8)
        {'type': 'Type05', 'name': '新老合伙人融合排异', 'stage': 1, 'row': 0, 'risk': '高'},
        {'type': 'Type06', 'name': '出资与出力估值撕裂', 'stage': 1, 'row': 1, 'risk': '中高'},
        {'type': 'Type07', 'name': '技术合伙人商业话语权缺失', 'stage': 1, 'row': 2, 'risk': '高'},
        {'type': 'Type08', 'name': '空降高管与创始团队的文化对冲', 'stage': 1, 'row': 3, 'risk': '中高'},
        # 增长阶段 (Type 9,10,11,12)
        {'type': 'Type09', 'name': '融资后轮次中的控制权博弈', 'stage': 2, 'row': 0, 'risk': '高'},
        {'type': 'Type10', 'name': '二代合伙人接班与元老退出', 'stage': 2, 'row': 1, 'risk': '中高'},
        {'type': 'Type11', 'name': '并购后核心团队的去留焦虑', 'stage': 2, 'row': 2, 'risk': '中高'},
        {'type': 'Type12', 'name': '合伙人退出与竞业边界纠纷', 'stage': 2, 'row': 3, 'risk': '高'},
    ]
    
    stage_x = [1.2, 6.0, 10.8]
    card_w = 3.8
    card_h = 1.1
    start_y = 6.8
    
    for ct in conflict_types:
        x = stage_x[ct['stage']]
        y = start_y - ct['row'] * 1.6
        
        # 风险颜色
        if ct['risk'] == '高':
            risk_color = '#FFCDD2'
            risk_text = '[高] '
        elif ct['risk'] == '中高':
            risk_color = '#FFE0B2'
            risk_text = '[中高] '
        else:
            risk_color = '#FFF9C4'
            risk_text = '[中] '
        
        # 卡片底色根据阶段
        base_color = stages[ct['stage']]['color']
        
        rect = FancyBboxPatch((x, y), card_w, card_h,
                              boxstyle="round,pad=0.02,rounding_size=0.1",
                              facecolor=base_color, edgecolor=COLORS['border'],
                              linewidth=1.2, alpha=0.85)
        ax.add_patch(rect)
        
        # 风险条
        risk_rect = Rectangle((x, y + card_h - 0.25), 0.6, 0.25,
                              facecolor=risk_color, edgecolor='none',
                              alpha=0.9)
        ax.add_patch(risk_rect)
        
        # Type 编号
        ax.text(x + 0.3, y + card_h - 0.125, ct['type'], fontsize=7, 
                ha='center', va='center', fontweight='bold', color=COLORS['text_dark'])
        
        # 名称
        ax.text(x + card_w/2 + 0.3, y + card_h/2 + 0.1, ct['name'], 
                fontsize=9, ha='center', va='center', fontweight='bold',
                color=COLORS['text_dark'])
        # 风险标签
        ax.text(x + card_w/2 + 0.3, y + card_h/2 - 0.35, f"{risk_text}风险等级: {ct['risk']}", 
                fontsize=7, ha='center', va='center', color=COLORS['text_mid'])
    
    # 底部：SKU 对应路径
    ax.text(8, 0.8, 'SKU-A 风险扫描  →  SKU-B 量化诊断  →  SKU-C 调解介入', 
            fontsize=12, ha='center', fontweight='bold', color=COLORS['accent'])
    ax.plot([2, 14], [0.5, 0.5], color=COLORS['accent'], lw=2, alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('/root/.openclaw/workspace/A-manyige/项目版本/V1.6/设计资产/12类型冲突阶段分布图-V1.0.png',
                dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()
    print("12类型冲突阶段分布图已生成")


if __name__ == '__main__':
    import os
    os.makedirs('/root/.openclaw/workspace/A-manyige/项目版本/V1.6/设计资产', exist_ok=True)
    draw_totem_map()
    draw_conflict_stage_map()
    print("全部设计资产已保存到: A-manyige/项目版本/V1.6/设计资产/")
