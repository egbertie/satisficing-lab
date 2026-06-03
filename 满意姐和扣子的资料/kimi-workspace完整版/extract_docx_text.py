#!/usr/bin/env python3
"""
Extract full text from docx using python-docx (preserves paragraph breaks).
"""
import sys
from docx import Document

path = sys.argv[1]
out_path = sys.argv[2]

doc = Document(path)
lines = []
for para in doc.paragraphs:
    text = para.text.strip()
    if text:
        lines.append(text)

with open(out_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f"Extracted {len(lines)} paragraphs to {out_path}")
