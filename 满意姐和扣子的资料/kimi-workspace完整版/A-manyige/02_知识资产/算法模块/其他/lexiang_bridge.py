#!/usr/bin/env python3
"""
腾讯乐享知识库 Skill 桥接器
用途：自动加载凭证、获取 Token、调用乐享 API
用法：python3 lexiang_bridge.py <action> [args]
"""

import os
import sys
import json
import time
from pathlib import Path

# 优先使用 workspace 下的 urllib 以便处理 TLS
try:
    import urllib.request
    import urllib.parse
except ImportError:
    print(json.dumps({"success": False, "error": "Python 环境缺少 urllib"}, ensure_ascii=False))
    sys.exit(1)

WORKSPACE = Path('/root/.openclaw/workspace')
ENV_FILE = WORKSPACE / '.env.lexiang'
TOKEN_CACHE = Path.home() / '.config' / 'lexiang' / 'token'

def load_env():
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k] = v
    # 也合并系统环境变量（优先级更高）
    for k in ['LEXIANG_APP_KEY', 'LEXIANG_APP_SECRET', 'LEXIANG_STAFF_ID']:
        if os.environ.get(k):
            env[k] = os.environ[k]
    return env

def get_token(app_key: str, app_secret: str) -> str:
    """获取乐享 access_token，返回 token 字符串"""
    url = "https://lxapi.lexiangla.com/cgi-bin/token"
    data = json.dumps({
        "grant_type": "client_credentials",
        "app_key": app_key,
        "app_secret": app_secret
    }).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={
        "Content-Type": "application/json; charset=utf-8"
    }, method='POST')
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode('utf-8'))
        token = body.get('access_token')
        if not token:
            raise RuntimeError(f"获取 token 失败: {body}")
        return token

def ensure_token(env: dict) -> str:
    """确保有有效的 token（优先缓存）"""
    TOKEN_CACHE.parent.mkdir(parents=True, exist_ok=True)
    if TOKEN_CACHE.exists():
        age = time.time() - TOKEN_CACHE.stat().st_mtime
        if age < 7000:
            return TOKEN_CACHE.read_text().strip()
    app_key = env.get('LEXIANG_APP_KEY', '')
    app_secret = env.get('LEXIANG_APP_SECRET', '')
    if not app_key or not app_secret:
        raise RuntimeError("缺少 LEXIANG_APP_KEY 或 LEXIANG_APP_SECRET，请先配置 .env.lexiang")
    token = get_token(app_key, app_secret)
    TOKEN_CACHE.write_text(token)
    return token

def api_request(method: str, path: str, token: str, staff_id: str = None, payload: dict = None) -> dict:
    """调用乐享 API"""
    url = f"https://lxapi.lexiangla.com/cgi-bin{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    if staff_id:
        headers["x-staff-id"] = staff_id
    data = json.dumps(payload).encode('utf-8') if payload else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))

def action_list_teams(token: str, staff_id: str):
    r = api_request('GET', '/v1/teams', token, staff_id)
    teams = r.get('data', [])
    return {"success": True, "count": len(teams), "teams": [{"id": t.get('id'), "name": t.get('attributes', {}).get('name')} for t in teams]}

def action_list_spaces(token: str, staff_id: str, team_id: str = None):
    if not team_id:
        # 自动获取第一个团队的 ID
        teams_res = action_list_teams(token, staff_id)
        teams = teams_res.get('teams', [])
        if teams:
            team_id = teams[0]['id']
        else:
            return {"success": True, "count": 0, "spaces": [], "note": "未找到任何团队"}
    query = f"team_id={team_id}"
    path = f"/v1/kb/spaces?{query}"
    r = api_request('GET', path, token, staff_id)
    spaces = r.get('data', [])
    return {"success": True, "count": len(spaces), "spaces": [{"id": s.get('id'), "name": s.get('attributes', {}).get('name')} for s in spaces], "team_id": team_id}

def action_create_entry(token: str, staff_id: str, space_id: str, name: str, entry_type: str = "page", parent_id: str = None, content: str = None):
    if not staff_id:
        return {"success": False, "error": "写操作需要 LEXIANG_STAFF_ID"}
    payload = {
        "data": {
            "type": "kb_entry",
            "attributes": {"entry_type": entry_type, "name": name}
        }
    }
    if content:
        payload["data"]["attributes"]["content"] = content
    rels = {"space": {"data": {"type": "kb_space", "id": space_id}}}
    if parent_id:
        rels["parent_entry"] = {"data": {"type": "kb_entry", "id": parent_id}}
    payload["data"]["relationships"] = rels
    r = api_request('POST', f'/v1/kb/entries?space_id={space_id}', token, staff_id, payload)
    return {"success": True, "entry": {"id": r.get('data', {}).get('id'), **r}}

def action_list_entries(token: str, staff_id: str, space_id: str, parent_id: str = None):
    query = f"space_id={space_id}"
    if parent_id:
        query += f"&parent_entry_id={parent_id}"
    r = api_request('GET', f'/v1/kb/entries?{query}', token, staff_id)
    entries = r.get('data', [])
    return {"success": True, "count": len(entries), "entries": [{"id": e.get('id'), "type": e.get('attributes', {}).get('entry_type'), "name": e.get('attributes', {}).get('name')} for e in entries]}

def main():
    if len(sys.argv) < 2:
        print("用法: python3 lexiang_bridge.py <action> [args]")
        print("")
        print("actions:")
        print("  list-teams                              列出团队")
        print("  list-spaces [--team-id <id>]            列出知识库")
        print("  list-entries --space-id <id>           列出知识条目")
        print("  create-entry --space-id <id> --name <name> [--type page|file|folder] [--parent-id <id>]")
        print("")
        print("前置条件:")
        print("  配置 .env.lexiang 文件（LEXIANG_APP_KEY, LEXIANG_APP_SECRET, LEXIANG_STAFF_ID）")
        print("示例:")
        print('  python3 lexiang_bridge.py list-teams')
        sys.exit(0)
    
    env = load_env()
    try:
        token = ensure_token(env)
    except RuntimeError as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    staff_id = env.get('LEXIANG_STAFF_ID', '')
    action = sys.argv[1]
    args = sys.argv[2:]
    opts = {}
    i = 0
    while i < len(args):
        if args[i].startswith('--') and i + 1 < len(args):
            key = args[i][2:].replace('-', '_')
            opts[key] = args[i + 1]
            i += 2
        else:
            i += 1
    
    try:
        if action == 'list-teams':
            result = action_list_teams(token, staff_id)
        elif action == 'list-spaces':
            result = action_list_spaces(token, staff_id, opts.get('team_id'))
        elif action == 'list-entries':
            result = action_list_entries(token, staff_id, opts['space_id'], opts.get('parent_id'))
        elif action == 'create-entry':
            result = action_create_entry(token, staff_id, opts['space_id'], opts['name'], opts.get('type', 'page'), opts.get('parent_id'))
        else:
            result = {"success": False, "error": f"Unknown action: {action}"}
    except Exception as e:
        result = {"success": False, "error": str(e)}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get('success') else 1)

if __name__ == '__main__':
    main()
