#!/usr/bin/env python3
"""
满意解研究所 · 本地测试服务器
=============================
模拟 GitHub Pages 的静态文件服务。
零密码、零认证、零依赖。
用法: python3 devserver.py [端口]
默认: http://localhost:8766
"""

import http.server
import os
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8766
ROOT = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]}")

print(f"🏠 满意解研究所 · 本地测试")
print(f"   路径: {ROOT}")
print(f"   地址: http://localhost:{PORT}")
print(f"   首页: http://localhost:{PORT}/index.html")
print(f"   驾驶舱: http://localhost:{PORT}/dashboard-v3.html")
print(f"   Ctrl+C 停止")
print(f"   {'=' * 40}")

http.server.HTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
