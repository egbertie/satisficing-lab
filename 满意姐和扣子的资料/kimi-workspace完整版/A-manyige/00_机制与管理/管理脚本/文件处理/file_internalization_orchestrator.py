#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
file_internalization_orchestrator.py
批量文件内化编排器 V1.0

目标：把 archive/safe-uploads/ 中的待处理文件批量提取、分类、
      并按 PMP（程序类）或 WEP（知识类）路由进行自动化内化前处理。

依赖：
  - python-docx（已验证）
  - pymupdf（已安装）
  - Pillow + pytesseract + tesseract-ocr（已安装）
"""

import os
import json
import sys
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

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
SAFE_UPLOADS_DIR = WORKSPACE / "archive" / "safe-uploads"
OUTPUT_DIR = WORKSPACE / "tmp" / "internalization_output"
PROGRESS_FILE = OUTPUT_DIR / ".internalization_progress.json"


@dataclass
class FileTask:
    source_path: Path
    file_hash: str
    file_type: str  # docx, pdf, png, jpg, md, txt, unknown
    status: str = "pending"  # pending, skipped, completed, failed
    output_path: Optional[Path] = None
    error_message: Optional[str] = None
    paragraph_count: int = 0
    word_count: int = 0


class FileInternalizationOrchestrator:
    """批量文件内化编排器 —— 基于 batch-processing-patterns 原则"""

    SUPPORTED_TYPES = {"docx", "pdf", "png", "jpg", "jpeg", "md", "txt"}

    def __init__(
        self,
        source_dir: Path = SAFE_UPLOADS_DIR,
        output_dir: Path = OUTPUT_DIR,
    ):
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.completed_set = self._load_progress()
        self.circuit_failures = 0
        self.max_circuit_failures = 5

    def _load_progress(self) -> set:
        if PROGRESS_FILE.exists():
            data = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
            return set(data.get("completed_hashes", []))
        return set()

    def _save_progress(self):
        PROGRESS_FILE.write_text(
            json.dumps({"completed_hashes": sorted(self.completed_set)}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _compute_hash(self, filepath: Path) -> str:
        blake = hashlib.blake2b(digest_size=16)
        blake.update(filepath.name.encode("utf-8"))
        stat = filepath.stat()
        blake.update(f"{stat.st_size}:{stat.st_mtime}".encode("utf-8"))
        return blake.hexdigest()

    def _should_skip(self, task: FileTask) -> Optional[str]:
        if task.file_hash in self.completed_set:
            return "已完成（断点续传）"
        if task.file_type not in self.SUPPORTED_TYPES:
            return f"不支持的文件类型: {task.file_type}"
        if self.circuit_failures >= self.max_circuit_failures:
            return "熔断器触发（连续失败过多）"
        return None

    def _classify_file(self, filepath: Path) -> str:
        ext = filepath.suffix.lower().lstrip(".")
        # PMP vs WEP 路由判定
        if ext in {"py", "js", "ts", "go", "rs"}:
            return "PMP"  # 精密制造流程（程序类）
        return "WEP"  # 智慧萃取流程（知识类）

    def _extract_docx(self, filepath: Path) -> Tuple[str, int, int]:
        if not _DOCX_AVAILABLE:
            raise RuntimeError("python-docx 未安装")
        try:
            document = docx.Document(str(filepath))
            paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
            text = "\n\n".join(paragraphs)
            word_count = sum(len(p.split()) for p in paragraphs)
            return text, len(paragraphs), word_count
        except Exception as e:
            # Fallback: try pymupdf for corrupted docx files
            if _PDF_AVAILABLE:
                try:
                    doc = fitz.open(str(filepath))
                    paragraphs = []
                    for page in doc:
                        txt = page.get_text().strip()
                        if txt:
                            paragraphs.append(txt)
                    text = "\n\n".join(paragraphs)
                    word_count = sum(len(p.split()) for p in paragraphs)
                    return text, len(paragraphs), word_count
                except Exception:
                    pass
            raise e

    def _extract_pdf(self, filepath: Path) -> Tuple[str, int, int]:
        if not _PDF_AVAILABLE:
            raise RuntimeError("pymupdf 未安装")
        doc = fitz.open(str(filepath))
        paragraphs = []
        for page in doc:
            text = page.get_text().strip()
            if text:
                paragraphs.append(text)
        full_text = "\n\n".join(paragraphs)
        word_count = sum(len(p.split()) for p in paragraphs)
        return full_text, len(paragraphs), word_count

    def _extract_image(self, filepath: Path) -> Tuple[str, int, int]:
        if not _OCR_AVAILABLE:
            raise RuntimeError("OCR 依赖未安装")
        img = Image.open(str(filepath))
        text = pytesseract.image_to_string(img, lang="chi_sim+eng")
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        word_count = len(text.split())
        return text, len(paragraphs), word_count

    def _extract_text(self, filepath: Path) -> Tuple[str, int, int]:
        text = filepath.read_text(encoding="utf-8")
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        word_count = len(text.split())
        return text, len(paragraphs), word_count

    def _process_item(self, task: FileTask) -> FileTask:
        try:
            if task.file_type == "docx":
                text, para_count, word_count = self._extract_docx(task.source_path)
            elif task.file_type == "pdf":
                text, para_count, word_count = self._extract_pdf(task.source_path)
            elif task.file_type in {"png", "jpg", "jpeg"}:
                text, para_count, word_count = self._extract_image(task.source_path)
            elif task.file_type in {"md", "txt"}:
                text, para_count, word_count = self._extract_text(task.source_path)
            else:
                raise ValueError(f"未处理的文件类型: {task.file_type}")

            # 构建输出路径
            relative = task.source_path.relative_to(self.source_dir)
            out_dir = self.output_dir / relative.parent / relative.stem
            out_dir.mkdir(parents=True, exist_ok=True)

            text_path = out_dir / "extracted.txt"
            meta_path = out_dir / "meta.json"
            text_path.write_text(text, encoding="utf-8")

            meta = {
                "source": str(task.source_path),
                "file_hash": task.file_hash,
                "file_type": task.file_type,
                "routed_to": self._classify_file(task.source_path),
                "paragraph_count": para_count,
                "word_count": word_count,
                "extracted_at": datetime.now().isoformat(),
            }
            meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

            task.output_path = text_path
            task.paragraph_count = para_count
            task.word_count = word_count
            task.status = "completed"
            self.circuit_failures = 0  # 成功则重置熔断器
            self.completed_set.add(task.file_hash)
            return task

        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            self.circuit_failures += 1
            return task

    def scan_files(self, date_subdir: Optional[str] = None) -> List[FileTask]:
        """扫描待处理文件队列"""
        target_dir = self.source_dir
        if date_subdir:
            target_dir = self.source_dir / date_subdir

        tasks = []
        for filepath in sorted(target_dir.rglob("*")):
            if not filepath.is_file():
                continue
            ext = filepath.suffix.lower().lstrip(".")
            # 跳过隐藏文件和已处理标记
            if filepath.name.startswith("."):
                continue
            file_hash = self._compute_hash(filepath)
            tasks.append(FileTask(
                source_path=filepath,
                file_hash=file_hash,
                file_type=ext if ext else "unknown",
            ))
        return tasks

    def run_batch(
        self,
        date_subdir: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict:
        """运行批处理，返回完整报告"""
        tasks = self.scan_files(date_subdir)
        if limit:
            tasks = tasks[:limit]

        completed = 0
        failed = 0
        skipped = 0

        for task in tasks:
            skip_reason = self._should_skip(task)
            if skip_reason:
                task.status = "skipped"
                task.error_message = skip_reason
                skipped += 1
                continue

            task = self._process_item(task)
            if task.status == "completed":
                completed += 1
            else:
                failed += 1

            # 每项处理后保存进度（断点续传）
            self._save_progress()

            # 熔断器检查
            if self.circuit_failures >= self.max_circuit_failures:
                # 把剩余的都标记为熔断跳过
                for t in tasks[tasks.index(task) + 1:]:
                    t.status = "skipped"
                    t.error_message = "熔断器触发（连续失败过多）"
                    skipped += 1
                break

        summary = {
            "total": len(tasks),
            "completed": completed,
            "failed": failed,
            "skipped": skipped,
            "output_dir": str(self.output_dir),
        }

        return {
            "summary": summary,
            "tasks": [asdict(t) for t in tasks],
        }

    def dependency_report(self) -> Dict[str, bool]:
        return {
            "python-docx": _DOCX_AVAILABLE,
            "pymupdf": _PDF_AVAILABLE,
            "pytesseract/Pillow": _OCR_AVAILABLE,
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 file_internalization_orchestrator.py [scan|run <subdir>]")
        sys.exit(0)

    cmd = sys.argv[1]
    orchestrator = FileInternalizationOrchestrator()

    if cmd == "deps":
        print(json.dumps(orchestrator.dependency_report(), ensure_ascii=False, indent=2))
    elif cmd == "scan":
        tasks = orchestrator.scan_files("2026-04-08")
        types = {}
        for t in tasks:
            types[t.file_type] = types.get(t.file_type, 0) + 1
        print(f"扫描到 {len(tasks)} 个文件")
        print(json.dumps(types, ensure_ascii=False, indent=2))
    elif cmd == "run" and len(sys.argv) >= 3:
        result = orchestrator.run_batch(sys.argv[2])
        print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    else:
        print("Unknown command")


if __name__ == "__main__":
    main()
