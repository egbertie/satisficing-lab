// 理解标准：先读，再改，改完做语法校验
// Task: 修复 admin-windows.html 的密码门

const fs = require('fs');
const path = '/Users/egbertielau/.openclaw/workspace/satisficing-lab/admin-windows.html';
let html = fs.readFileSync(path, 'utf8');

// 1. 移除密码门 HTML 覆盖层 (gate-overlay)
html = html.replace(/<div class="gate-overlay" id="gate">.*?<\/div>\s*<\/div>\s*<\/div>/s, (match) => {
  // match is gate overlay div
  return '';
});

// Actually, let me be more precise
// Remove the gate HTML block
const gateStart = html.indexOf('<div class="gate-overlay" id="gate">');
const gateEnd = html.indexOf('</div>\n<div class="app" id="app">');
if (gateStart > -1 && gateEnd > -1) {
  // Find the actual end of the gate div
  // gate-overlay is followed by gate-box, then gate-error, gate-degrade
  // Then </div> (close gate-box) </div> (close gate-overlay)
  // Let me just remove between gateStart and the div before app
  html = html.substring(0, gateStart) + html.substring(gateEnd);
}

// 2. Update the IIFE comment
html = html.replace(
  /\/\* ===== 密码门 — 已移除.*?\*\/\s*\(function\(\)\{\s*document\.getElementById\('gate'\)\.classList\.add\('hidden'\);\s*document\.getElementById\('app'\)\.classList\.add\('show'\);\s*initApp\(\);\s*\}\)\(\);/s,
  '/* ===== 直接进入（无密码） ===== */\ninitApp();'
);

fs.writeFileSync(path, html);
console.log('Done');
