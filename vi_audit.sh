#!/bin/bash
BRAND_COLORS="#C23B22|#F5F0E6|#f5f0e6|#B8860B|#4A4A4A|#2A2A2A|#D4C5A0|#d4c5a0|#fff|#FFF"
VIOLATIONS=$(grep -rn '#[0-9A-Fa-f]\{6\}' *.html *.css 2>/dev/null | grep -vE "$BRAND_COLORS")
if [ -z "$VIOLATIONS" ]; then echo "✅ VI合规·全部文件通过"; exit 0
else echo "🔴 违规色:"; echo "$VIOLATIONS"; exit 1; fi
