#!/usr/bin/env python3
"""
飞书 Token 惰性刷新 v2.0
=========================
解决飞书授权频繁丢失问题——但不过度刷新浪费Token。

策略（v2.0 优化）:
  1. 惰性刷新：只在被调用时检查 app_access_token 缓存是否<2h有效
  2. 缓存命中 → 直接用，不发起新请求
  3. 缓存过期 → 静默刷新一次
  4. 不设独立 Cron——并入飞书相关任务的 pre-step
  5. 每次 OpenClaw 飞书通道 ON 状态自动维护 app_access_token
  6. user_access_token 由 OpenClaw 飞书通道内部 OAuth 管理

参考: MEMORY.md Cron优化原则——能合并的合、能降频的降、不做主动浪费
创建于: 2026-06-04 (v1.0) · 优化: 2026-06-04 (v2.0)
"""

import json
import os
import sys
import time
import urllib.request
import urllib.parse
import urllib.error

APP_ID = 'cli_a973d0912c78dcef'
APP_SECRET = '***'

WORKSPACE = os.environ.get('SRI_WORKSPACE', os.path.expanduser('~/.openclaw/workspace'))
TOKEN_FILE = os.path.join(WORKSPACE, 'memory/_data/feishu_user_token.json')
APP_TOKEN_FILE = '/tmp/feishu_app_token.txt'

# app_access_token 缓存多久 (秒) — 飞书返回 expire=7200，缓存 7000s
APP_TOKEN_TTL = 7000


def get_app_token() -> str | None:
    """
    获取 app_access_token (应用身份)。
    惰性策略: 缓存有效则直接返回，过期才刷新。
    """
    if os.path.exists(APP_TOKEN_FILE):
        try:
            mtime = os.path.getmtime(APP_TOKEN_FILE)
            age = time.time() - mtime
            if age < APP_TOKEN_TTL:
                with open(APP_TOKEN_FILE) as f:
                    return f.read().strip()
        except:
            pass

    # 缓存过期或不存在 → 获取新 token
    data = {
        'app_id': APP_ID,
        'app_secret': APP_SECRET
    }
    req = urllib.request.Request(
        'https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal',
        data=json.dumps(data).encode(),
        headers={'Content-Type': 'application/json; charset=utf-8'}
    )
    try:
        resp = urllib.request.urlopen(req)
        body = json.loads(resp.read())
        if body.get('code') == 0:
            token = body['app_access_token']
            os.makedirs(os.path.dirname(APP_TOKEN_FILE), exist_ok=True)
            with open(APP_TOKEN_FILE, 'w') as f:
                f.write(token)
            return token
    except Exception as e:
        print(f'Failed to get app_token: {e}', file=sys.stderr)
    return None


def get_cached_token_age() -> int | None:
    """返回缓存 token 的年龄（秒），无缓存返回 None"""
    if not os.path.exists(APP_TOKEN_FILE):
        return None
    return int(time.time() - os.path.getmtime(APP_TOKEN_FILE))


def status() -> dict:
    """返回当前 token 状态（不主动刷新）"""
    age = get_cached_token_age()
    return {
        'app_token': {
            'available': age is not None,
            'age_seconds': age,
            'remaining_seconds': max(0, APP_TOKEN_TTL - (age or APP_TOKEN_TTL)),
            'needs_refresh': age is None or (age or 0) >= APP_TOKEN_TTL
        },
        'oauth_config': {
            'app_id': APP_ID,
            'oauth_url': (
                'https://accounts.feishu.cn/open-apis/authen/v1/authorize'
                f'?client_id={APP_ID}'
                '&response_type=code'
                '&redirect_uri=http://127.0.0.1:9292/callback'
                '&scope=im:message%20im:message:send_as_bot%20drive:drive%20'
                'docs:doc%20bitable:app%20calendar:calendar%20im:resource%20'
                'im:chat:readonly%20offline_access'
                '&state=openclaw_feishu_auth'
            )
        }
    }


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'

    if cmd == 'status':
        print(json.dumps(status(), indent=2, ensure_ascii=False))
    elif cmd == 'app-token':
        token = get_app_token()
        if token:
            print(token[:30] + '...')
        else:
            print('FAILED')
            sys.exit(1)
    elif cmd == 'ensure':
        # 确保 token 可用（过期则刷新），由飞书相关 Cron 的 pre-step 调用
        token = get_app_token()
        if token:
            age = get_cached_token_age()
            print(f'OK (age={age}s, remaining={max(0,APP_TOKEN_TTL-age)}s)')
            sys.exit(0)
        else:
            print('FAILED')
            sys.exit(1)
    else:
        print(f'Usage: {sys.argv[0]} [status|app-token|ensure]')
        sys.exit(1)
