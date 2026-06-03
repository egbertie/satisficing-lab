#!/usr/bin/env python3
"""
腾讯文档 Skill 桥接器
用途：自动处理腾讯文档授权检查 + Token 获取 + MCP 配置
用法：python3 tencent_docs_bridge.py <action> [args]
"""

import os
import sys
import json
import subprocess
from pathlib import Path

WORKSPACE = Path('/root/.openclaw/workspace')
SETUP_SH = WORKSPACE / 'skills' / 'tencent-docs' / 'setup.sh'

def run_setup(step: str) -> str:
    """运行 setup.sh 的指定步骤，返回 stdout"""
    result = subprocess.run(
        ['bash', str(SETUP_SH), step],
        capture_output=True,
        text=True,
        cwd=str(SETUP_SH.parent)
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def check_auth():
    """检查授权状态"""
    stdout, stderr, rc = run_setup('tdoc_check_and_start_auth')
    # 可能包含 mcporter 安装输出，取最后一行
    lines = [l for l in stdout.splitlines() if l.strip()]
    last = lines[-1] if lines else stdout
    if last.startswith('READY'):
        return {'status': 'READY', 'message': '腾讯文档已授权，可直接使用'}
    elif last.startswith('AUTH_REQUIRED:'):
        url = last.split(':', 1)[1]
        return {'status': 'AUTH_REQUIRED', 'url': url, 'message': '需要用户授权'}
    else:
        return {'status': 'ERROR', 'output': stdout, 'stderr': stderr, 'returncode': rc}

def fetch_token():
    """用户确认授权后，获取 Token"""
    stdout, stderr, rc = run_setup('tdoc_fetch_token')
    lines = [l for l in stdout.splitlines() if l.strip()]
    last = lines[-1] if lines else stdout
    if last == 'TOKEN_READY':
        return {'status': 'TOKEN_READY', 'message': 'Token 获取成功'}
    elif last.startswith('ERROR:'):
        code = last.split(':', 1)[1]
        return {'status': 'ERROR', 'code': code, 'stdout': stdout, 'stderr': stderr}
    else:
        return {'status': 'UNKNOWN', 'output': stdout, 'stderr': stderr, 'returncode': rc}

def main():
    if len(sys.argv) < 2:
        print("用法: python3 tencent_docs_bridge.py <action>")
        print("")
        print("actions:")
        print("  check   检查授权状态")
        print("  fetch   用户授权后，获取 Token")
        print("")
        print("示例:")
        print("  python3 tencent_docs_bridge.py check")
        sys.exit(0)
    
    action = sys.argv[1]
    if action == 'check':
        data = check_auth()
    elif action == 'fetch':
        data = fetch_token()
    else:
        data = {'success': False, 'error': f'Unknown action: {action}'}
    
    print(json.dumps(data, ensure_ascii=False, indent=2))
    sys.exit(0 if data.get('status') in ('READY', 'TOKEN_READY') else 1)

if __name__ == '__main__':
    main()
