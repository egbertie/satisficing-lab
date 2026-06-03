---
# 知识元数据 (5标准化)
knowledge_id: W15-E3FAC5
title: 文件处理快速参考
category: 11_Skill文档
source: skills/file-handler-universal/QUICK_REF.md
ingested_at: 2026-03-27 17:59:30
word_count: 1171
week: 15
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 文件处理快速参考

> **知识ID**: W15-E3FAC5  
> **分类**: 11_Skill文档  
> **来源**: `skills/file-handler-universal/QUICK_REF.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 文件处理快速参考

## 一句话指令

| 你想做 | 指令 |
|--------|------|
| 读取DOCX | `python3 skills/file-handler-universal/file_handler.py read file.docx` |
| 读取PDF | `python3 skills/file-handler-universal/file_handler.py read file.pdf` |
| DOCX转MD | `pandoc file.docx -o file.md` |
| MD转DOCX | `pandoc file.md -o file.docx` |
| 上传飞书 | `python3 skills/file-handler-universal/file_handler.py upload file.pdf` |

## Python快速代码

```python
# 读取任何文件
from skills.file-handler-universal.file_handler import FileHandler
handler = FileHandler()
text = handler.read_file("document.docx")

# 读取PDF
from pypdf import PdfReader
reader = PdfReader("file.pdf")
text = "\n".join([p.extract_text() for p in reader.pages])

# DOCX转Markdown
import subprocess
result = subprocess.run(['pandoc', 'file.docx', '-t', 'markdown'], capture_output=True, text=True)
print(result.stdout)
```

## 支持的文件类型

✅ **完全支持**: .md, .txt, .docx, .pdf, .xlsx, .csv, .png, .jpg  
⚠️ **需配置**: 飞书/Notion上传需配置API Key  
❌ **不支持**: .pptx, .mp3, .mp4

## 问题排查

```bash
# 检查pandoc
which pandoc && pandoc --version

# 检查pypdf
python3 -c "from pypdf import PdfReader; print('OK')"

# 检查openpyxl
python3 -c "import openpyxl; print('OK')"
```
