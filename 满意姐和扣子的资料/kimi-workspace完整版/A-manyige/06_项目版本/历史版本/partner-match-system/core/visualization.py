"""
可视化模块 - 将抽象数据转化为可感知的视觉体验
参考：Bret Victor的"Seeing the invisible"理念
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, FancyBboxPatch
import numpy as np
from typing import Dict, List, Tuple
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class AttractorLandscapeVisualizer:
    """
    吸引子景观可视化
    展示两人协作系统的动力学景观
    """
    
    def __init__(self, figsize=(12, 10)):
        self.figsize = figsize
        
    def visualize(self, collaboration_data: Dict, save_path: str = None):
        """
        绘制吸引子景观
        
        Args:
            collaboration_data: 包含协作模式分布的字典
            save_path: 保存路径
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # 创建地形网格
        x = np.linspace(-5, 5, 100)
        y = np.linspace(-5, 5, 100)
        X, Y = np.meshgrid(x, y)
        
        # 基于协作模式生成地形高度
        Z = self._generate_landscape(X, Y, collaboration_data)
        
        # 绘制等高线
        levels = np.linspace(Z.min(), Z.max(), 20)
        contour = ax.contourf(X, Y, Z, levels=levels, cmap='viridis', alpha=0.7)
        ax.contour(X, Y, Z, levels=levels, colors='white', alpha=0.3, linewidths=0.5)
        
        # 标记吸引子位置
        attractors = self._calculate_attractors(collaboration_data)
        for i, (attractor, strength) in enumerate(attractors):
            x_pos = np.random.uniform(-3, 3)
            y_pos = np.random.uniform(-3, 3)
            size = 200 + strength * 500
            
            circle = Circle((x_pos, y_pos), 0.3, color='#ff6b6b', alpha=0.8, zorder=5)
            ax.add_patch(circle)
            
            ax.annotate(attractor, (x_pos, y_pos), 
                       fontsize=10, ha='center', va='center',
                       color='white', fontweight='bold')
        
        # 添加系统轨迹
        self._draw_trajectory(ax, collaboration_data)
        
        ax.set_xlim(-5, 5)
        ax.set_ylim(-5, 5)
        ax.set_aspect('equal')
        ax.axis('off')
        
        plt.colorbar(contour, ax=ax, label='系统稳定性')
        plt.title('Attractor Landscape: 协作系统动力学景观', fontsize=16, fontweight='bold', pad=20)
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='black')
        
        return fig
    
    def _generate_landscape(self, X, Y, data):
        """生成景观高度"""
        Z = np.zeros_like(X)
        
        # 添加多个高斯峰代表不同吸引子
        peaks = [
            ((-2, -2), 2, 1.5),   # 同步吸引子
            ((2, 2), 2.5, 1),      # 互补吸引子
            ((0, -3), 1.8, 0.8),   # 创造吸引子
        ]
        
        for (x0, y0), height, width in peaks:
            Z += height * np.exp(-((X - x0)**2 + (Y - y0)**2) / (2 * width**2))
        
        # 添加噪声模拟复杂性
        Z += 0.2 * np.random.random(Z.shape)
        
        return Z
    
    def _calculate_attractors(self, data):
        """计算吸引子位置"""
        modes = data.get('collaboration_pattern', {})
        total = sum(modes.values())
        return [(mode, count/total) for mode, count in modes.items()]
    
    def _draw_trajectory(self, ax, data):
        """绘制系统演化轨迹"""
        t = np.linspace(0, 4*np.pi, 200)
        x = 3 * np.cos(t) * np.exp(-t/10)
        y = 2 * np.sin(t) * np.exp(-t/10)
        ax.plot(x, y, 'w-', linewidth=2, alpha=0.6, label='系统轨迹')
        ax.scatter(x[-1], y[-1], c='red', s=100, marker='*', zorder=10)


class CognitiveDiversityMap:
    """
    认知多样性图谱
    艺术化展示两人的"思维舞蹈"
    """
    
    def __init__(self):
        self.colors = {
            'partner_a': '#8b5cf6',  # 紫色
            'partner_b': '#06b6d4',  # 青色
            'overlap': '#ffffff'     # 白色
        }
    
    def create_radial_chart(self, style_a, style_b, names=('Partner A', 'Partner B')):
        """
        创建径向认知图谱
        """
        categories = ['分析型', '直觉型', '细节导向', '全局导向', 
                     '风险容忍', '风险规避', '独立型', '依存型']
        
        # 数据转换
        values_a = [
            style_a.analytical, 1-style_a.intuitive,
            style_a.detail_oriented, 1-style_a.detail_oriented,
            style_a.risk_tolerance, 1-style_a.risk_tolerance,
            style_a.independent, 1-style_a.independent
        ]
        
        values_b = [
            style_b.analytical, 1-style_b.intuitive,
            style_b.detail_oriented, 1-style_b.detail_oriented,
            style_b.risk_tolerance, 1-style_b.risk_tolerance,
            style_b.independent, 1-style_b.independent
        ]
        
        # 使用Plotly创建交互式雷达图
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values_a + [values_a[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(139, 92, 246, 0.3)',
            line=dict(color=self.colors['partner_a'], width=2),
            name=names[0]
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=values_b + [values_b[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(6, 182, 212, 0.3)',
            line=dict(color=self.colors['partner_b'], width=2),
            name=names[1]
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1]),
                bgcolor='rgba(0,0,0,0.1)'
            ),
            showlegend=True,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title='认知风格图谱 - 思维舞蹈'
        )
        
        return fig
    
    def create_dance_visualization(self, style_a, style_b, n_frames=50):
        """
        创建"思维舞蹈"动画概念图
        展示两人在思考空间中的动态交互
        """
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # 创建思考空间网格
        x = np.linspace(0, 10, n_frames)
        y = np.linspace(0, 10, n_frames)
        
        # Partner A 的轨迹（分析型 - 规律）
        t = np.linspace(0, 4*np.pi, n_frames)
        traj_a_x = 5 + 3 * np.cos(t * 0.5) + 0.5 * np.sin(t * 3)
        traj_a_y = 5 + 2 * np.sin(t * 0.5) + 0.3 * np.cos(t * 2)
        
        # Partner B 的轨迹（直觉型 - 跳跃）
        traj_b_x = 5 + 2 * np.cos(t * 0.8 + 1) + np.random.normal(0, 0.3, n_frames)
        traj_b_y = 5 + 3 * np.sin(t * 0.6) + np.random.normal(0, 0.3, n_frames)
        
        # 绘制轨迹
        ax.plot(traj_a_x, traj_a_y, color=self.colors['partner_a'], 
               linewidth=2, alpha=0.6, label='Partner A')
        ax.plot(traj_b_x, traj_b_y, color=self.colors['partner_b'], 
               linewidth=2, alpha=0.6, label='Partner B')
        
        # 绘制位置点
        ax.scatter(traj_a_x[-1], traj_a_y[-1], s=200, c=self.colors['partner_a'], 
                  marker='o', edgecolors='white', linewidths=2, zorder=5)
        ax.scatter(traj_b_x[-1], traj_b_y[-1], s=200, c=self.colors['partner_b'], 
                  marker='s', edgecolors='white', linewidths=2, zorder=5)
        
        # 绘制连接两人的"认知张力"线
        for i in range(0, n_frames, 5):
            alpha = 0.1 + 0.3 * (i / n_frames)
            ax.plot([traj_a_x[i], traj_b_x[i]], [traj_a_y[i], traj_b_y[i]], 
                   'w--', alpha=alpha, linewidth=0.5)
        
        # 添加当前距离标注
        distance = np.sqrt((traj_a_x[-1] - traj_b_x[-1])**2 + 
                          (traj_a_y[-1] - traj_b_y[-1])**2)
        
        ax.annotate(f'认知距离: {distance:.2f}', 
                   xy=((traj_a_x[-1] + traj_b_x[-1])/2, (traj_a_y[-1] + traj_b_y[-1])/2),
                   fontsize=10, color='white', ha='center',
                   bbox=dict(boxstyle='round', facecolor='black', alpha=0.5))
        
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_aspect('equal')
        ax.set_facecolor('#1a1a2e')
        ax.legend(loc='upper right', facecolor='black', edgecolor='white')
        ax.set_title('思维舞蹈: 认知空间中的动态交互', fontsize=14, color='white', pad=20)
        
        plt.tight_layout()
        return fig


class FutureEvolutionSimulator:
    """
    未来演化模拟器可视化
    """
    
    def create_evolution_timeline(self, predictions: Dict):
        """
        创建演化时间线
        """
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.6, 0.4],
            subplot_titles=('合作成功概率演化', '关键事件预测'),
            vertical_spacing=0.15
        )
        
        # 时间点和概率
        time_points = ['当前', '6个月', '1年', '3年', '5年']
        probabilities = [0.5, 
                        predictions['6_months']['success_probability'],
                        predictions['1_year']['success_probability'],
                        predictions['3_years']['success_probability'],
                        predictions['3_years']['success_probability'] * 0.9]  # 5年略有下降
        
        # 绘制概率曲线
        fig.add_trace(
            go.Scatter(
                x=time_points,
                y=[p * 100 for p in probabilities],
                mode='lines+markers',
                line=dict(color='#8b5cf6', width=3),
                marker=dict(size=12, color='#06b6d4', symbol='diamond'),
                fill='tozeroy',
                fillcolor='rgba(139, 92, 246, 0.2)',
                name='成功概率'
            ),
            row=1, col=1
        )
        
        # 添加置信区间
        upper = [min(100, p * 100 + 10) for p in probabilities]
        lower = [max(0, p * 100 - 10) for p in probabilities]
        
        fig.add_trace(
            go.Scatter(
                x=time_points + time_points[::-1],
                y=upper + lower[::-1],
                fill='toself',
                fillcolor='rgba(139, 92, 246, 0.1)',
                line=dict(color='rgba(0,0,0,0)'),
                name='置信区间',
                showlegend=False
            ),
            row=1, col=1
        )
        
        # 添加关键事件标注
        events = [
            predictions['6_months']['key_challenge'],
            predictions['1_year']['key_challenge'],
            predictions['3_years']['key_challenge']
        ]
        
        fig.add_trace(
            go.Bar(
                x=['6个月', '1年', '3年'],
                y=[1, 2, 3],
                text=events,
                textposition='outside',
                marker_color=['#10b981', '#f59e0b', '#8b5cf6'],
                showlegend=False
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title='未来演化路径模拟',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=600
        )
        
        fig.update_yaxes(title_text='成功率 (%)', row=1, col=1, range=[0, 100])
        fig.update_xaxes(title_text='时间', row=2, col=1)
        
        return fig


class QuantumStateVisualizer:
    """
    量子态可视化
    将抽象的波函数转化为直观的视觉
    """
    
    def visualize_wavefunction(self, wavefunction, title='量子态可视化'):
        """
        可视化波函数
        """
        states = list(wavefunction.amplitudes.keys())
        amplitudes = list(wavefunction.amplitudes.values())
        probabilities = [abs(a)**2 for a in amplitudes]
        phases = [np.angle(a) for a in amplitudes]
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # 概率柱状图
        ax1 = axes[0]
        bars = ax1.bar(states, probabilities, color='#8b5cf6', alpha=0.7, edgecolor='white')
        ax1.set_ylabel('概率', fontsize=12)
        ax1.set_title('测量概率分布', fontsize=12)
        ax1.set_ylim(0, 1)
        for bar, prob in zip(bars, probabilities):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{prob:.1%}', ha='center', va='bottom', color='white')
        
        # 相位轮
        ax2 = axes[1]
        ax2.set_xlim(-1.5, 1.5)
        ax2.set_ylim(-1.5, 1.5)
        ax2.set_aspect('equal')
        ax2.set_title('相位分布', fontsize=12)
        
        for i, (state, phase) in enumerate(zip(states, phases)):
            x = 0.8 * np.cos(phase)
            y = 0.8 * np.sin(phase)
            ax2.arrow(0, 0, x, y, head_width=0.05, head_length=0.05, 
                     fc=plt.cm.hsv(i/len(states)), ec='white', alpha=0.8)
            ax2.text(x * 1.2, y * 1.2, state, ha='center', va='center', 
                    color='white', fontsize=9)
        
        circle = plt.Circle((0, 0), 1, fill=False, color='white', alpha=0.3)
        ax2.add_patch(circle)
        ax2.axis('off')
        
        # 叠加态表示
        ax3 = axes[2]
        ax3.set_xlim(0, 10)
        ax3.set_ylim(0, len(states))
        
        for i, (state, amp) in enumerate(zip(states, amplitudes)):
            # 绘制概率幅的实部和虚部
            real, imag = amp.real, amp.imag
            
            # 实部
            ax3.barh(i, abs(real) * 5, left=1, 
                    color='#06b6d4' if real > 0 else '#ef4444', alpha=0.7)
            # 虚部
            ax3.barh(i + 0.3, abs(imag) * 5, left=1, 
                    color='#10b981' if imag > 0 else '#f59e0b', alpha=0.7)
            
            ax3.text(0.5, i + 0.15, state, ha='center', va='center', 
                    color='white', fontsize=10)
        
        ax3.set_yticks([])
        ax3.set_title('复数概率幅 (实部:青/红, 虚部:绿/黄)', fontsize=12)
        
        plt.suptitle(title, fontsize=14, fontweight='bold', color='white')
        plt.tight_layout()
        
        return fig


def generate_full_report_visualization(match_result: Dict, save_dir: str = './outputs'):
    """
    生成完整的可视化报告
    """
    import os
    os.makedirs(save_dir, exist_ok=True)
    
    visualizations = []
    
    # 1. 吸引子景观
    attractor_viz = AttractorLandscapeVisualizer()
    fig = attractor_viz.visualize(
        match_result['layer_results']['emergent_matching'],
        save_path=f'{save_dir}/01_attractor_landscape.png'
    )
    visualizations.append('01_attractor_landscape.png')
    
    # 2. 认知多样性图谱
    diversity_viz = CognitiveDiversityMap()
    style_a = match_result['layer_results']['cognitive_diversity']['style_a']
    style_b = match_result['layer_results']['cognitive_diversity']['style_b']
    fig = diversity_viz.create_dance_visualization(style_a, style_b)
    plt.savefig(f'{save_dir}/02_cognitive_dance.png', dpi=150, 
               bbox_inches='tight', facecolor='#1a1a2e')
    visualizations.append('02_cognitive_dance.png')
    
    # 3. 未来演化
    evolution_viz = FutureEvolutionSimulator()
    fig = evolution_viz.create_evolution_timeline(match_result['predictions'])
    fig.write_html(f'{save_dir}/03_future_evolution.html')
    visualizations.append('03_future_evolution.html')
    
    return visualizations


if __name__ == '__main__':
    # 演示可视化
    print("Entanglement Visualization Module")
    print("可视化模块演示")
    
    # 创建示例数据
    example_data = {
        'collaboration_pattern': {
            'synchronization': 25,
            'complementary': 35,
            'conflict': 15,
            'generative': 25
        }
    }
    
    # 生成吸引子景观
    viz = AttractorLandscapeVisualizer()
    viz.visualize(example_data, save_path='attractor_demo.png')
    print("✓ 吸引子景观已生成: attractor_demo.png")
