"""
满意解研究所 · 飞书邮箱集成 v1.0
==============================
通过飞书开放平台 API 发送邮件
需要 user_access_token（以用户身份发信）

SMTP备选方案：
  smtp.feishu.cn:465 (SSL)
  专用密码在飞书邮箱设置中生成
"""
import json, requests, smtplib, base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from server.config import FEISHU_APP_ID, FEISHU_APP_SECRET
from server.models.database import execute


# ═══════════════════════════════════════
# 飞书 API 方式发信（优先）
# ═══════════════════════════════════════

def send_email_api(to_email: str, to_name: str, subject: str,
                   body_html: str = "", body_text: str = "",
                   user_token: str = None, cc: list = None) -> dict:
    """
    通过飞书 API 发送邮件
    需要: user_access_token（已授权 mail:user_mailbox.message:send 权限）
    """
    if not user_token:
        # 尝试从缓存获取
        try:
            tokens = json.load(open("/tmp/feishu_user_tokens.json"))
            user_token = tokens.get("access_token")
        except:
            return {"ok": False, "error": "缺少 user_access_token"}
    
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    body = {
        "subject": subject,
        "to": [{"mail_address": to_email, "name": to_name}],
    }
    
    if body_html:
        body["body_html"] = body_html
    if body_text:
        body["body_plain_text"] = body_text
    if cc:
        body["cc"] = [{"mail_address": e} for e in cc]
    
    try:
        resp = requests.post(
            "https://open.feishu.cn/open-apis/mail/v1/user_mailboxes/me/messages/send",
            headers=headers, json=body
        )
        result = resp.json()
        return {"ok": result.get("code") == 0, "data": result}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ═══════════════════════════════════════
# SMTP 方式发信（备选）
# ═══════════════════════════════════════

def send_email_smtp(to_email: str, subject: str, body_html: str,
                    smtp_user: str, smtp_password: str, from_name: str = "满意解研究所") -> bool:
    """
    通过飞书 SMTP 发送邮件
    smtp_user: 你的飞书邮箱地址（如 egbertie@你的域名.com）
    smtp_password: 飞书邮箱专用密码（在飞书邮箱设置中生成，不是登录密码）
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{from_name} <{smtp_user}>"
        msg["To"] = to_email
        msg.attach(MIMEText(body_html, "html", "utf-8"))
        
        with smtplib.SMTP_SSL("smtp.feishu.cn", 465) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [to_email], msg.as_string())
        
        return True
    except Exception as e:
        print(f"SMTP 发送失败: {e}")
        return False


# ═══════════════════════════════════════
# 邮件模板
# ═══════════════════════════════════════

def email_welcome(name: str) -> str:
    """欢迎邮件"""
    return f"""<!DOCTYPE html>
<html><body style="font-family:-apple-system,sans-serif;max-width:600px;margin:0 auto;padding:24px">
<div style="text-align:center;padding:32px 0">
  <h1 style="color:#C23B22;margin:0">🔥 满意解研究所</h1>
  <p style="color:#5C5C5C;font-size:14px;margin-top:4px">火承土印·光的接力</p>
</div>
<div style="background:#FAF7F2;border-radius:12px;padding:24px;margin:16px 0">
  <h2 style="color:#2D2D2D;margin-top:0">欢迎你，{name}！</h2>
  <p style="color:#5C5C5C;line-height:1.8">感谢你选择满意解研究所。<br><br>
  作为硬科技创始人的决策教练，我们致力于让每一个「人」的决策都有据可依。</p>
  <p style="color:#5C5C5C;line-height:1.8">你现在可以：</p>
  <ul style="color:#5C5C5C;line-height:2">
    <li>🧭 <strong>五维决策自评</strong> — 3分钟了解你的决策模式</li>
    <li>🤝 <strong>合伙人匹配诊断</strong> — 科学评估适配度</li>
    <li>📊 <strong>323+ 决策工具</strong> — 覆盖选人/用人/留人全周期</li>
  </ul>
</div>
<div style="text-align:center;padding:16px">
  <a href="https://egbertie.github.io/satisficing-lab/assessment.html" 
     style="display:inline-block;background:#C23B22;color:#fff;padding:12px 32px;border-radius:8px;text-decoration:none;font-weight:600">
    开始你的第一次决策自评 →
  </a>
</div>
<div style="text-align:center;padding:16px;color:#999;font-size:11px">
  <p>满意解研究所 · 让每个合伙人决策都有据可依</p>
  <p>如需帮助，请回复此邮件或加入我们的飞书群</p>
</div>
</body></html>"""


def email_inquiry_reply(name: str) -> str:
    """留言自动回复"""
    return f"""<!DOCTYPE html>
<html><body style="font-family:-apple-system,sans-serif;max-width:600px;margin:0 auto;padding:24px">
<h2 style="color:#C23B22">收到你的留言了，{name}！</h2>
<p style="color:#5C5C5C;line-height:1.8">
  感谢你联系满意解研究所。<br><br>
  我们会在 <strong>24 小时内</strong> 回复你的咨询。<br>
  如果紧急，可以直接加入我们的飞书群交流。
</p>
<div style="margin:24px 0;padding:16px;background:#FAF7F2;border-radius:8px">
  <p style="color:#2D2D2D;margin:0">📧 hello@satisficing.io（待配置）<br>💬 飞书搜索「满意解研究所」</p>
</div>
<p style="color:#999;font-size:11px">满意解研究所 · 火承土印·光的接力</p>
</body></html>"""


def email_delivery(product_name: str, download_url: str) -> str:
    """产品交付邮件"""
    return f"""<!DOCTYPE html>
<html><body style="font-family:-apple-system,sans-serif;max-width:600px;margin:0 auto;padding:24px">
<h2 style="color:#C23B22">📦 你的产品已就绪</h2>
<p style="color:#5C5C5C;line-height:1.8">
  你订购的 <strong>{product_name}</strong> 已准备完成。
</p>
<div style="text-align:center;margin:24px 0">
  <a href="{download_url}" 
     style="display:inline-block;background:#C23B22;color:#fff;padding:12px 32px;border-radius:8px;text-decoration:none;font-weight:600">
    查看产品 →
  </a>
</div>
<p style="color:#999;font-size:11px">如有疑问，请回复此邮件</p>
</body></html>"""


def email_referral_invite(referrer_name: str, referral_link: str) -> str:
    """转介绍邀请邮件"""
    return f"""<!DOCTYPE html>
<html><body style="font-family:-apple-system,sans-serif;max-width:600px;margin:0 auto;padding:24px">
<h2 style="color:#C23B22">{referrer_name} 邀请你体验满意解研究所</h2>
<p style="color:#5C5C5C;line-height:1.8">
  你的朋友觉得满意解研究所的决策工具可能对你有帮助。<br><br>
  🔥 <strong>3分钟了解你的决策模式</strong>，科学评估合伙人适配度。
</p>
<div style="text-align:center;margin:24px 0">
  <a href="{referral_link}" 
     style="display:inline-block;background:#C23B22;color:#fff;padding:12px 32px;border-radius:8px;text-decoration:none;font-weight:600">
    免费体验 →
  </a>
</div>
<p style="color:#999;font-size:11px">满意解研究所 · 让每个合伙人决策都有据可依</p>
</body></html>"""


# ═══════════════════════════════════════
# 邮件日志
# ═══════════════════════════════════════

def log_email(customer_id: int, to_email: str, to_name: str, subject: str,
              template_id: str, category: str, status: str = "sent", metadata: dict = None):
    execute("""
        INSERT INTO email_logs (customer_id, to_email, to_name, subject, template_id, category, status, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (customer_id, to_email, to_name, subject, template_id, category, status,
          json.dumps(metadata or {}, ensure_ascii=False)))


def get_email_stats() -> dict:
    """邮件发送统计"""
    from server.models.database import query
    return {
        "total_sent": query("SELECT COUNT(*) as c FROM email_logs")[0]["c"],
        "today_sent": query("SELECT COUNT(*) as c FROM email_logs WHERE sent_at >= date('now','localtime')")[0]["c"],
        "by_category": {r["category"]: r["c"] for r in
                        query("SELECT category, COUNT(*) as c FROM email_logs GROUP BY category")},
        "by_status": {r["status"]: r["c"] for r in
                      query("SELECT status, COUNT(*) as c FROM email_logs GROUP BY status")},
    }
