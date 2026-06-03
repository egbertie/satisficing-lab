# 📄 文件格式读取工具包

快速、稳定的PDF、Word、Excel、文本文件读取解决方案，自动处理中文编码问题。

## ✨ 特性

- 🔥 **统一接口** - 一行代码读取多种格式
- 🔍 **自动编码检测** - 智能识别GBK/UTF-8等编码，告别乱码
- 📊 **多格式支持** - PDF, DOCX, XLSX, CSV, TXT
- 🚀 **高性能** - 支持大文件流式读取
- 📝 **结构保留** - 表格数据自动转为结构化格式
- 🛡️ **错误处理** - 优雅处理损坏文件和编码错误

## 🚀 快速开始

### 1. 安装依赖

```bash
bash install_deps.sh
```

或手动安装：

```bash
pip install pdfplumber PyMuPDF chardet python-docx pandas openpyxl
```

### 2. 运行测试

```bash
python quick_start.py
```

### 3. 开始使用

```python
from file_reader import read_file, batch_read

# 读取PDF
content = read_file("document.pdf")

# 读取Word
content = read_file("report.docx")

# 读取Excel（返回字典列表）
data = read_file("data.xlsx")

# 批量读取
results = batch_read("./docs", "*.pdf")
```

## 📖 使用示例

### 基础用法

```python
from file_reader import read_file

# 读取PDF - 自动使用最佳引擎
content = read_file("file.pdf")

# 读取PDF - 指定引擎（可选: 'pdfplumber', 'pymupdf'）
content = read_file("file.pdf", pdf_engine="pymupdf")

# 读取Word文档
content = read_file("file.docx")

# 读取文本文件 - 自动检测编码
content = read_file("file.txt")

# 读取Excel - 返回结构化数据
data = read_file("file.xlsx")
```

### 高级用法

```python
from file_reader import FileReader

# 创建自定义读取器
reader = FileReader(
    encoding_fallbacks=['utf-8', 'gbk', 'gb18030']
)

# 读取PDF指定页数
content = reader.read("document.pdf", max_pages=10)

# 读取Excel指定Sheet
content = reader.read("data.xlsx", sheet_name="Sheet1")
```

### 批量处理

```python
from file_reader import batch_read

# 批量读取目录中所有PDF
results = batch_read("./documents", "*.pdf")

# 递归读取子目录
results = batch_read("./data", "*.txt", recursive=True)

# 处理结果
for filepath, content in results.items():
    print(f"{filepath}: {len(str(content))} 字符")
```

## 📂 文件结构

```
workspace/
├── file_reader.py          # 核心读取工具
├── install_deps.sh         # 依赖安装脚本
├── quick_start.py          # 快速上手指南
├── test_advanced.py        # 高级功能测试
├── docs/
│   └── 文件格式读取技术研究报告.md
└── test_files/             # 测试文件目录
    ├── test_utf8.txt
    ├── test_gbk.txt
    ├── test_data.csv
    └── test_document.docx
```

## 📊 技术方案对比

### PDF读取

| 引擎 | 速度 | 表格提取 | 推荐使用场景 |
|------|------|----------|--------------|
| pdfplumber | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 首选，表格提取能力强 |
| PyMuPDF | ⭐⭐⭐⭐⭐ | ⭐⭐ | 大文件、高性能场景 |

### 文本编码检测

| 方案 | 准确率 | 推荐使用场景 |
|------|--------|--------------|
| chardet | ⭐⭐⭐⭐ | 通用场景 |
| charset-normalizer | ⭐⭐⭐⭐⭐ | 需要更高准确性 |
| 多编码尝试 | ⭐⭐⭐ | 已知编码范围 |

### Word读取

| 库 | 功能 | 推荐使用场景 |
|----|----|----|
| python-docx | ⭐⭐⭐⭐⭐ | 首选，功能完整 |
| docx2txt | ⭐⭐⭐ | 纯文本提取 |

## 🔧 命令行使用

```bash
# 读取单个文件
python file_reader.py document.pdf

# 查看帮助
python file_reader.py
```

## ⚠️ 常见问题

### Q: 读取中文PDF出现乱码？

A: 工具会自动处理编码，如仍有问题，尝试指定引擎：

```python
content = read_file("file.pdf", pdf_engine="pymupdf")
```

### Q: 大PDF文件内存溢出？

A: 使用`max_pages`参数分批读取：

```python
content = read_file("large.pdf", max_pages=100)
```

### Q: Excel文件读取失败？

A: 确保安装openpyxl：

```bash
pip install openpyxl
```

## 📝 依赖清单

### 核心依赖（必须）

- `pdfplumber` - PDF读取（推荐）
- `PyMuPDF` - PDF高性能读取
- `chardet` - 编码自动检测
- `python-docx` - Word文档读取
- `pandas` - Excel数据处理
- `openpyxl` - Excel文件读取

### 可选依赖

- `easyocr` - 图片OCR
- `paddleocr` - 中文OCR（推荐）

## 📈 性能建议

1. **大文件处理**: 使用`read_only=True`模式
2. **批量处理**: 使用`batch_read`函数
3. **内存优化**: 使用生成器/yield处理大文件
4. **编码检测**: 对于已知编码，直接指定避免检测开销

## 🔒 错误处理

工具已内置完善的错误处理：

- 文件不存在 → `FileReaderError`
- 编码检测失败 → 使用备用编码列表
- 文件损坏 → 记录日志并跳过
- 依赖缺失 → 清晰的安装提示

## 📄 许可

MIT License

## 🤝 贡献

欢迎提交Issue和PR！

---

**创建日期**: 2026-03-13  
**版本**: v1.0
