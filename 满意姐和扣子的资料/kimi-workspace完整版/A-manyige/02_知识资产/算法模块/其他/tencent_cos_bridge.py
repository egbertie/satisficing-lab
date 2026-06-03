#!/usr/bin/env python3
"""
腾讯云 COS Skill 桥接器
用途：让 Kimi Claw / OpenClaw 能够零摩擦调用已安装的 tencent-cos-skill
原理：读取 .env.tencent，自动注入环境变量，调用 skills/tencent-cos-skill/scripts/cos_node.mjs
用法：python3 tencent_cos_bridge.py <action> [options]
"""

import os
import sys
import json
import subprocess
from pathlib import Path

WORKSPACE = Path('/root/.openclaw/workspace')
ENV_FILE = WORKSPACE / '.env.tencent'
NODE_SCRIPT = WORKSPACE / 'skills' / 'tencent-cos-skill' / 'scripts' / 'cos_node.mjs'

REQUIRED_ENV = ['TENCENT_COS_SECRET_ID', 'TENCENT_COS_SECRET_KEY', 'TENCENT_COS_REGION', 'TENCENT_COS_BUCKET']

def load_env():
    """从 .env.tencent 加载凭证，如缺失则报错"""
    env = os.environ.copy()
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                env[key] = value
    missing = [k for k in REQUIRED_ENV if not env.get(k)]
    if missing:
        print(json.dumps({"success": False, "error": f"Missing env vars: {missing}"}, ensure_ascii=False))
        sys.exit(1)
    return env

def run(action: str, args: list) -> dict:
    """执行 cos_node.mjs 并解析 JSON 输出"""
    env = load_env()
    cmd = ['node', str(NODE_SCRIPT), action] + args
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=str(NODE_SCRIPT.parent))
    
    # 优先尝试解析 stdout 为 JSON
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        data = {
            "success": result.returncode == 0,
            "stdout": stdout,
            "stderr": stderr,
            "returncode": result.returncode,
        }
    
    if result.returncode != 0 and data.get("success") is not False:
        data["success"] = False
    
    return data

def main():
    if len(sys.argv) < 2:
        print("用法: python3 tencent_cos_bridge.py <action> [options]")
        print("")
        print("支持 action:")
        print("  upload      --file <路径> [--key <对象键>]")
        print("  put-string  --content <文本> --key <对象键> [--content-type <类型>]")
        print("  download    --key <对象键> [--output <本地路径>]")
        print("  list        [--prefix <前缀>] [--max-keys <数量>]")
        print("  sign-url    --key <对象键> [--expires <秒数>]")
        print("  delete      --key <对象键>")
        print("  head        --key <对象键>")
        print("")
        print("示例:")
        print('  python3 tencent_cos_bridge.py put-string --content "hello" --key test/hello.txt')
        sys.exit(0)
    
    action = sys.argv[1]
    args = sys.argv[2:]
    data = run(action, args)
    print(json.dumps(data, ensure_ascii=False, indent=2))
    sys.exit(0 if data.get("success") else 1)

if __name__ == '__main__':
    main()
