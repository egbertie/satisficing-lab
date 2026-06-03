> 生成时间: 2026-04-01 14:13+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

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
