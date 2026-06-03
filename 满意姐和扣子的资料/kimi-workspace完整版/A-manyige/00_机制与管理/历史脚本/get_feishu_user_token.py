#!/usr/bin/env python3
"""
获取飞书 User Access Token
运行此脚本，按提示操作即可
"""

import json
import requests
import urllib.parse
import webbrowser
import http.server
import socketserver
import threading
import time

# 配置
APP_ID = "cli_a927c5dfa4381cc6"
APP_SECRET = "8950yzh6jj17nQkKBjvGIdRocdrslhjI"
REDIRECT_URI = "http://localhost:8080/callback"

# 全局变量存储code
auth_code = None

class CallbackHandler(http.server.SimpleHTTPRequestHandler):
    """处理OAuth回调"""
    def do_GET(self):
        global auth_code
        
        if "/callback" in self.path:
            # 解析URL参数
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            
            if 'code' in params:
                auth_code = params['code'][0]
                
                # 返回成功页面
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(b"""
                <html>
                <head><title>授权成功</title></head>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: green;">✅ 授权成功！</h1>
                    <p>请返回终端查看结果</p>
                    <p>可以关闭此页面</p>
                </body>
                </html>
                """)
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Error: No code received")
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # 静默日志

def start_callback_server():
    """启动回调服务器"""
    with socketserver.TCPServer(("", 8080), CallbackHandler) as httpd:
        print("🔌 回调服务器已启动 (localhost:8080)")
        httpd.handle_request()  # 只处理一个请求

def get_user_token():
    """获取用户Token的完整流程"""
    global auth_code
    
    print("="*60)
    print("飞书 User Access Token 获取工具")
    print("="*60)
    
    # 步骤1: 生成授权URL
    params = {
        "app_id": APP_ID,
        "redirect_uri": REDIRECT_URI,
        "state": "random_state_123"
    }
    auth_url = "https://open.feishu.cn/open-apis/oauthen/authorize?" + urllib.parse.urlencode(params)
    
    print("\n步骤1: 请在浏览器中访问以下URL并授权")
    print("-"*60)
    print(auth_url)
    print("-"*60)
    
    # 自动打开浏览器（如果可以）
    try:
        webbrowser.open(auth_url)
        print("已尝试自动打开浏览器")
    except:
        print("请手动复制上面的URL到浏览器")
    
    # 步骤2: 启动回调服务器等待授权
    print("\n步骤2: 等待授权回调...")
    print("请在浏览器中登录飞书并点击'同意授权'")
    
    # 启动服务器
    server_thread = threading.Thread(target=start_callback_server)
    server_thread.daemon = True
    server_thread.start()
    
    # 等待code
    timeout = 120  # 2分钟超时
    start_time = time.time()
    
    while auth_code is None and time.time() - start_time < timeout:
        time.sleep(1)
    
    if auth_code is None:
        print("❌ 超时：未收到授权回调")
        return None
    
    print(f"✅ 授权成功，获得code: {auth_code[:20]}...")
    
    # 步骤3: 用code换token
    print("\n步骤3: 用code换取access_token...")
    
    url = "https://open.feishu.cn/open-apis/oauthen/v1/access_token"
    data = {
        "grant_type": "authorization_code",
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "code": auth_code,
        "redirect_uri": REDIRECT_URI
    }
    
    resp = requests.post(url, json=data)
    result = resp.json()
    
    if result.get("code") == 0:
        access_token = result["data"]["access_token"]
        refresh_token = result["data"].get("refresh_token", "")
        expires_in = result["data"].get("expires_in", 7200)
        
        print("\n" + "="*60)
        print("🎉 成功获取 User Access Token!")
        print("="*60)
        print(f"\n⚠️  请保存以下信息（只显示一次）：")
        print("-"*60)
        print(f"Access Token:  {access_token}")
        print(f"Refresh Token: {refresh_token}")
        print(f"有效期: {expires_in}秒 ({expires_in//3600}小时)")
        print("-"*60)
        print("\n使用方法：")
        print(f"将access_token发给AI，替换所有tenant_token的地方")
        print("\n刷新方法（token过期后）：")
        print(f"curl -X POST https://open.feishu.cn/open-apis/oauthen/v1/refresh_access_token \\")
        print(f"  -d '{{\"grant_type\": \"refresh_token\", \"refresh_token\": \"{refresh_token}\"}}'")
        
        return access_token
    else:
        print(f"❌ 获取token失败: {result.get('msg')}")
        return None

if __name__ == "__main__":
    try:
        token = get_user_token()
        if token:
            print("\n✅ 完成！请将access_token复制给AI。")
        else:
            print("\n❌ 失败，请重试。")
    except KeyboardInterrupt:
        print("\n\n已取消")
    except Exception as e:
        print(f"\n❌ 错误: {e}")