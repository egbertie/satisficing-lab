#!/bin/bash
SITE="/Users/egbertielau/.openclaw/workspace/site"
PASS=0; FAIL=0

echo "🔬 全站质量体检 $(date '+%H:%M:%S')"
echo ""

# JS语法
echo "📋 JS语法"
for f in "$SITE"/*.html; do
  python3 -c "
import re,subprocess,tempfile,os
with open('$f') as fp: c=fp.read()
for js in re.findall(r'<script[^>]*>(.*?)</script>',c,re.DOTALL):
  tf=tempfile.NamedTemporaryFile(mode='w',suffix='.js',delete=False)
  tf.write(js);tf.close()
  r=subprocess.run(['node','--check',tf.name],capture_output=True,text=True)
  os.unlink(tf.name)
  if r.returncode!=0:
    print(f'❌ {os.path.basename(\"$f\")}')
    exit(1)
  " 2>/dev/null && echo "   ✅ $(basename $f)" && PASS=$((PASS+1)) || FAIL=$((FAIL+1))
done
echo "   结果: ✅$PASS ❌$FAIL"

# event.target
echo ""
echo "📋 event.target"
C=$(grep -rl 'event\.target' "$SITE"/*.html 2>/dev/null | wc -l | tr -d ' ')
[ "$C" -eq 0 ] && echo "   ✅ 全站安全" || { echo "   ❌ $C 个文件"; grep -rl 'event\.target' "$SITE"/*.html | while read f; do echo "     - $(basename $f)"; done; }

# crypto
echo ""
echo "📋 crypto.subtle"
C=$(grep -rl 'crypto\.subtle' "$SITE"/*.html 2>/dev/null | wc -l | tr -d ' ')
[ "$C" -eq 0 ] && echo "   ✅ 全站安全" || { echo "   ❌ $C 个文件"; grep -rl 'crypto\.subtle' "$SITE"/*.html | while read f; do echo "     - $(basename $f)"; done; }

# 线上一致性(关键页面)
echo ""
echo "📋 线上一致性"
for f in dashboard.html cases.html index.html about.html; do
  L=$(md5 -q "$SITE/$f" 2>/dev/null)
  R=$(curl -sL "https://egbertie.github.io/satisficing-lab/$f" 2>/dev/null | md5 -q 2>/dev/null)
  [ "$L" = "$R" ] && [ -n "$L" ] && echo "   ✅ $f" || echo "   ❌ $f"
done

echo ""
echo "✅ 体检完成"
