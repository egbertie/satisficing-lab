#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五路图腾信息图 SVG 生成器
生成环形五行图腾可视化图
"""

import math

# SVG 配置
WIDTH = 1200
HEIGHT = 1200
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2

# 颜色配置
COLORS = {
    'earth': {'fill': '#D4A574', 'stroke': '#8B4513', 'text': '#3E2723'},   # 土 - LIU
    'metal': {'fill': '#E8E8E8', 'stroke': '#B8860B', 'text': '#212121'},   # 金 - SIMON
    'water': {'fill': '#87CEEB', 'stroke': '#4682B4', 'text': '#0D47A1'},   # 水 - GUANYIN
    'wood': {'fill': '#90EE90', 'stroke': '#228B22', 'text': '#1B5E20'},    # 木 - CONFUCIUS
    'fire': {'fill': '#FF6B6B', 'stroke': '#DC143C', 'text': '#B71C1C'},    # 火 - HUINENG
    'center': {'fill': '#FFF8DC', 'stroke': '#DAA520', 'text': '#4A3728'},  # 中心
}

# 图腾数据
TOTEMS = [
    {
        'name': 'LIU',
        'chinese': '刘禹锡',
        'element': '土',
        'element_en': 'Earth',
        'spirit': '惟吾德馨',
        'icon': '🏛️',
        'color': 'earth',
        'angle': 270,  # 顶部
    },
    {
        'name': 'SIMON',
        'chinese': '赫伯特·西蒙',
        'element': '金',
        'element_en': 'Metal',
        'spirit': '满意解',
        'icon': '⚖️',
        'color': 'metal',
        'angle': 342,  # 右上
    },
    {
        'name': 'GUANYIN',
        'chinese': '观自在菩萨',
        'element': '水',
        'element_en': 'Water',
        'spirit': '自在从容',
        'icon': '🪷',
        'color': 'water',
        'angle': 54,   # 右下
    },
    {
        'name': 'CONFUCIUS',
        'chinese': '孔子',
        'element': '木',
        'element_en': 'Wood',
        'spirit': '仁者爱人',
        'icon': '🎋',
        'color': 'wood',
        'angle': 126,  # 左下
    },
    {
        'name': 'HUINENG',
        'chinese': '六祖慧能',
        'element': '火',
        'element_en': 'Fire',
        'spirit': '顿悟/知行合一',
        'icon': '🔥',
        'color': 'fire',
        'angle': 198,  # 左上
    },
]

def polar_to_cartesian(cx, cy, radius, angle_deg):
    """极坐标转笛卡尔坐标"""
    angle_rad = math.radians(angle_deg)
    x = cx + radius * math.cos(angle_rad)
    y = cy + radius * math.sin(angle_rad)
    return x, y

def create_rounded_rect(x, y, width, height, radius, fill, stroke, stroke_width=3):
    """创建圆角矩形"""
    return f'''<rect x="{x}" y="{y}" width="{width}" height="{height}" 
        rx="{radius}" ry="{radius}" 
        fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'''

def create_text(x, y, text, fill, font_size=14, font_weight="normal", text_anchor="middle"):
    """创建文本"""
    return f'''<text x="{x}" y="{y}" fill="{fill}" font-size="{font_size}" 
        font-weight="{font_weight}" text-anchor="{text_anchor}" font-family="Arial, sans-serif">{text}</text>'''

def create_circle(cx, cy, r, fill, stroke, stroke_width=3):
    """创建圆形"""
    return f'''<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'''

def create_line(x1, y1, x2, y2, stroke, stroke_width=2, dasharray=None):
    """创建线条"""
    dash = f' stroke-dasharray="{dasharray}"' if dasharray else ''
    return f'''<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{stroke_width}"{dash}/>'''

def create_arrow(x1, y1, x2, y2, stroke, stroke_width=3):
    """创建带箭头的线条"""
    marker_id = f"arrow_{stroke.replace('#', '')}"
    return f'''<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{stroke_width}" marker-end="url(#{marker_id})"/>'''

def generate_svg():
    """生成完整的SVG"""
    
    # SVG 头部
    svg_parts = [
        f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
<defs>
    <!-- 箭头标记定义 -->
    <marker id="arrow_D4A574" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
        <path d="M0,0 L0,6 L9,3 z" fill="#D4A574"/>
    </marker>
    <marker id="arrow_B8860B" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
        <path d="M0,0 L0,6 L9,3 z" fill="#B8860B"/>
    </marker>
    <marker id="arrow_4682B4" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
        <path d="M0,0 L0,6 L9,3 z" fill="#4682B4"/>
    </marker>
    <marker id="arrow_228B22" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
        <path d="M0,0 L0,6 L9,3 z" fill="#228B22"/>
    </marker>
    <marker id="arrow_DC143C" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
        <path d="M0,0 L0,6 L9,3 z" fill="#DC143C"/>
    </marker>
    <!-- 阴影滤镜 -->
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
        <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.3"/>
    </filter>
</defs>
'''
    ]
    
    # 背景
    svg_parts.append(f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#FAFAFA"/>')
    
    # 标题
    svg_parts.append(create_text(CENTER_X, 50, "五路图腾体系 V2.4", "#333", font_size=28, font_weight="bold"))
    svg_parts.append(create_text(CENTER_X, 80, "Five Totems System · 五行相生", "#666", font_size=16))
    
    # 绘制五行相生循环箭头（外圈）
    outer_radius = 380
    arrow_angles = [270, 342, 54, 126, 198]
    arrow_colors = ['#D4A574', '#B8860B', '#4682B4', '#228B22', '#DC143C']
    
    for i in range(5):
        start_angle = arrow_angles[i]
        end_angle = arrow_angles[(i + 1) % 5]
        
        # 计算箭头起点和终点
        x1, y1 = polar_to_cartesian(CENTER_X, CENTER_Y, outer_radius, start_angle + 15)
        x2, y2 = polar_to_cartesian(CENTER_X, CENTER_Y, outer_radius, end_angle - 15)
        
        # 绘制弧形箭头路径
        svg_parts.append(f'<path d="M {x1} {y1} A {outer_radius} {outer_radius} 0 0 1 {x2} {y2}" fill="none" stroke="{arrow_colors[i]}" stroke-width="4" marker-end="url(#arrow_{arrow_colors[i].replace("#", "")})"/>')
    
    # 绘制图腾节点
    node_radius = 320
    node_width = 180
    node_height = 200
    
    for i, totem in enumerate(TOTEMS):
        angle = totem['angle']
        cx, cy = polar_to_cartesian(CENTER_X, CENTER_Y, node_radius, angle)
        
        # 节点左上角坐标
        x = cx - node_width / 2
        y = cy - node_height / 2
        
        color = COLORS[totem['color']]
        
        # 节点阴影背景
        svg_parts.append(create_rounded_rect(x+3, y+3, node_width, node_height, 15, 
            "rgba(0,0,0,0.1)", "none", 0))
        
        # 节点主体
        svg_parts.append(create_rounded_rect(x, y, node_width, node_height, 15, 
            color['fill'], color['stroke'], 3))
        
        # 图标
        svg_parts.append(create_text(cx, y + 35, totem['icon'], color['text'], font_size=32))
        
        # 英文名
        svg_parts.append(create_text(cx, y + 65, totem['name'], color['text'], font_size=16, font_weight="bold"))
        
        # 中文名
        svg_parts.append(create_text(cx, y + 85, totem['chinese'], color['text'], font_size=12))
        
        # 分隔线
        svg_parts.append(f'<line x1="{x + 20}" y1="{y + 100}" x2="{x + node_width - 20}" y2="{y + 100}" stroke="{color["stroke"]}" stroke-width="2"/>')
        
        # 五行标志
        element_colors = {'土': '🟫', '金': '⬜', '水': '🔵', '木': '🟢', '火': '🔴'}
        element_text = f"{element_colors[totem['element']]} {totem['element']} · {totem['element_en']}"
        svg_parts.append(create_text(cx, y + 125, element_text, color['text'], font_size=12, font_weight="bold"))
        
        # 分隔线2
        svg_parts.append(f'<line x1="{x + 20}" y1="{y + 140}" x2="{x + node_width - 20}" y2="{y + 140}" stroke="{color["stroke"]}" stroke-width="1"/>')
        
        # 核心精神
        svg_parts.append(create_text(cx, y + 165, totem['spirit'], color['text'], font_size=14, font_weight="bold"))
    
    # 绘制中心圆
    center_radius = 100
    center_color = COLORS['center']
    
    # 中心圆阴影
    svg_parts.append(create_circle(CENTER_X + 3, CENTER_Y + 3, center_radius, 
        "rgba(0,0,0,0.1)", "none", 0))
    
    # 中心圆主体
    svg_parts.append(create_circle(CENTER_X, CENTER_Y, center_radius, 
        center_color['fill'], center_color['stroke'], 4))
    
    # 中心文字
    svg_parts.append(create_text(CENTER_X, CENTER_Y - 25, "⭕", center_color['text'], font_size=24))
    svg_parts.append(create_text(CENTER_X, CENTER_Y + 5, "五路图腾", center_color['text'], font_size=18, font_weight="bold"))
    svg_parts.append(create_text(CENTER_X, CENTER_Y + 28, "WU LU", center_color['text'], font_size=10))
    svg_parts.append(create_text(CENTER_X, CENTER_Y + 45, "TOTEMS", center_color['text'], font_size=10))
    svg_parts.append(create_text(CENTER_X, CENTER_Y + 70, "五行相生·生生不息", center_color['text'], font_size=11))
    
    # 绘制中心到各节点的连接线
    for totem in TOTEMS:
        angle = totem['angle']
        node_x, node_y = polar_to_cartesian(CENTER_X, CENTER_Y, node_radius - node_height/2, angle)
        center_edge_x, center_edge_y = polar_to_cartesian(CENTER_X, CENTER_Y, center_radius, angle)
        
        color = COLORS[totem['color']]
        svg_parts.append(create_line(center_edge_x, center_edge_y, node_x, node_y, 
            color['stroke'], 2, "5,5"))
    
    # 添加五行相生标签
    label_radius = 450
    labels = ["土生金", "金生水", "水生木", "木生火", "火生土"]
    for i, (angle, label) in enumerate(zip([306, 18, 90, 162, 234], labels)):
        lx, ly = polar_to_cartesian(CENTER_X, CENTER_Y, label_radius, angle)
        bg_color = arrow_colors[i]
        # 标签背景
        svg_parts.append(f'<circle cx="{lx}" cy="{ly}" r="28" fill="{bg_color}" stroke="white" stroke-width="2"/>')
        # 标签文字
        svg_parts.append(create_text(lx, ly + 5, label, "white", font_size=11, font_weight="bold"))
    
    # 添加图例
    legend_x = 50
    legend_y = HEIGHT - 200
    
    svg_parts.append(create_rounded_rect(legend_x, legend_y, 300, 180, 10, 
        "white", "#ddd", 2))
    svg_parts.append(create_text(legend_x + 150, legend_y + 25, "📜 五行相生原理", "#333", font_size=14, font_weight="bold"))
    
    legend_items = [
        ("🟫 → ⬜", "土生金: 大地孕育矿藏，品德孕育智慧"),
        ("⬜ → 🔵", "金生水: 金凝水露，理性滋养感性"),
        ("🔵 → 🟢", "水生木: 水润草木，智慧滋养仁爱"),
        ("🟢 → 🔴", "木生火: 木燃生火，仁爱激发顿悟"),
        ("🔴 → 🟫", "火生土: 火烬归土，智慧回归品德"),
    ]
    
    for i, (symbol, desc) in enumerate(legend_items):
        svg_parts.append(create_text(legend_x + 20, legend_y + 55 + i * 25, symbol, "#333", font_size=12, text_anchor="start"))
        svg_parts.append(create_text(legend_x + 70, legend_y + 55 + i * 25, desc, "#666", font_size=10, text_anchor="start"))
    
    # 版本信息
    svg_parts.append(create_text(WIDTH - 50, HEIGHT - 30, "版本: V2.4 | 2026-03-13", "#999", font_size=10, text_anchor="end"))
    
    # SVG 结束
    svg_parts.append('</svg>')
    
    return '\n'.join(svg_parts)

if __name__ == '__main__':
    svg_content = generate_svg()
    with open('五路图腾信息图.svg', 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print("SVG 文件已生成: 五路图腾信息图.svg")
