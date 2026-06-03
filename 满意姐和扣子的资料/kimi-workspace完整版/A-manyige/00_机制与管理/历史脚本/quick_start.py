#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件格式读取工具 - 快速上手指南
运行此脚本创建测试文件并演示读取功能
"""

import os
import sys
from pathlib import Path

# 创建测试目录
test_dir = Path("./test_files")
test_dir.mkdir(exist_ok=True)

print("=" * 60)
print("  文件格式读取工具 - 快速上手")
print("=" * 60)
print()

# 1. 创建测试文本文件
print("[1] 创建测试文件...")

# UTF-8编码的文本文件
test_txt = test_dir / "test_utf8.txt"
test_txt.write_text("""这是UTF-8编码的测试文件。
这是一段中文内容。
Hello World in English.
数字: 12345
特殊字符: àáâãäåæçèéêë
""", encoding='utf-8')
print(f"  ✓ 创建: {test_txt}")

# GBK编码的文本文件
test_gbk = test_dir / "test_gbk.txt"
test_gbk.write_text("这是GBK编码的测试文件。中文内容测试。", encoding='gbk')
print(f"  ✓ 创建: {test_gbk}")

# CSV测试文件
test_csv = test_dir / "test_data.csv"
test_csv.write_text("""姓名,年龄,城市,分数
张三,25,北京,85.5
李四,30,上海,92.0
王五,28,广州,78.5
赵六,35,深圳,88.0
""", encoding='utf-8')
print(f"  ✓ 创建: {test_csv}")

print()

# 2. 演示文件读取
print("[2] 测试文件读取功能...")
print()

try:
    from file_reader import read_file, batch_read, FileReader
    
    # 测试1: 读取UTF-8文本
    print("测试1: 读取UTF-8文本文件")
    print("-" * 40)
    content = read_file(test_txt)
    print(content[:200])
    print()
    
    # 测试2: 读取GBK文本（自动检测编码）
    print("测试2: 读取GBK文本文件（自动编码检测）")
    print("-" * 40)
    content = read_file(test_gbk)
    print(content[:200])
    print()
    
    # 测试3: 读取CSV
    print("测试3: 读取CSV文件（返回结构化数据）")
    print("-" * 40)
    rows = read_file(test_csv)
    for row in rows[:3]:
        print(f"  {row}")
    print(f"  ... 共{len(rows)}行数据")
    print()
    
    # 测试4: 批量读取
    print("测试4: 批量读取目录中的所有文本文件")
    print("-" * 40)
    results = batch_read(test_dir, "*.txt")
    for filepath, content in results.items():
        filename = Path(filepath).name
        preview = str(content)[:50].replace('\n', ' ')
        print(f"  {filename}: {preview}...")
    print()
    
    print("=" * 60)
    print("  所有测试通过!")
    print("=" * 60)
    print()
    print("使用示例:")
    print()
    print("  1. 简单读取:")
    print("     from file_reader import read_file")
    print("     content = read_file('document.pdf')")
    print()
    print("  2. 读取Word文档:")
    print("     content = read_file('report.docx')")
    print()
    print("  3. 读取Excel:")
    print("     data = read_file('data.xlsx')  # 返回字典列表")
    print()
    print("  4. 批量读取:")
    print("     results = batch_read('./folder', '*.pdf')")
    print()
    print("  5. 高级用法:")
    print("     reader = FileReader()")
    print("     content = reader.read('file.pdf', pdf_engine='pymupdf')")
    print()
    
except ImportError as e:
    print(f"错误: 缺少依赖 - {e}")
    print()
    print("请先安装依赖:")
    print("  bash install_deps.sh")
    print("  或")
    print("  pip install pdfplumber PyMuPDF chardet python-docx pandas openpyxl")
    sys.exit(1)
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
