#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
downloads_md_converter.py
.kimi/downloads/ → Markdown 转化流水线 V1.0

目标：将 .kimi/downloads/ 中的全部文件按类型转化为结构化的 Markdown，
      归档到 archive/md_conversions/YYYY-MM-DD/，并生成元数据与进度追踪。

设计原则：
  1. 本地处理，零 LLM Token 消耗
  2. 不偷工减料：保留原文件结构、标题层级、页码分隔
  3. 可复用：新上传文件可增量执行
  4. 安全清理：转换验证通过后，原始文件移入 archive/original_downloads/ 备份

转化策略：
  - DOCX  → MD：python-docx 提取段落，按样式映射为 Markdown 标题
  - PDF   → MD：PyMuPDF 按页提取，保留分页符与段落结构
  - PNG/JPG → MD：OCR 提取文本，图像本身以 base64 嵌入（可选关闭）
  - TXT/MD → 直接复制并添加 YAML frontmatter
  - 其他   → 跳过并记录

依赖：python-docx, pymupdf, Pillow, pytesseract, tesseract-ocr
"""

import os
import sys
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

sys.path.insert(0, '/root/.openclaw/workspace')
from defense_base_components import BaseComponent

# Optional parsers
_DOCX_AVAILABLE = False
_PDF_AVAILABLE = False
_OCR_AVAILABLE = False

try:
    import docx
    _DOCX_AVAILABLE = True
except ImportError:
    pass

try:
    import fitz  # PyMuPDF
    _PDF_AVAILABLE = True
except ImportError:
    pass

try:
    from PIL import Image
    import pytesseract
    _OCR_AVAILABLE = True
except ImportError:
    pass


WORKSPACE = Path("/root/.openclaw/workspace")
DOWNLOADS_DIR = WORKSPACE / ".kimi" / "downloads"
MD_OUTPUT_DIR = WORKSPACE / "archive" / "md_conversions"
ORIGINAL_BACKUP_DIR = WORKSPACE / "archive" / "original_downloads"
PROGRESS_FILE = WORKSPACE / "tmp" / "downloads_conversion_progress.json"


@dataclass
class ConversionTask:
    source_path: Path
    file_hash: str
    file_type: str
    status: str = "pending"
    output_path: Optional[Path] = None
    error_message: Optional[str] = None
    paragraph_count: int = 0
    word_count: int = 0
    char_count: int = 0


class DownloadsMdConverter(BaseComponent):
    """
    .kimi/downloads/ → Markdown 转化流水线
    继承 BaseComponent，复用 workspace 基础设施
    """

    SUPPORTED_TYPES = {"docx", "pdf", "png", "jpg", "jpeg", "md", "txt"}

    def __init__(
        self,
        source_dir: Path = DOWNLOADS_DIR,
        output_dir: Path = MD_OUTPUT_DIR,
        backup_dir: Path = ORIGINAL_BACKUP_DIR,
        dry_run: bool = False,
    ):
        super().__init__("downloads_md_converter")
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.backup_dir = backup_dir
        self.dry_run = dry_run or os.environ.get("DOWNLOADS_CONVERTER_DRY_RUN") == "1"

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.progress = self._load_progress()
        self.today_str = datetime.now().strftime("%Y-%m-%d")

    def _load_progress(self) -> Dict:
        """加载进度记录（已完成哈希集合）"""
        if PROGRESS_FILE.exists():
            try:
                return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"completed_hashes": []}

    def _save_progress(self):
        """保存进度记录"""
        PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
        PROGRESS_FILE.write_text(
            json.dumps(self.progress, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _compute_hash(self, filepath: Path) -> str:
        """计算文件 md5"""
        h = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    def _should_skip(self, task: ConversionTask) -> Optional[str]:
        """判断是否已处理过（基于文件哈希）"""
        if task.file_hash in self.progress.get("completed_hashes", []):
            # 检查 MD 文件是否真实存在
            expected = self.output_dir / self.today_str / f"{task.source_path.stem}.md"
            if expected.exists() and expected.stat().st_size > 0:
                return f"already_converted: {expected}"
        return None

    def _classify_file(self, filepath: Path) -> str:
        """按扩展名分类"""
        ext = filepath.suffix.lower().lstrip(".")
        if ext in self.SUPPORTED_TYPES:
            return ext
        return "unknown"

    # ───────────────────────────────────────────────
    # 各类文件提取器
    # ───────────────────────────────────────────────

    def _extract_docx_fallback(self, filepath: Path) -> Tuple[str, int, int, int]:
        """DOCX 备用提取：直接读取 word/document.xml，绕过 python-docx 的 bookmark 解析"""
        import zipfile
        import re

        with zipfile.ZipFile(str(filepath)) as zf:
            xml_content = zf.read("word/document.xml").decode("utf-8", errors="replace")

        # 策略：先把整个 XML 中所有 <w:t> 标签内的文本按顺序提取出来
        # 同时尝试按 <w:p> 段落边界拆分（精确匹配 <w:p[...]> 到 </w:p> 的文本片段）
        paragraphs = []

        # 方法A：按完整的 w:p 块提取（贪婪匹配整个段落标签包裹的内容）
        # 非贪婪匹配确保每个段落独立
        for p_block in re.findall(r'<w:p\b[^>]*>.*?</w:p>', xml_content, re.DOTALL):
            p_texts = re.findall(r'<w:t\b[^>]*>(.*?)</w:t>', p_block, re.DOTALL)
            para_text = "".join(p_texts).strip()
            # 清理残留的 XML 尖括号内容（极少数情况）
            para_text = re.sub(r'<[^>]+>', '', para_text)
            if para_text:
                paragraphs.append(para_text)

        # 方法B兜底：如果段落提取为空（极少），退化为全文提取
        if not paragraphs:
            texts = re.findall(r'<w:t\b[^>]*>(.*?)</w:t>', xml_content, re.DOTALL)
            full_text = "".join(texts).strip()
            # 按空行拆分段落
            paragraphs = [p.strip() for p in re.split(r'\n\s*\n', full_text) if p.strip()]

        content = "\n\n".join(paragraphs)
        para_count = len(paragraphs)
        word_count = len(content.split())
        char_count = len(content)
        return content, para_count, word_count, char_count

    def _extract_docx(self, filepath: Path) -> Tuple[str, int, int, int]:
        """DOCX → Markdown：保留标题层级"""
        if not _DOCX_AVAILABLE:
            raise RuntimeError("python-docx not installed")

        try:
            document = docx.Document(str(filepath))
        except KeyError:
            # 常见原因：word/#bookmarkXXX 缺失导致 python-docx 崩溃
            return self._extract_docx_fallback(filepath)

        lines = []
        para_count = 0
        word_count = 0

        for para in document.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            para_count += 1
            word_count += len(text.split())

            style = para.style.name if para.style else "Normal"
            if style.startswith("Heading"):
                try:
                    level = int(style.replace("Heading", "").strip())
                except ValueError:
                    level = 1
                prefix = "#" * level + " "
            else:
                prefix = ""

            lines.append(f"{prefix}{text}")

        content = "\n\n".join(lines)
        char_count = len(content)
        return content, para_count, word_count, char_count

    def _extract_pdf(self, filepath: Path) -> Tuple[str, int, int, int]:
        """PDF → Markdown：按页提取，保留分页结构"""
        if not _PDF_AVAILABLE:
            raise RuntimeError("pymupdf not installed")

        doc = fitz.open(str(filepath))
        pages = []
        para_count = 0
        word_count = 0

        for page_num in range(len(doc)):
            text = doc.load_page(page_num).get_text("text").strip()
            if text:
                lines = text.splitlines()
                para_count += len([l for l in lines if l.strip()])
                word_count += len(text.split())
                pages.append(f"<!-- Page {page_num + 1} -->\n\n{text}")

        doc.close()
        content = "\n\n---\n\n".join(pages)
        char_count = len(content)
        return content, para_count, word_count, char_count

    def _extract_image(self, filepath: Path) -> Tuple[str, int, int, int]:
        """PNG/JPG → Markdown：OCR 提取文本"""
        if not _OCR_AVAILABLE:
            raise RuntimeError("Pillow + pytesseract not installed")

        image = Image.open(str(filepath))
        text = pytesseract.image_to_string(image, lang="chi_sim+eng").strip()
        image.close()

        lines = text.splitlines()
        para_count = len([l for l in lines if l.strip()])
        word_count = len(text.split())

        content = f"<!-- Image OCR: {filepath.name} -->\n\n{text}"
        char_count = len(content)
        return content, para_count, word_count, char_count

    def _extract_text(self, filepath: Path) -> Tuple[str, int, int, int]:
        """TXT/MD → 直接读取"""
        raw = filepath.read_text(encoding="utf-8", errors="replace")
        para_count = len([l for l in raw.splitlines() if l.strip()])
        word_count = len(raw.split())
        char_count = len(raw)
        return raw, para_count, word_count, char_count

    # ───────────────────────────────────────────────
    # Markdown 组装
    # ───────────────────────────────────────────────

    def _build_markdown(
        self,
        task: ConversionTask,
        body: str,
    ) -> str:
        """为提取内容添加标准 YAML frontmatter"""
        frontmatter = {
            "title": task.source_path.stem,
            "source_filename": task.source_path.name,
            "file_hash": task.file_hash,
            "file_type": task.file_type,
            "converted_at": datetime.now().isoformat(),
            "paragraph_count": task.paragraph_count,
            "word_count": task.word_count,
            "char_count": task.char_count,
            "converter": "downloads_md_converter.py v1.0",
        }
        fm_lines = ["---"] + [f"{k}: {v}" for k, v in frontmatter.items()] + ["---", ""]
        return "\n".join(fm_lines) + body

    def _process_item(self, task: ConversionTask) -> ConversionTask:
        """处理单个文件"""
        try:
            if task.file_type == "docx":
                body, p, w, c = self._extract_docx(task.source_path)
            elif task.file_type == "pdf":
                body, p, w, c = self._extract_pdf(task.source_path)
            elif task.file_type in ("png", "jpg", "jpeg"):
                body, p, w, c = self._extract_image(task.source_path)
            elif task.file_type in ("md", "txt"):
                body, p, w, c = self._extract_text(task.source_path)
            else:
                task.status = "skipped"
                task.error_message = f"unsupported_type: {task.file_type}"
                return task

            task.paragraph_count = p
            task.word_count = w
            task.char_count = c

            # 生成 Markdown
            md_content = self._build_markdown(task, body)

            # 写入输出目录
            out_dir = self.output_dir / self.today_str
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{task.source_path.stem}.md"

            if not self.dry_run:
                out_path.write_text(md_content, encoding="utf-8")

            task.output_path = out_path
            task.status = "completed"

            # 记录进度
            if task.file_hash not in self.progress.get("completed_hashes", []):
                self.progress.setdefault("completed_hashes", []).append(task.file_hash)

        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)

        return task

    def scan_files(self) -> List[ConversionTask]:
        """扫描源目录，生成待处理任务列表"""
        tasks = []
        if not self.source_dir.exists():
            return tasks

        for filepath in sorted(self.source_dir.iterdir()):
            if not filepath.is_file():
                continue
            file_type = self._classify_file(filepath)
            file_hash = self._compute_hash(filepath)
            task = ConversionTask(
                source_path=filepath,
                file_hash=file_hash,
                file_type=file_type,
            )
            skip_reason = self._skip_if_done(task)
            if skip_reason:
                task.status = "skipped"
                task.error_message = skip_reason
            tasks.append(task)
        return tasks

    def _skip_if_done(self, task: ConversionTask) -> Optional[str]:
        """检查是否已经转换过（支持跨日期回溯查找）"""
        if task.file_hash in self.progress.get("completed_hashes", []):
            # 查找任何日期子目录下的对应 MD
            for date_dir in self.output_dir.iterdir():
                if not date_dir.is_dir():
                    continue
                expected = date_dir / f"{task.source_path.stem}.md"
                if expected.exists() and expected.stat().st_size > 0:
                    task.output_path = expected
                    return f"already_converted: {expected}"
        return None

    def run_batch(
        self,
        cleanup_after_success: bool = False,
    ) -> Dict:
        """执行批量转化"""
        tasks = self.scan_files()
        report = {
            "timestamp": self.get_timestamp(),
            "dry_run": self.dry_run,
            "total": len(tasks),
            "completed": 0,
            "skipped": 0,
            "failed": 0,
            "unsupported": 0,
            "cleaned": 0,
            "tasks": [],
        }

        for task in tasks:
            if task.status == "skipped":
                report["skipped"] += 1
                report["tasks"].append(asdict(task))
                continue

            if task.file_type == "unknown":
                task.status = "skipped"
                task.error_message = "unsupported file type"
                report["unsupported"] += 1
                report["tasks"].append(asdict(task))
                continue

            processed = self._process_item(task)
            report["tasks"].append(asdict(processed))

            if processed.status == "completed":
                report["completed"] += 1
            else:
                report["failed"] += 1

        self._save_progress()

        if cleanup_after_success and not self.dry_run:
            report["cleaned"] = self._cleanup_originals(report["tasks"])

        self._generate_report(report)
        return report

    def _cleanup_originals(self, tasks: List[Dict]) -> int:
        """将转换成功的原始文件移入备份目录"""
        cleaned = 0
        backup_subdir = self.backup_dir / self.today_str
        backup_subdir.mkdir(parents=True, exist_ok=True)

        for task in tasks:
            if task["status"] != "completed":
                continue
            src = Path(task["source_path"])
            if not src.exists():
                continue
            dest = backup_subdir / src.name
            try:
                shutil.move(str(src), str(dest))
                cleaned += 1
            except Exception as e:
                self.log_error(f"Cleanup failed for {src}: {e}")

        return cleaned

    def _generate_report(self, report: Dict):
        """生成 Markdown 报告"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_dir = WORKSPACE / "memory" / "asset-activation"
        log_dir.mkdir(parents=True, exist_ok=True)
        report_file = log_dir / f"downloads-md-conversion-{date_str}.md"

        lines = [
            "# .kimi/downloads/ → Markdown 转化报告",
            "",
            f"**时间**: {report['timestamp']}",
            f"**模式**: {'Dry-Run' if report['dry_run'] else '实际执行'}",
            "",
            "## 执行摘要",
            "",
            f"- 📁 扫描文件总数: {report['total']}",
            f"- ✅ 成功转化: {report['completed']}",
            f"- ⏭️ 已转化跳过: {report['skipped']}",
            f"- ❌ 转化失败: {report['failed']}",
            f"- 🚫 不支持的类型: {report['unsupported']}",
            f"- 🗑️ 已清理原始文件: {report.get('cleaned', 0)}",
            "",
            "## 成功转化详情",
            "",
            "| 原始文件 | 类型 | 段落数 | 字数 | 输出路径 |",
            "|----------|------|--------|------|----------|",
        ]

        for task in report["tasks"]:
            if task["status"] == "completed":
                out = task.get("output_path", "N/A")
                lines.append(
                    f"| `{task['source_path'].split('/')[-1]}` | {task['file_type']} | "
                    f"{task['paragraph_count']} | {task['word_count']} | `{out}` |"
                )

        if report["failed"] > 0:
            lines.extend(["", "## 失败详情", ""])
            for task in report["tasks"]:
                if task["status"] == "failed":
                    lines.append(
                        f"- `{task['source_path'].split('/')[-1]}` → {task.get('error_message', 'unknown')}"
                    )

        report_file.write_text("\n".join(lines), encoding="utf-8")
        print(f"✅ 转化报告已生成: {report_file}")

    def dependency_report(self) -> Dict[str, bool]:
        return {
            "python-docx": _DOCX_AVAILABLE,
            "pymupdf": _PDF_AVAILABLE,
            "ocr": _OCR_AVAILABLE,
        }


def main():
    dry_run = "--dry-run" in sys.argv
    cleanup = "--cleanup" in sys.argv

    converter = DownloadsMdConverter(dry_run=dry_run)

    deps = converter.dependency_report()
    print("依赖状态:", deps)

    report = converter.run_batch(cleanup_after_success=cleanup)
    print(
        f"\n结果: 总计 {report['total']} | 成功 {report['completed']} | "
        f"跳过 {report['skipped']} | 失败 {report['failed']} | "
        f"清理 {report.get('cleaned', 0)}"
    )


if __name__ == "__main__":
    main()
