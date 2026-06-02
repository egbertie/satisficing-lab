#!/bin/bash
# auto_heal.sh — 满意解研究所·自动修复引擎
# 根因: 免疫系统有检测无修复→此脚本关闭Detection-Remediation回路
# Cron: 每小时免疫自检后执行

SITE_DIR="/Users/egbertielau/.openclaw/workspace/site"
WORKSPACE="/Users/egbertielau/.openclaw/workspace"
LOG="$WORKSPACE/memory/_data/auto_heal_log.jsonl"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

healed=0
failed=0
details=""

# === 修复1: 文化密码缺失 ===
echo "[$TIMESTAMP] 修复1: 文化密码检测..."
culture_line='<div style="text-align:center;padding:8px 0;font-size:10px;opacity:0.25;letter-spacing:1px">火承土印·鼎玉契晋·三脉两翼·五维相生</div>'

for f in "$SITE_DIR"/*.html; do
    fname=$(basename "$f")
    if grep -q "五维相生" "$f"; then continue; fi
    if ! grep -q '</body>' "$f"; then continue; fi
    
    sed -i '' "s|</body>|${culture_line}\n</body>|" "$f"
    if grep -q "五维相生" "$f"; then
        healed=$((healed + 1))
        details="$details, culture:$fname"
    else
        failed=$((failed + 1))
        details="$details, culture-fail:$fname"
    fi
done
echo "  文化补全: healed=$healed failed=$failed"

# === 修复2: 反馈组件缺失 ===
echo "[$TIMESTAMP] 修复2: 反馈组件检测..."
fb_block='<div style="max-width:600px;margin:24px auto;padding:0 16px;text-align:center;font-size:13px;border-top:1px solid #D4C5A0;padding-top:20px"><div id="fbQ" style="color:#4A4A4A;font-weight:600;margin-bottom:10px">这个页面对你有用吗？</div><div id="fbBtns" style="display:flex;gap:8px;justify-content:center;margin-bottom:6px"><button onclick="var k=location.pathname.split("/").pop();localStorage.setItem("fb_"+k,"up");document.getElementById("fbBtns").style.display="none";document.getElementById("fbQ").textContent="感谢反馈！"'" style="padding:8px 18px;border-radius:20px;border:1.5px solid #D4C5A0;background:#fff;cursor:pointer;font-size:13px">👍 有用</button><button onclick="var k=location.pathname.split("/").pop();localStorage.setItem("fb_"+k,"text");document.getElementById("fbBtns").style.display="none";document.getElementById("fbQ").textContent="感谢反馈！"'" style="padding:8px 18px;border-radius:20px;border:1.5px solid #D4C5A0;background:#fff;cursor:pointer;font-size:13px">💬 有建议</button></div></div>"

for f in "$SITE_DIR"/*.html; do
    fname=$(basename "$f")
    if grep -q "反馈" "$f" || grep -q "sri_fb_" "$f"; then continue; fi
    if ! grep -q '</body>' "$f"; then continue; fi
    
    sed -i '' "s|</body>|${fb_block}\n</body>|" "$f"
    if grep -q "反馈" "$f"; then
        healed=$((healed + 1))
        details="$details, fb:$fname"
    fi
done
echo "  反馈补全: healed=$healed"

# === 修复3: 品牌残留 ===
echo "[$TIMESTAMP] 修复3: 品牌残留检测..."
count=0
for f in "$SITE_DIR"/*.html; do
    if grep -q "满意红" "$f"; then
        sed -i '' 's/满意红/满意解研究所/g' "$f"
        count=$((count + 1))
    fi
done
echo "  品牌替换: $count页"
healed=$((healed + count))

# === 修复4: 返回链接缺失 ===
echo "[$TIMESTAMP] 修复4: 返回链接检测..."
back_link='<p style="text-align:center;padding:10px;font-size:11px"><a href="go.html" style="color:#C23B22;text-decoration:none">← 返回决策通道</a></p>'
rc=0
for f in "$SITE_DIR"/*.html; do
    fname=$(basename "$f")
    [ "$fname" = "index.html" ] && continue
    if grep -q '返回' "$f" || grep -q 'go.html' "$f"; then continue; fi
    if ! grep -q '</body>' "$f"; then continue; fi
    
    sed -i '' "s|</body>|${back_link}\n</body>|" "$f"
    rc=$((rc + 1))
done
echo "  返回链接: $rc页"
healed=$((healed + rc))

# === 修复5: event.target残留 ===
echo "[$TIMESTAMP] 修复5: event.target检测..."
et=0
for f in "$SITE_DIR"/*.html; do
    fname=$(basename "$f")
    [ "$fname" = "admin-windows.html" ] && continue  # 豁免(字符串常量)
    if grep -q 'event\.target' "$f"; then
        et=$((et + 1))
    fi
done
echo "  event.target(排除豁免): $et页"

# === 修复6: 双副本同步 ===
echo "[$TIMESTAMP] 修复6: 双副本同步..."
cp "$SITE_DIR"/*.html "$WORKSPACE/satisficing-lab/" 2>/dev/null
cp "$SITE_DIR"/*.css "$WORKSPACE/satisficing-lab/" 2>/dev/null
cp "$SITE_DIR"/*.js "$WORKSPACE/satisficing-lab/" 2>/dev/null
echo "  site→satisficing-lab: done"

# === 写日志 ===
total_healed=$healed
echo "{\"ts\":\"$TIMESTAMP\",\"healed\":$total_healed,\"failed\":$failed,\"details\":\"$details\"}" >> "$LOG"
echo "[$TIMESTAMP] auto_heal完成: healed=$total_healed failed=$failed"
