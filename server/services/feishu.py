"""
满意解研究所 · 飞书集成服务
=====================
多维表格双向同步 + 群机器人通知
"""
import json
import requests
from datetime import datetime
from server.config import (
    FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_WEBHOOK,
    FEISHU_BITABLE_TOKEN, FEISHU_BITABLE_TABLE_ID
)

# 缓存 tenant_access_token
_token_cache = {"token": None, "expires_at": 0}


def _get_tenant_token() -> str:
    """获取 tenant_access_token（用于调用 API）"""
    now = datetime.now().timestamp()
    if _token_cache["token"] and _token_cache["expires_at"] > now + 60:
        return _token_cache["token"]

    resp = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}
    )
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"飞书 token 获取失败: {data}")

    _token_cache["token"] = data["tenant_access_token"]
    _token_cache["expires_at"] = now + data.get("expire", 7200)
    return _token_cache["token"]


def send_feishu_notification(title: str, blocks: list) -> bool:
    """推送富文本消息到飞书群"""
    try:
        body = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": [blocks]
                    }
                }
            }
        }
        resp = requests.post(FEISHU_WEBHOOK, json=body)
        return resp.json().get("code") == 0
    except Exception:
        return False


def send_feishu_text(text: str) -> bool:
    """推送纯文本到飞书群"""
    try:
        resp = requests.post(
            FEISHU_WEBHOOK,
            json={"msg_type": "text", "content": {"text": text}}
        )
        return resp.json().get("code") == 0
    except Exception:
        return False


def notify_new_customer(customer: dict):
    """新客户注册通知"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    blocks = [
        {"tag": "text", "text": "🎉 后端系统 · 新客户注册\n\n"},
        {"tag": "text", "text": f"👤 姓名：{customer.get('name', '未填')}\n"},
        {"tag": "text", "text": f"📧 邮箱：{customer.get('email', '未填')}\n"},
        {"tag": "text", "text": f"🏢 企业：{customer.get('company', '未填')}\n"},
        {"tag": "text", "text": f"💼 职位：{customer.get('position', '未填')}\n"},
        {"tag": "text", "text": f"🔬 赛道：{customer.get('industry', '未填')}\n"},
        {"tag": "text", "text": f"📥 来源：{customer.get('source', '未填')}\n"},
        {"tag": "text", "text": f"\n⏰ 时间：{now}\n\n"},
        {"tag": "a", "text": "📊 查看客户数据表",
         "href": f"https://gcngtm4k2m6u.feishu.cn/base/{FEISHU_BITABLE_TOKEN}"}
    ]
    return send_feishu_notification("🎉 满意解研究所 · 新客户注册（后端）", blocks)


def notify_new_inquiry(inquiry: dict):
    """新客户留言通知"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    blocks = [
        {"tag": "text", "text": "📬 后端系统 · 新客户留言\n\n"},
        {"tag": "text", "text": f"👤 姓名：{inquiry.get('name', '未填')}\n"},
        {"tag": "text", "text": f"📧 邮箱：{inquiry.get('email', '未填')}\n"},
        {"tag": "text", "text": f"🏢 企业：{inquiry.get('company', '未填')}\n"},
        {"tag": "text", "text": f"💬 留言：{inquiry.get('message', '未填')}\n"},
        {"tag": "text", "text": f"\n⏰ 时间：{now}\n"},
    ]
    return send_feishu_notification("🔔 满意解研究所 · 新客户留言（后端）", blocks)


def sync_customer_to_bitable(customer: dict) -> bool:
    """同步客户数据到飞书多维表格"""
    try:
        token = _get_tenant_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }

        # 写入记录
        fields = {
            "姓名": customer.get("name", ""),
            "邮箱": customer.get("email", ""),
            "手机": customer.get("phone", ""),
            "企业名称": customer.get("company", ""),
            "职位": customer.get("position", ""),
            "行业赛道": customer.get("industry", ""),
            "融资阶段": customer.get("stage", ""),
            "客户来源": customer.get("source", ""),
            "提交时间": int(datetime.now().timestamp() * 1000),  # 毫秒时间戳
            "处理状态": "新线索",
        }

        url = (f"https://open.feishu.cn/open-apis/bitable/v1/apps/"
               f"{FEISHU_BITABLE_TOKEN}/tables/{FEISHU_BITABLE_TABLE_ID}/records")

        resp = requests.post(url, headers=headers, json={"fields": fields})
        result = resp.json()
        return result.get("code") == 0
    except Exception:
        return False


def sync_inquiry_to_bitable(inquiry: dict) -> bool:
    """同步客户留言到飞书多维表格"""
    try:
        token = _get_tenant_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }

        fields = {
            "姓名": inquiry.get("name", ""),
            "邮箱": inquiry.get("email", ""),
            "企业名称": inquiry.get("company", ""),
            "需求描述": inquiry.get("message", ""),
            "提交时间": int(datetime.now().timestamp() * 1000),
            "处理状态": "新线索",
        }

        url = (f"https://open.feishu.cn/open-apis/bitable/v1/apps/"
               f"{FEISHU_BITABLE_TOKEN}/tables/{FEISHU_BITABLE_TABLE_ID}/records")

        resp = requests.post(url, headers=headers, json={"fields": fields})
        return resp.json().get("code") == 0
    except Exception:
        return False
