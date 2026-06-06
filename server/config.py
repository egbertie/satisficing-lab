"""
满意解研究所 · 后端配置中心
=========================
所有环境变量和配置统一管理
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SERVER_DIR = BASE_DIR / "server"
DATA_DIR = BASE_DIR / "memory" / "_data"

# === 飞书配置 ===
FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID", "cli_a973d0912c78dcef")
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")
FEISHU_WEBHOOK = os.environ.get("FEISHU_WEBHOOK", "")

# 飞书多维表格（客户数据中心）
FEISHU_BITABLE_TOKEN = os.environ.get("FEISHU_BITABLE_TOKEN", "")
FEISHU_BITABLE_TABLE_ID = os.environ.get("FEISHU_BITABLE_TABLE_ID", "")

# === 数据库 ===
DATABASE_PATH = SERVER_DIR / "data" / "sri.db"
DATABASE_URI = f"sqlite:///{DATABASE_PATH}"

# === JWT 认证 ===
JWT_SECRET = os.environ.get("SRI_JWT_SECRET", "sri-dev-secret-change-in-production")
JWT_EXPIRES_HOURS = 72

# === 服务器 ===
HOST = "127.0.0.1"
PORT = int(os.environ.get("SRI_PORT", 5050))
DEBUG = os.environ.get("SRI_DEBUG", "false").lower() == "true"

# === CORS ===
CORS_ORIGINS = [
    "http://localhost:8766",      # dev.sh 本地测试
    "http://127.0.0.1:8766",
    "https://egbertie.github.io",  # GitHub Pages
    "http://localhost:5000",
]

# === 产品交付 ===
# 客户可下载的文件存放目录
DELIVERY_DIR = BASE_DIR / "delivery"
DELIVERY_DIR.mkdir(exist_ok=True)

# === 客户角色 ===
CUSTOMER_ROLES = ["trial", "free", "premium", "vip", "partner"]
CUSTOMER_ROLE_PRODUCTS = {
    "trial": ["assessment"],           # 试用：只能自评
    "free": ["assessment", "radar"],   # 免费：自评+雷达
    "premium": ["assessment", "radar", "cards", "match"],  # 付费：核心工具
    "vip": ["*"],                      # VIP：全部
    "partner": ["*"],                  # 合伙人：全部+管理
}
