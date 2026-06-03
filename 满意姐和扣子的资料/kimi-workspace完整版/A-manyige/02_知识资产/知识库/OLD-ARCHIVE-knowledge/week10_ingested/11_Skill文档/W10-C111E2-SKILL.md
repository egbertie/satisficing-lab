---
# 知识元数据 (5标准化)
knowledge_id: W10-C111E2
title: Document Processor
category: 11_Skill文档
source: skills/.archive_document-processor/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 7599
week: 10
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Document Processor

> **知识ID**: W10-C111E2  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_document-processor/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: document-processor
description: Unified document processing suite - Convert documents to/from Markdown, PDF parsing with OCR, batch document conversion. Replaces markdown-converter, markdown-exporter, and mineru with integrated document workflow. Use for: PDF to Markdown, Word to Markdown, Markdown to PDF/DOCX/PPTX, document OCR, batch document conversion, academic paper parsing.
triggers: ["pdf", "markdown", "docx", "convert document", "ocr", "paper", "extract", "document"]
---

# Document Processor

**统一文档处理套件** - 一站式文档转换、PDF解析、OCR识别和格式转换解决方案。

> 🎯 替代: markdown-converter + markdown-exporter + mineru

---

## 核心能力

| 功能模块 | 覆盖场景 |
|---------|---------|
| **文档导入** | PDF/Word/PPT/Excel → Markdown |
| **文档导出** | Markdown → PDF/DOCX/PPTX/Excel/HTML |
| **PDF解析** | 学术论文、扫描件、复杂版面OCR |
| **批量处理** | 目录级文档批量转换 |
| **智能提取** | 表格、公式、图片结构化提取 |

---

## 快速开始

### 1. 文档转Markdown (Import)

```bash
# PDF转Markdown
docp import paper.pdf -o paper.md

# Word转Markdown
docp import report.docx -o report.md

# PPT转Markdown
docp import slides.pptx -o slides.md

# Excel转Markdown
docp import data.xlsx -o data.md

# 批量转换
docp import ./papers/*.pdf --output-dir ./markdown/
```

### 2. Markdown转文档 (Export)

```bash
# Markdown转PDF
docp export report.md -o report.pdf

# Markdown转Word
docp export report.md -o report.docx

# Markdown转PPT
docp export slides.md -o slides.pptx

# Markdown转Excel (表格)
docp export tables.md -o data.xlsx

# Markdown转HTML
docp export page.md -o page.html
```

### 3. PDF高级解析 (Academic OCR)

```bash
# 学术论文解析 (本地OCR)
docp parse paper.pdf -o paper.md --formula --table

# 扫描件OCR
docp parse scanned.pdf -o output.md --ocr --lang ch+en

# 提取图片
docp parse document.pdf --extract-images --output-dir ./images/

# 批量论文解析
docp parse ./papers/*.pdf --output-dir ./parsed/ --batch
```

---

## 命令详解

### `docp import` - 导入到Markdown

```bash
# 基础用法
docp import <input> [options]

Options:
  -o, --output <file>       输出文件路径
  --output-dir <dir>        批量输出目录
  --format <format>         输出格式: md, txt, json
  --extract-images          提取图片到指定目录
  --image-dir <dir>         图片输出目录
  --preserve-layout         保留原始版面结构
```

**支持格式:**

| 输入格式 | 扩展名 | 特点 |
|---------|--------|------|
| PDF | .pdf | 支持扫描件OCR |
| Word | .docx, .doc | 保留标题层级 |
| PowerPoint | .pptx, .ppt | 每页一个章节 |
| Excel | .xlsx, .xls | 表格转Markdown表格 |
| HTML | .html, .htm | 清理标签 |
| 图片 | .jpg, .png | OCR识别 |
| EPub | .epub | 电子书解析 |
| 压缩包 | .zip | 批量解压处理 |

**示例:**

```bash
# 学术论文转Markdown，提取公式
docp import paper.pdf -o paper.md --formula

# 批量转换Word文档
docp import ./docs/*.docx --output-dir ./markdown/

# 从URL获取并转换
docp import https://example.com/doc.pdf -o doc.md
```

### `docp export` - 从Markdown导出

```bash
# 基础用法
docp export <input.md> [options]

Options:
  -o, --output <file>       输出文件
  --format <format>         目标格式: pdf, docx, pptx, xlsx, html, png
  --template <file>         使用模板文件
  --theme <theme>           主题: default, academic, business
  --toc                     生成目录
  --numbered                章节编号
```

**导出格式矩阵:**

| 目标格式 | 用途 | 特殊选项 |
|---------|------|---------|
| PDF | 打印、分享 | `--page-size a4`, `--margin 2cm` |
| DOCX | 编辑、协作 | `--template template.docx` |
| PPTX | 演示 | `--slide-level 2` |
| XLSX | 表格数据 | `--sheet-per-table` |
| HTML | 网页发布 | `--css style.css`, `--standalone` |
| PNG | 图片预览 | `--dpi 300`, `--full-page` |

**示例:**

```bash
# Markdown转PDF (学术样式)
docp export thesis.md -o thesis.pdf --theme academic --toc --numbered

# Markdown转Word (使用模板)
docp export report.md -o report.docx --template company_template.docx

# Markdown转PPT
docp export presentation.md -o slides.pptx --slide-level 2

# Markdown表格转Excel
docp export tables.md -o data.xlsx --sheet-per-table

# 批量导出
docp export ./markdown/*.md --output-dir ./pdf/ --format pdf
```

### `docp parse` - PDF高级解析

```bash
# 基础用法
docp parse <input.pdf> [options]

Options:
  -o, --output <file>       输出Markdown文件
  --formula                 启用公式识别 (LaTeX输出)
  --table                   启用表格结构识别
  --ocr                     强制OCR模式 (扫描件)
  --lang <lang>             OCR语言: ch, en, ch+en, jp
  --layout-model <model>    版面分析模型: fast, accurate
  --extract-images          提取内嵌图片
  --image-dir <dir>         图片保存目录
  --batch                   批量处理模式
  --output-dir <dir>        批量输出目录
  --timeout <seconds>       单文件超时时间
```

**版面分析模型:**

| 模型 | 速度 | 准确度 | 适用场景 |
|------|------|--------|---------|
| fast | ⚡ 快 | 高 | 常规文档 |
| accurate | 🐢 慢 | 最高 | 复杂版面、学术论文 |

**示例:**

```bash
# 学术论文完整解析
docp parse paper.pdf -o paper.md --formula --table --extract-images --image-dir ./paper_images/

# 中文扫描件OCR
docp parse scan.pdf -o text.md --ocr --lang ch

# 批量论文处理
docp parse ./arxiv/*.pdf --output-dir ./parsed/ --batch --formula --table

# 仅提取表格
docp parse report.pdf --extract-tables -o tables.json
```

### `docp batch` - 批量处理工作流

```bash
# 定义处理流水线
docp batch --config workflow.yaml
```

**workflow.yaml 示例:**

```yaml
workflow:
  name: 论文处理流水线
  
input:
  pattern: "./papers/**/*.pdf"
  
steps:
  - name: parse
    action: parse
    options:
      formula: true
      table: true
      extract_images: true
      
  - name: translate
    action: translate
    target_lang: zh
    
  - name: export
    action: export
    format: docx
    template: "./templates/academic.docx"
    
output:
  dir: "./output/"
  naming: "{original}_processed"
```

---

## Python API

```python
from document_processor import DocumentProcessor

docp = DocumentProcessor()

# 导入文档
md_content = docp.import_document("paper.pdf", formula=True, table=True)
print(md_content.text)

# 导出文档
docp.export_document("report.md", "report.pdf", theme="academic", toc=True)

# PDF高级解析
result = docp.parse_pdf("scanned.pdf", ocr=True, lang="ch+en")
print(result.markdown)
print(result.tables)  # 提取的表格
print(result.images)  # 提取的图片路径

# 批量处理
results = docp.batch_process(
    pattern="./papers/*.pdf",
    action="parse",
    output_dir="./parsed/",
    options={"formula": True, "table": True}
)
```

---

## 特殊功能

### 学术论文处理

```bash
# arXiv论文一键解析
docp arxiv 2410.17247 -o paper.md --formula --table

# 从URL解析
docp import https://arxiv.org/pdf/2410.17247.pdf -o paper.md

# 生成阅读笔记模板
docp paper paper.pdf --template note --output note.md
```

### 代码块提取

```bash
# 从Markdown提取代码块到单独文件
docp extract-code input.md --output-dir ./code/

# 按语言分类
docp extract-code input.md --group-by-language --output-dir ./code/
```

### 文档对比

```bash
# 对比两个文档差异
docp diff doc1.pdf doc2.pdf -o diff.md

# 生成对比报告
docp diff version1.md version2.md --report detailed -o report.html
```

---

## 与原有Skill的兼容

| 原Skill | 原命令 | 新命令 | 状态 |
|---------|--------|--------|------|
| markdown-converter | `uvx markitdown input.pdf` | `docp import input.pdf` | ✅ 替代 |
| markdown-exporter | `md_to_pdf input.md output.pdf` | `docp export input.md -o output.pdf` | ✅ 替代 |
| markdown-exporter | `md_to_docx input.md output.docx` | `docp export input.md -o output.docx` | ✅ 替代 |
| markdown-exporter | `md_to_xlsx input.md output.xlsx` | `docp export input.md -o output.xlsx` | ✅ 替代 |
| mineru | MinerU API调用 | `docp parse input.pdf` | ✅ 替代 |

---

## 依赖安装

```bash
# 基础依赖
pip install markitdown markdown-exporter

# PDF解析依赖
pip install pdfplumber pymupdf

# OCR依赖 (可选)
pip install paddleocr paddlepaddle

# 完整依赖
pip install -r requirements.txt
```

---

## 性能对比

| 方案 | 外部API | 本地处理 | 月度成本 |
|------|--------|---------|---------|
| markdown-converter | markitdown | ✅ | 免费 |
| markdown-exporter | 部分需API | 混合 | 部分收费 |
| mineru | MinerU API | ❌ | API费用 |
| **document-processor** | **无** | **✅ 完全本地** | **完全免费** |

---

**状态**: ✅ 生产就绪
**自建替代计数**: +3 (markdown-converter, markdown-exporter, mineru)
