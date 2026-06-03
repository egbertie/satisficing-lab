"""
---
KIA-CODE: 知识入库代码级闭环
Asset: report_template_system.py
Status: ✅ 代码级KIA完成
Date: 2026-04-15
Batch: OM-03 Python资产25份代码级KIA-批次四

KIA-Loop:
  - 接收清点: 2026-04-15
  - 轻量提取: 2026-04-15 (代码结构识别)
  - 查重去冗: 2026-04-15 (无重复代码)
  - Tier分级: T1 (核心项目资产)
  - 深度洞察: 2026-04-15 (协作与认知系统)
  - 血液化: ✅ 完成 (五路图腾映射确认)
  - 归档锁定: 2026-04-15

功能定位:
  - 用途: 报告模板系统
  - 关联: 标准化交付
  - 维护者: 蓝军+满意姐

血液化映射:
  - 五路图腾关联: 交付物生成
  - 产品映射: 司马贺-标准化
  - 运营映射: 协作与认知优化

---
"""

#!/usr/bin/env python3
"""
报告模板系统
统一生成各类报告，减少重复写作
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace')

from defense_base_components import BaseComponent
from datetime import datetime
from typing import Dict, List, Optional, Any

class ReportTemplate(BaseComponent):
    """
    报告模板基类
    提供标准化的报告生成框架
    """
    
    def __init__(self, template_name: str):
        super().__init__(f"report_{template_name}")
        self.template_name = template_name
    
    def render_header(self, title: str, subtitle: str = "") -> str:
        """渲染报告头部"""
        lines = [
            "# " + title,
            "",
            f"> **生成时间**: {self.get_timestamp()}",
            f"> **模板**: {self.template_name}",
        ]
        if subtitle:
            lines.append(f"> **备注**: {subtitle}")
        lines.extend(["", "---", ""])
        return '\n'.join(lines)
    
    def render_table(self, headers: List[str], rows: List[List[str]]) -> str:
        """渲染Markdown表格"""
        if not rows:
            return "_无数据_\n"
        
        lines = []
        # 表头
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("|" + "|".join(["---" for _ in headers]) + "|")
        # 数据行
        for row in rows:
            lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
        lines.append("")
        return '\n'.join(lines)
    
    def render_section(self, title: str, content: str = "") -> str:
        """渲染章节"""
        lines = [f"## {title}", ""]
        if content:
            lines.append(content)
        lines.append("")
        return '\n'.join(lines)
    
    def render_checklist(self, items: List[Dict[str, Any]]) -> str:
        """渲染检查清单"""
        lines = []
        for item in items:
            status = "✅" if item.get('done') else "⏳" if item.get('in_progress') else "❌"
            priority = item.get('priority', '')
            text = item.get('text', '')
            lines.append(f"- [{status}] [{priority}] {text}")
        lines.append("")
        return '\n'.join(lines)
    
    def render_footer(self, notes: str = "") -> str:
        """渲染报告尾部"""
        lines = ["---", ""]
        if notes:
            lines.extend(["### 备注", notes, ""])
        lines.append(f"*报告生成时间: {self.get_timestamp()}*")
        return '\n'.join(lines)

class FileProcessingReport(ReportTemplate):
    """
    文件处理报告模板
    用于生成文件处理任务登记报告
    """
    
    def __init__(self):
        super().__init__("file_processing")
    
    def generate(self, data: Dict) -> str:
        """
        生成文件处理报告
        
        data格式:
        {
            'file_name': str,
            'file_path': str,
            'file_size': int,
            'paragraphs': int,
            'processing_time': str,
            'phases': List[Dict],
            'deliverables': List[Dict],
            'status': str
        }
        """
        lines = []
        
        # 头部
        lines.append(self.render_header(
            f"文件处理报告 - {data.get('file_name', 'Unknown')}",
            f"处理状态: {data.get('status', 'Unknown')}"
        ))
        
        # 文件信息
        lines.append(self.render_section("一、文件信息"))
        info_rows = [
            ["文件名", data.get('file_name', '-')],
            ["文件路径", data.get('file_path', '-')],
            ["文件大小", f"{data.get('file_size', 0):,} bytes"],
            ["段落数", str(data.get('paragraphs', 0))],
            ["处理时长", data.get('processing_time', '-')],
        ]
        lines.append(self.render_table(["项目", "详情"], info_rows))
        
        # 处理阶段
        lines.append(self.render_section("二、处理阶段"))
        phase_rows = []
        for phase in data.get('phases', []):
            phase_rows.append([
                phase.get('name', '-'),
                "✅ 完成" if phase.get('completed') else "❌ 失败",
                phase.get('notes', '-')
            ])
        lines.append(self.render_table(["阶段", "状态", "备注"], phase_rows))
        
        # 交付物
        lines.append(self.render_section("三、交付物清单"))
        deliv_rows = []
        for d in data.get('deliverables', []):
            deliv_rows.append([
                d.get('name', '-'),
                d.get('path', '-'),
                f"{d.get('size', 0):,} bytes",
                "✅" if d.get('verified') else "⏳"
            ])
        lines.append(self.render_table(["名称", "路径", "大小", "验证"], deliv_rows))
        
        # 下一步
        if data.get('next_steps'):
            lines.append(self.render_section("四、下一步行动"))
            lines.append(self.render_checklist(data['next_steps']))
        
        # 尾部
        lines.append(self.render_footer(data.get('notes', '')))
        
        return '\n'.join(lines)

class SystemDeploymentReport(ReportTemplate):
    """
    系统部署报告模板
    用于生成技术方案部署报告
    """
    
    def __init__(self):
        super().__init__("system_deployment")
    
    def generate(self, data: Dict) -> str:
        """
        生成系统部署报告
        
        data格式:
        {
            'system_name': str,
            'version': str,
            'components': List[Dict],
            'test_results': List[Dict],
            'metrics': Dict
        }
        """
        lines = []
        
        # 头部
        lines.append(self.render_header(
            f"系统部署报告 - {data.get('system_name', 'Unknown')}",
            f"版本: {data.get('version', '1.0')}"
        ))
        
        # 组件列表
        lines.append(self.render_section("一、部署组件"))
        comp_rows = []
        for comp in data.get('components', []):
            comp_rows.append([
                comp.get('name', '-'),
                comp.get('file', '-'),
                f"{comp.get('size', 0):,} bytes",
                "✅" if comp.get('deployed') else "❌",
                "✅" if comp.get('tested') else "⏳"
            ])
        lines.append(self.render_table(
            ["组件名", "文件", "大小", "部署", "测试"], 
            comp_rows
        ))
        
        # 测试结果
        lines.append(self.render_section("二、测试结果"))
        test_rows = []
        for test in data.get('test_results', []):
            test_rows.append([
                test.get('name', '-'),
                "✅ 通过" if test.get('passed') else "❌ 失败",
                test.get('details', '-')
            ])
        lines.append(self.render_table(["测试项", "结果", "详情"], test_rows))
        
        # 指标
        if data.get('metrics'):
            lines.append(self.render_section("三、关键指标"))
            metric_rows = [[k, str(v)] for k, v in data['metrics'].items()]
            lines.append(self.render_table(["指标", "数值"], metric_rows))
        
        # 尾部
        lines.append(self.render_footer())
        
        return '\n'.join(lines)

class OptimizationReport(ReportTemplate):
    """
    优化报告模板
    用于生成流程/代码优化报告
    """
    
    def __init__(self):
        super().__init__("optimization")
    
    def generate(self, data: Dict) -> str:
        """
        生成优化报告
        
        data格式:
        {
            'optimization_name': str,
            'before': Dict,
            'after': Dict,
            'improvements': List[Dict]
        }
        """
        lines = []
        
        # 头部
        lines.append(self.render_header(
            f"优化报告 - {data.get('optimization_name', 'Unknown')}"
        ))
        
        # 优化效果对比
        lines.append(self.render_section("一、优化效果"))
        
        before = data.get('before', {})
        after = data.get('after', {})
        
        comparison_rows = []
        for key in set(list(before.keys()) + list(after.keys())):
            b_val = before.get(key, '-')
            a_val = after.get(key, '-')
            # 计算改进百分比
            improvement = ""
            if isinstance(b_val, (int, float)) and isinstance(a_val, (int, float)) and b_val != 0:
                pct = (b_val - a_val) / b_val * 100
                improvement = f"节省 {pct:.0f}%"
            comparison_rows.append([key, str(b_val), str(a_val), improvement])
        
        lines.append(self.render_table(
            ["指标", "优化前", "优化后", "改进"],
            comparison_rows
        ))
        
        # 改进项
        lines.append(self.render_section("二、改进详情"))
        for i, imp in enumerate(data.get('improvements', []), 1):
            lines.append(f"### 2.{i} {imp.get('title', '改进项')}")
            lines.append("")
            lines.append(imp.get('description', ''))
            lines.append("")
            if imp.get('impact'):
                lines.append(f"**影响**: {imp['impact']}")
                lines.append("")
        
        # 固化位置
        if data.get('solidified_locations'):
            lines.append(self.render_section("三、固化位置"))
            for loc in data['solidified_locations']:
                status = "✅" if loc.get('done') else "⏳"
                lines.append(f"- {status} `{loc.get('path', '-')}` - {loc.get('description', '')}")
            lines.append("")
        
        # 尾部
        lines.append(self.render_footer())
        
        return '\n'.join(lines)

# 快捷生成函数
def quick_file_report(file_name: str, **kwargs) -> str:
    """快速生成文件处理报告"""
    template = FileProcessingReport()
    data = {
        'file_name': file_name,
        'status': '完成',
        **kwargs
    }
    return template.generate(data)

def quick_deployment_report(system_name: str, **kwargs) -> str:
    """快速生成部署报告"""
    template = SystemDeploymentReport()
    data = {
        'system_name': system_name,
        'version': '1.0',
        **kwargs
    }
    return template.generate(data)

def quick_optimization_report(name: str, **kwargs) -> str:
    """快速生成优化报告"""
    template = OptimizationReport()
    data = {
        'optimization_name': name,
        **kwargs
    }
    return template.generate(data)

if __name__ == "__main__":
    print("=" * 60)
    print("📋 报告模板系统 - 测试")
    print("=" * 60)
    
    # 测试文件处理报告
    print("\n[测试1] 文件处理报告")
    file_report = quick_file_report(
        file_name="test_file.docx",
        file_path="/test/path",
        file_size=10240,
        paragraphs=50,
        processing_time="30分钟",
        phases=[
            {'name': '前置确认', 'completed': True, 'notes': '无重复'},
            {'name': '全量提取', 'completed': True, 'notes': '50段'},
        ],
        deliverables=[
            {'name': '分析报告', 'path': '/report.md', 'size': 2048, 'verified': True}
        ]
    )
    print(file_report[:500] + "...")
    
    # 测试部署报告
    print("\n[测试2] 系统部署报告")
    deploy_report = quick_deployment_report(
        system_name="统一防御系统",
        version="3.0",
        components=[
            {'name': 'Skill条件反射V2', 'file': 'skill_conditioning_v2.py', 'size': 3788, 'deployed': True, 'tested': True}
        ],
        test_results=[
            {'name': '操作预检', 'passed': True, 'details': '3/3通过'}
        ],
        metrics={'组件数': 6, '测试通过率': '100%'}
    )
    print(deploy_report[:500] + "...")
    
    # 测试优化报告
    print("\n[测试3] 优化报告")
    opt_report = quick_optimization_report(
        name="批量重复检测",
        before={'检测次数': 36, '检测时间': '18分钟'},
        after={'检测次数': 1, '检测时间': '5秒'},
        improvements=[
            {'title': '批量检测', 'description': '一次性检测所有文件', 'impact': '节省97%时间'}
        ],
        solidified_locations=[
            {'path': 'AGENTS.md', 'description': '批量检测优化', 'done': True}
        ]
    )
    print(opt_report[:500] + "...")
    
    print("\n" + "=" * 60)
    print("✅ 报告模板系统测试完成")
    print("=" * 60)
