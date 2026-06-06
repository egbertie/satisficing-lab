#!/usr/bin/env python3
"""
满意红 · 本地门户服务
=====================
自建HTTP服务器，不依赖GitHub Pages。
直接读取工作区文件，无需Git推送。

特性:
- 服务工作区根目录所有文件（HTML/CSS/JS/图片/数据）
- 内置密码门验证 (与所有页面统一: 123654)
- 支持目录浏览（文件浏览器功能）
- Markdown/代码文件在线预览
- 零外部依赖，仅用Python标准库
- 支持launchd常驻 + 后台运行

端口: 8765
"""

import os
import sys
import json
import time
import base64
import hashlib
import mimetypes
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from http import HTTPStatus
from pathlib import Path

# ========== 配置 ==========
PORT = 8765
WORKSPACE = Path(os.path.dirname(os.path.abspath(__file__)))
PASSWORD = "123654"
PASSWORD_SALT = "satisfice-portal-2026"  # 用于token生成
SESSION_TTL = 86400  # 24小时

# 文件扩展名 → Content-Type 映射
MIME_MAP = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.md': 'text/markdown; charset=utf-8',
    '.txt': 'text/plain; charset=utf-8',
    '.py': 'text/plain; charset=utf-8',
    '.xml': 'application/xml; charset=utf-8',
    '.svg': 'image/svg+xml',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
    '.ico': 'image/x-icon',
    '.pdf': 'application/pdf',
    '.zip': 'application/zip',
    '.gz': 'application/gzip',
    '.tar': 'application/x-tar',
}

# 路径穿越防护：只允许访问工作区内的文件
ALLOWED_ROOTS = [WORKSPACE.resolve()]

def is_safe_path(path: Path) -> bool:
    """防止路径穿越攻击"""
    try:
        resolved = path.resolve()
        for root in ALLOWED_ROOTS:
            try:
                resolved.relative_to(root)
                return True
            except ValueError:
                continue
        return False
    except (ValueError, OSError):
        return False

def make_session_token(ip: str) -> str:
    """生成会话token"""
    h = hashlib.sha256()
    h.update(f"{PASSWORD}:{PASSWORD_SALT}:{ip}:{int(time.time() // 3600)}".encode())
    return h.hexdigest()[:32]

def verify_session_token(token: str, ip: str) -> bool:
    """验证会话token（当前小时或上一小时都有效，因为跨小时边界）"""
    for offset in [0, -3600]:
        h = hashlib.sha256()
        h.update(f"{PASSWORD}:{PASSWORD_SALT}:{ip}:{int(time.time() // 3600 + offset//3600)}".encode())
        if h.hexdigest()[:32] == token:
            return True
    return False


class ThreadingServer(ThreadingMixIn, HTTPServer):
    """多线程HTTP服务器"""
    daemon_threads = True


class PortalHandler(SimpleHTTPRequestHandler):
    """自定义请求处理器"""
    timeout = 30  # 30秒超时

    def __init__(self, *args, **kwargs):
        self.directory = str(WORKSPACE)
        super().__init__(*args, **kwargs)

    def log_message(self, format, *args):
        """简洁日志"""
        ts = time.strftime('%H:%M:%S')
        print(f"[{ts}] {args[0]}", flush=True)

    def _get_client_ip(self) -> str:
        """获取客户端IP"""
        forwarded = self.headers.get('X-Forwarded-For', '')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return self.client_address[0]

    def _check_auth(self) -> bool:
        """检查认证状态"""
        # 检查Cookie
        cookie = self.headers.get('Cookie', '')
        if 'portal_token=' in cookie:
            # 解析cookie
            token = None
            for item in cookie.split(';'):
                item = item.strip()
                if item.startswith('portal_token='):
                    token = item[len('portal_token='):]
                    break
            if token and verify_session_token(token, self._get_client_ip()):
                return True
        return False

    def _serve_password_gate(self, redirect_to: str = '/'):
        """服务密码门"""
        # 如果已认证，直接跳转
        if self._check_auth():
            self.send_response(302)
            self.send_header('Location', redirect_to)
            self.end_headers()
            return

        # 读取 portal 模式 — 使用内置模板
        gate_html = self._get_portal_html(redirect_to)
        body = gate_html.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def _get_portal_html(self, redirect_to: str = 'dashboard-v3.html') -> str:
        """生成门户页面HTML"""
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>满意红</title>
<style>
:root {{
  --bg: #F5F0E6;
  --ink: #4A3728;
  --ink-light: #8B7355;
  --ink-lighter: #B8A898;
  --accent-red: #C23B22;
  --accent-gold: #B8860B;
  --border: #E0D5C0;
}}
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{
  font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans SC",sans-serif;
  background:var(--bg); color:var(--ink); min-height:100vh;
  display:flex; align-items:center; justify-content:center;
  -webkit-tap-highlight-color:transparent;
}}
#gate {{
  display:flex; flex-direction:column; align-items:center;
  padding:32px 20px; max-width:320px; width:100%;
}}
.logo {{
  width:88px; height:88px; background:var(--accent-red);
  color:#fff; border-radius:20px; display:flex;
  align-items:center; justify-content:center;
  font-size:44px; font-weight:700; margin-bottom:20px;
  box-shadow: 0 4px 24px rgba(194,59,34,0.25);
}}
h1 {{ font-size:1.6em; margin-bottom:4px; }}
.subtitle {{ color:var(--ink-light); font-size:0.9em; margin-bottom:28px; }}
input {{
  width:100%; padding:12px 16px; border:1px solid var(--border);
  border-radius:8px; background:#fff; color:var(--ink);
  font-size:1em; outline:none; text-align:center; -webkit-appearance:none;
  margin-bottom:14px; transition:border 0.2s;
}}
input:focus {{ border-color:var(--accent-gold); }}
button {{
  width:100%; padding:12px; background:var(--accent-red); color:#fff;
  border:none; border-radius:8px; font-size:1em; cursor:pointer;
  font-weight:500; -webkit-appearance:none; transition:opacity 0.2s;
}}
button:active {{ opacity:0.8; }}
.hint {{ color:var(--ink-lighter); font-size:0.8em; margin-top:14px; }}
.error {{ color:var(--accent-red); font-size:0.8em; margin-top:8px; display:none; }}
</style>
</head>
<body>
<div id="gate">
  <div class="logo">红</div>
  <h1>满意红</h1>
  <p class="subtitle">知识体系 · 本地服务</p>
  <input type="password" id="pw" placeholder="输入通行码" inputmode="numeric" autofocus
    onkeydown="if(event.key==='Enter')unlock()">
  <button onclick="unlock()">进入</button>
  <p class="hint">通行码验证后24小时内免重复输入</p>
  <p class="error" id="err">通行码错误</p>
</div>
<script>
var PASS = '{PASSWORD}';
function unlock() {{
  var pw = document.getElementById('pw').value;
  if (pw === PASS) {{
    // 设为cookie (服务端验证用)
    document.cookie = 'portal_pw=' + pw + ';path=/;max-age=86400;samesite=lax';
    // 跳转
    window.location.href = '{redirect_to}';
  }} else {{
    var inp = document.getElementById('pw');
    var err = document.getElementById('err');
    inp.value = ''; inp.style.borderColor = 'var(--accent-red)';
    err.style.display = 'block';
    setTimeout(function(){{ inp.style.borderColor=''; err.style.display='none'; }}, 1500);
  }}
}}
</script>
</body>
</html>'''

    def _serve_login(self):
        """处理登录请求"""
        content_len = int(self.headers.get('Content-Length', 0))
        if content_len > 0:
            post_data = self.rfile.read(content_len).decode('utf-8')
            params = urllib.parse.parse_qs(post_data)
            pw = params.get('pw', [''])[0]

            if pw == PASSWORD:
                token = make_session_token(self._get_client_ip())
                redirect = params.get('r', ['/dashboard-v3.html'])[0]
                body = 'ok'
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.send_header('Set-Cookie',
                    f'portal_token={token}; Path=/; Max-Age={SESSION_TTL}; SameSite=Lax; HttpOnly')
                self.send_header('Content-Length', len(body))
                self.end_headers()
                self.wfile.write(body.encode())
                return

        self.send_response(403)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        body = 'wrong password'
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body.encode())

    def _serve_directory_listing(self, dir_path: Path, url_path: str):
        """目录浏览（简易文件浏览器）"""
        try:
            entries = sorted(dir_path.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
        except PermissionError:
            self.send_error(403, "Forbidden")
            return

        # 面包屑
        parts = url_path.strip('/').split('/')
        breadcrumb = '<a href="/">🏠 根目录</a>'
        accum = ''
        for p in parts:
            if p:
                accum += '/' + p
                breadcrumb += f' / <a href="{accum}">{p}</a>'

        items_html = ''
        for entry in entries:
            name = entry.name
            if name.startswith('.') and name != '.nojekyll':
                continue  # 隐藏文件
            rel = url_path.rstrip('/') + '/' + name
            if entry.is_dir():
                icon = '📁'
                size = '-'
                klass = 'dir'
            else:
                ext = entry.suffix.lower()
                icon_map = {
                    '.html': '🌐', '.md': '📝', '.py': '🐍', '.json': '📋',
                    '.txt': '📄', '.png': '🖼️', '.jpg': '🖼️', '.svg': '🎨',
                    '.pdf': '📕', '.zip': '📦', '.gz': '📦', '.sh': '⚙️',
                    '.js': '📜', '.css': '🎨',
                }
                icon = icon_map.get(ext, '📄')
                try:
                    sz = entry.stat().st_size
                    if sz < 1024:
                        size = f'{sz}B'
                    elif sz < 1024 * 1024:
                        size = f'{sz/1024:.0f}K'
                    else:
                        size = f'{sz/(1024*1024):.1f}M'
                except OSError:
                    size = '?'
                klass = 'file'

            items_html += f'''<tr class="{klass}">
                <td>{icon} <a href="{rel}">{name}</a></td>
                <td style="text-align:right;color:#8B7355;font-size:0.85em">{size}</td>
            </tr>\n'''

        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>📁 {url_path} - 满意红</title>
<style>
:root {{ --bg:#F5F0E6; --ink:#4A3728; --link:#C23B22; --border:#E0D5C0; --accent:#B8860B; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,"Noto Sans SC",sans-serif;
  background:var(--bg); color:var(--ink); max-width:800px; margin:0 auto; padding:20px; }}
a {{ color:var(--link); text-decoration:none; }}
a:hover {{ text-decoration:underline; }}
.breadcrumb {{ color:#8B7355; font-size:0.9em; margin-bottom:16px; padding-bottom:10px; border-bottom:1px solid var(--border); }}
.search-box {{ display:flex; gap:8px; margin-bottom:20px; }}
.search-box input {{
  flex:1; padding:10px 14px; border:1px solid var(--border); border-radius:8px;
  font-size:0.95em; outline:none; background:#fff; color:var(--ink);
  transition:border 0.2s;
}}
.search-box input:focus {{ border-color:var(--accent); }}
.search-box button {{
  padding:10px 16px; background:var(--accent); color:#fff; border:none;
  border-radius:8px; font-size:0.9em; cursor:pointer; white-space:nowrap;
}}
.search-box button:hover {{ opacity:0.85; }}
.search-info {{ font-size:0.85em; color:#8B7355; margin-bottom:14px; display:none; }}
.search-info.show {{ display:block; }}
table {{ width:100%; border-collapse:collapse; }}
td {{ padding:8px 4px; border-bottom:1px solid var(--border); }}
tr.hidden {{ display:none; }}
tr:hover {{ background:rgba(184,134,11,0.06); }}
h2 {{ margin-bottom:16px; }}
.footer {{ margin-top:30px; padding-top:12px; border-top:1px solid var(--border); color:#B8A898; font-size:0.75em; text-align:center; }}
</style>
</head>
<body>
<h2>📁 目录浏览</h2>
<div class="breadcrumb">{breadcrumb}</div>
<div class="search-box">
  <input type="text" id="search" placeholder="🔍 搜索文件或目录..." autofocus
    oninput="doSearch()" onkeydown="if(event.key==='Escape'){{this.value='';doSearch();}}">
  <button onclick="document.getElementById('search').value='';doSearch();">清除</button>
</div>
<div class="search-info" id="info"></div>
<table id="fileTable">
{items_html}
</table>
<div class="footer">满意红 · 本地服务 · {time.strftime('%Y-%m-%d %H:%M')}</div>
<script>
function doSearch() {{
  var q = document.getElementById('search').value.toLowerCase().trim();
  var rows = document.querySelectorAll('#fileTable tr');
  var total = 0, shown = 0;
  rows.forEach(function(r) {{
    var name = r.textContent.toLowerCase();
    if (!q) {{ r.classList.remove('hidden'); shown++; }}
    else if (name.includes(q)) {{ r.classList.remove('hidden'); shown++; }}
    else {{ r.classList.add('hidden'); }}
    total++;
  }});
  var info = document.getElementById('info');
  if (q) {{
    info.className = 'search-info show';
    info.textContent = '找到 ' + shown + ' / ' + total + ' 个项目';
  }} else {{
    info.className = 'search-info';
  }}
}}
</script>
</body>
</html>'''
        body = html.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def _serve_markdown_preview(self, file_path: Path):
        """Markdown 预览"""
        try:
            text = file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.send_error(500, str(e))
            return

        # 简单Markdown→HTML（不依赖外部库）
        html_text = self._markdown_to_html(text)

        full = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{file_path.name} - 满意红</title>
<style>
:root {{ --bg:#F5F0E6; --ink:#4A3728; --link:#C23B22; --border:#E0D5C0; --code-bg:#F0EBD8; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,"Noto Sans SC",sans-serif;
  background:var(--bg); color:var(--ink); max-width:820px; margin:0 auto; padding:20px; line-height:1.7; }}
a {{ color:var(--link); }}
h1,h2,h3 {{ margin-top:1.5em; margin-bottom:0.5em; }}
h1 {{ font-size:1.5em; border-bottom:2px solid var(--border); padding-bottom:8px; }}
h2 {{ font-size:1.25em; }}
code {{ background:var(--code-bg); padding:2px 6px; border-radius:3px; font-size:0.9em; }}
pre {{ background:var(--code-bg); padding:12px 16px; border-radius:6px; overflow-x:auto; }}
pre code {{ background:none; padding:0; }}
blockquote {{ border-left:3px solid #B8860B; margin:1em 0; padding:4px 16px; color:#8B7355; }}
table {{ border-collapse:collapse; width:100%; margin:1em 0; }}
th,td {{ border:1px solid var(--border); padding:8px 12px; text-align:left; }}
th {{ background:rgba(184,134,11,0.1); }}
hr {{ border:none; border-top:1px solid var(--border); margin:2em 0; }}
.back {{ font-size:0.85em; color:#B8A898; margin-bottom:16px; }}
.back a {{ color:#B8A898; }}
</style>
</head>
<body>
<div class="back"><a href="/">🏠 满意红</a> · {file_path.name}</div>
{html_text}
</body>
</html>'''
        body = full.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def _markdown_to_html(self, text: str) -> str:
        """简易Markdown→HTML转换"""
        import re
        lines = text.split('\n')
        out = []
        in_code = False
        in_table = False
        table_rows = []

        i = 0
        while i < len(lines):
            line = lines[i]

            # 代码块
            if line.strip().startswith('```'):
                if in_code:
                    out.append('</code></pre>')
                    in_code = False
                else:
                    out.append('<pre><code>')
                    in_code = True
                i += 1
                continue

            if in_code:
                out.append(self._escape_html(line))
                i += 1
                continue

            # 空行
            if not line.strip():
                if in_table:
                    out.append(self._render_table(table_rows))
                    table_rows = []
                    in_table = False
                i += 1
                continue

            # 表格
            if '|' in line and line.strip().startswith('|'):
                cells = [c.strip() for c in line.strip().split('|')[1:-1]]
                if all(c.startswith('---') or c.startswith(':--') for c in cells):
                    # 分隔行，跳过
                    i += 1
                    continue
                table_rows.append(cells)
                in_table = True
                i += 1
                continue
            elif in_table:
                out.append(self._render_table(table_rows))
                table_rows = []
                in_table = False

            # 标题
            m = re.match(r'^(#{1,6})\s+(.*)', line)
            if m:
                level = len(m.group(1))
                out.append(f'<h{level}>{self._inline_markdown(m.group(2))}</h{level}>')
                i += 1
                continue

            # 水平线
            if re.match(r'^[-*_]{3,}\s*$', line):
                out.append('<hr>')
                i += 1
                continue

            # 引用
            m = re.match(r'^>\s*(.*)', line)
            if m:
                quoted_lines = []
                while i < len(lines) and lines[i].startswith('>'):
                    quoted_lines.append(re.sub(r'^>\s?', '', lines[i]))
                    i += 1
                out.append(f'<blockquote>{"<br>".join(self._inline_markdown(l) for l in quoted_lines)}</blockquote>')
                continue

            # 列表
            m = re.match(r'^(\s*)[-*+]\s+(.*)', line)
            if m:
                list_items = []
                indent = len(m.group(1))
                while i < len(lines):
                    m2 = re.match(r'^(\s*)[-*+]\s+(.*)', lines[i])
                    if not m2 or len(m2.group(1)) != indent:
                        break
                    list_items.append(self._inline_markdown(m2.group(2)))
                    i += 1
                items = ''.join(f'<li>{item}</li>' for item in list_items)
                out.append(f'<ul>{items}</ul>')
                continue

            # 编号列表
            m = re.match(r'^(\s*)\d+\.\s+(.*)', line)
            if m:
                list_items = []
                while i < len(lines):
                    m2 = re.match(r'^\d+\.\s+(.*)', lines[i])
                    if not m2:
                        break
                    list_items.append(self._inline_markdown(m2.group(1)))
                    i += 1
                items = ''.join(f'<li>{item}</li>' for item in list_items)
                out.append(f'<ol>{items}</ol>')
                continue

            # 普通段落
            para_lines = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith('#') and not lines[i].startswith('>') and not re.match(r'^[-*+]|\d+\.|```|\|', lines[i]):
                para_lines.append(lines[i])
                i += 1
            out.append(f'<p>{"<br>".join(self._inline_markdown(l) for l in para_lines)}</p>')

        # 清理末尾
        if in_table:
            out.append(self._render_table(table_rows))
        if in_code:
            out.append('</code></pre>')

        return '\n'.join(out)

    def _inline_markdown(self, text: str) -> str:
        """行内Markdown"""
        import re
        # 粗体
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        # 斜体
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        # 行内代码
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
        # 链接
        text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
        return text

    def _render_table(self, rows: list) -> str:
        """渲染表格"""
        if not rows:
            return ''
        html = '<table>\n'
        if rows:
            html += '<tr>' + ''.join(f'<th>{self._inline_markdown(c)}</th>' for c in rows[0]) + '</tr>\n'
        for row in rows[1:]:
            html += '<tr>' + ''.join(f'<td>{self._inline_markdown(c)}</td>' for c in row) + '</tr>\n'
        html += '</table>'
        return html

    def _escape_html(self, text: str) -> str:
        """转义HTML"""
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    # ===== 主路由 =====

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed.path)

        # POST 登录接口
        if path == '/login':
            self._serve_login()
            return

        # 安全：路径穿越检测
        file_path = (WORKSPACE / path.lstrip('/')).resolve()

        if not is_safe_path(file_path):
            self.send_error(403, "Forbidden")
            return

        # 根目录 → 直接跳转dashboard
        if path == '/' or path == '':
            self.send_response(302)
            self.send_header('Location', '/dashboard-v3.html')
            self.end_headers()
            return

        # 目录 → 目录浏览
        if file_path.is_dir():
            self._serve_directory_listing(file_path, path)
            return

        # Markdown → 预览
        if file_path.suffix.lower() == '.md':
            self._serve_markdown_preview(file_path)
            return

        # 其他文件 → 静态服务
        self._serve_file(path)

    def do_POST(self):
        """处理POST（登录）"""
        self.do_GET()

    def _serve_file(self, path: str):
        """服务静态文件"""
        file_path = (WORKSPACE / path.lstrip('/')).resolve()

        if not is_safe_path(file_path) or not file_path.is_file():
            self.send_error(404, "Not Found")
            return

        ext = file_path.suffix.lower()
        content_type = MIME_MAP.get(ext, 'application/octet-stream')

        try:
            with open(file_path, 'rb') as f:
                data = f.read()

            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', len(data))
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_error(500, str(e))


def main():
    print(f"🏠 满意红 · 本地门户服务")
    print(f"   工作区: {WORKSPACE}")
    print(f"   地址:   http://localhost:{PORT}")
    print(f"   停止:   Ctrl+C")
    print(f"   启动:   {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   {'─' * 40}")

    server = ThreadingServer(('0.0.0.0', PORT), PortalHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n   {'─' * 40}")
        print(f"   已停止。")
        server.server_close()


if __name__ == '__main__':
    main()
