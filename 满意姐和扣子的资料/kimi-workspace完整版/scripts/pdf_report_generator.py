#!/usr/bin/env python3
"""
PDF报告生成模块
使用 md-to-pdf 技能将Markdown报告转换为PDF
"""

import os
import subprocess
from datetime import datetime

REPORTS_DIR = "/root/.openclaw/workspace/reports/assessments"
PDF_OUTPUT_DIR = "/root/.openclaw/workspace/reports/assessments/pdf"

# 确保PDF输出目录存在
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)


def markdown_to_pdf(md_filepath: str, output_filename: str = None) -> str:
    """
    将Markdown报告转换为PDF
    
    Args:
        md_filepath: Markdown文件路径
        output_filename: 输出PDF文件名（可选）
        
    Returns:
        生成的PDF文件路径
    """
    if not os.path.exists(md_filepath):
        raise FileNotFoundError(f"Markdown文件不存在: {md_filepath}")
    
    # 生成输出文件名
    if not output_filename:
        base_name = os.path.basename(md_filepath).replace('.md', '')
        output_filename = f"{base_name}.pdf"
    
    output_path = os.path.join(PDF_OUTPUT_DIR, output_filename)
    
    # 使用 md-to-pdf 技能转换
    # 方法1: 通过系统命令调用 md-to-pdf CLI
    try:
        # 检查 md-to-pdf 是否可用
        result = subprocess.run(
            ["which", "md-to-pdf"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # 使用 md-to-pdf CLI
            cmd = [
                "md-to-pdf",
                "--input", md_filepath,
                "--output", output_path,
                "--style", "professional"
            ]
            subprocess.run(cmd, check=True)
            print(f"    PDF生成成功: {output_path}")
            return output_path
        else:
            # 降级方案：创建占位符
            print(f"    md-to-pdf CLI不可用，创建占位符...")
            return create_pdf_placeholder(md_filepath, output_path)
            
    except subprocess.CalledProcessError as e:
        print(f"    PDF生成失败: {e}")
        return create_pdf_placeholder(md_filepath, output_path)


def create_pdf_placeholder(md_filepath: str, output_path: str) -> str:
    """
    当PDF转换不可用时，创建占位符文件
    """
    placeholder_path = output_path.replace('.pdf', '.txt')
    
    with open(md_filepath, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    placeholder_content = f"""
PDF报告占位符
================

原始Markdown报告路径: {md_filepath}
目标PDF路径: {output_path}
生成时间: {datetime.now().isoformat()}

说明: md-to-pdf工具暂时不可用，请手动转换或使用以下方法:

方法1: 使用 md-to-pdf 技能
```
md-to-pdf --input {md_filepath} --output {output_path}
```

方法2: 使用在线转换工具
- https://www.markdowntopdf.com/
- 或使用 VS Code 插件 "Markdown PDF"

方法3: 直接阅读Markdown版本
Markdown报告已保存在: {md_filepath}

================================

Markdown内容预览:
{md_content[:500]}...
"""
    
    with open(placeholder_path, 'w', encoding='utf-8') as f:
        f.write(placeholder_content)
    
    print(f"    占位符已创建: {placeholder_path}")
    return placeholder_path


def batch_generate_pdf():
    """
    批量生成所有未转换的报告PDF
    """
    md_files = [f for f in os.listdir(REPORTS_DIR) if f.endswith('.md')]
    
    print(f"发现 {len(md_files)} 个Markdown报告待转换")
    
    for md_file in md_files:
        md_path = os.path.join(REPORTS_DIR, md_file)
        pdf_name = md_file.replace('.md', '.pdf')
        pdf_path = os.path.join(PDF_OUTPUT_DIR, pdf_name)
        
        # 检查PDF是否已存在
        if os.path.exists(pdf_path):
            print(f"  跳过已存在的PDF: {pdf_name}")
            continue
        
        print(f"  转换: {md_file}")
        markdown_to_pdf(md_path, pdf_name)


if __name__ == "__main__":
    # 测试PDF生成
    test_md = "/root/.openclaw/workspace/reports/assessments/assessment_recvh7az9MI8jK_20260418_131853.md"
    if os.path.exists(test_md):
        result = markdown_to_pdf(test_md)
        print(f"测试完成: {result}")
    else:
        print(f"测试文件不存在: {test_md}")
        print("运行批量转换...")
        batch_generate_pdf()
