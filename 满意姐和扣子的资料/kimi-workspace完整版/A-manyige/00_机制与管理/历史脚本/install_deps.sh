#!/bin/bash
# 文件格式读取工具安装脚本
# 一键安装所有必要依赖

echo "=========================================="
echo "  文件格式读取工具安装脚本"
echo "=========================================="
echo ""

# 检查Python版本
echo "[1/5] 检查Python环境..."
python3 --version 2>/dev/null || python --version

if [ $? -ne 0 ]; then
    echo "错误: 未找到Python，请先安装Python 3.8或更高版本"
    exit 1
fi

# 安装核心依赖
echo ""
echo "[2/5] 安装核心依赖..."
pip install -q --upgrade pip

# P1 - 最高优先级依赖
echo "  - 安装PDF处理库 (pdfplumber, PyMuPDF)..."
pip install -q pdfplumber PyMuPDF

echo "  - 安装编码检测库 (chardet, charset-normalizer)..."
pip install -q chardet charset-normalizer

echo "  - 安装Word处理库 (python-docx, docx2txt)..."
pip install -q python-docx docx2txt

# P2 - 中期依赖
echo "  - 安装Excel处理库 (pandas, openpyxl)..."
pip install -q pandas openpyxl xlrd

# OCR - 可选依赖
echo ""
echo "[3/5] 安装OCR依赖 (可选)..."
echo "  是否安装OCR库? (用于图片文字识别)"
read -p "  输入 y 安装，其他键跳过: " install_ocr

if [ "$install_ocr" = "y" ] || [ "$install_ocr" = "Y" ]; then
    echo "  - 安装EasyOCR (开箱即用)..."
    pip install -q easyocr
    echo "  - 安装PaddleOCR (中文OCR首选)..."
    pip install -q paddleocr -i https://pypi.tuna.tsinghua.edu.cn/simple || echo "  警告: PaddleOCR安装失败"
else
    echo "  跳过OCR库安装"
fi

# 验证安装
echo ""
echo "[4/5] 验证安装..."
python3 -c "
import sys
errors = []

# 检查P1依赖
try:
    import pdfplumber
    print('  ✓ pdfplumber')
except:
    errors.append('pdfplumber')
    print('  ✗ pdfplumber')

try:
    import fitz
    print('  ✓ PyMuPDF (fitz)')
except:
    errors.append('PyMuPDF')
    print('  ✗ PyMuPDF')

try:
    import chardet
    print('  ✓ chardet')
except:
    errors.append('chardet')
    print('  ✗ chardet')

try:
    import docx
    print('  ✓ python-docx')
except:
    errors.append('python-docx')
    print('  ✗ python-docx')

try:
    import pandas
    print('  ✓ pandas')
except:
    errors.append('pandas')
    print('  ✗ pandas')

try:
    import openpyxl
    print('  ✓ openpyxl')
except:
    errors.append('openpyxl')
    print('  ✗ openpyxl')

if errors:
    print(f'\n警告: 以下包安装失败: {', '.join(errors)}')
    sys.exit(1)
else:
    print('\n所有核心依赖安装成功!')
"

if [ $? -ne 0 ]; then
    echo ""
    echo "部分依赖安装失败，请检查错误信息"
    exit 1
fi

# 测试file_reader.py
echo ""
echo "[5/5] 测试file_reader.py..."
python3 file_reader.py 2>/dev/null

echo ""
echo "=========================================="
echo "  安装完成!"
echo "=========================================="
echo ""
echo "使用方法:"
echo "  1. 作为模块导入:"
echo "     from file_reader import read_file"
echo "     content = read_file('document.pdf')"
echo ""
echo "  2. 命令行使用:"
echo "     python file_reader.py <文件路径>"
echo ""
echo "  3. 批量读取:"
echo "     python -c \"from file_reader import batch_read; batch_read('./docs', '*.pdf')\""
echo ""
echo "支持的格式:"
echo "  - PDF (.pdf)"
echo "  - Word (.docx)"
echo "  - Excel (.xlsx, .xls)"
echo "  - CSV (.csv)"
echo "  - 文本 (.txt, .md, .json, etc.)"
echo ""
