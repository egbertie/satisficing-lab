/**
 * 满意解研究所 · 前端 API SDK v1.0
 * ================================
 * 封装所有后端 API 调用，统一处理 token 和错误
 */

const SRI_API = {
  base: "http://127.0.0.1:5050",
  // 部署到腾讯云后改为: "https://api.你的域名.com"

  tokenKey: "sri_token",
  customerKey: "sri_customer",

  // ─── Token 管理 ───
  getToken() {
    return localStorage.getItem(this.tokenKey);
  },

  setToken(token) {
    localStorage.setItem(this.tokenKey, token);
  },

  clearToken() {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.customerKey);
  },

  getCustomer() {
    try {
      return JSON.parse(localStorage.getItem(this.customerKey) || "null");
    } catch { return null; }
  },

  setCustomer(c) {
    localStorage.setItem(this.customerKey, JSON.stringify(c));
  },

  isLoggedIn() {
    return !!this.getToken();
  },

  // ─── HTTP 封装 ───
  async _fetch(path, options = {}) {
    const url = `${this.base}${path}`;
    const headers = { "Content-Type": "application/json", ...options.headers };

    // 自动附加 token
    const token = this.getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const resp = await fetch(url, { ...options, headers });
    const data = await resp.json().catch(() => ({}));

    if (!resp.ok) {
      throw { status: resp.status, ...data };
    }
    return data;
  },

  // ─── 认证 ───
  async register(fields) {
    const data = await this._fetch("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(fields)
    });
    this.setToken(data.token);
    this.setCustomer(data.customer);
    return data;
  },

  async login(email, password) {
    const data = await this._fetch("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });
    this.setToken(data.token);
    this.setCustomer(data.customer);
    return data;
  },

  async logout() {
    try { await this._fetch("/api/auth/logout", { method: "POST" }); } catch {}
    this.clearToken();
  },

  async getMe() {
    const data = await this._fetch("/api/auth/me");
    this.setCustomer(data.customer);
    return data;
  },

  // ─── 客户交互 ───
  async contact(fields) {
    return this._fetch("/api/contact", {
      method: "POST",
      body: JSON.stringify(fields)
    });
  },

  async getInquiries() {
    return this._fetch("/api/inquiries");
  },

  // ─── 档案 ───
  async getProfile() {
    const data = await this._fetch("/api/profile");
    this.setCustomer(data.customer);
    return data;
  },

  async updateProfile(fields) {
    const data = await this._fetch("/api/profile", {
      method: "PATCH",
      body: JSON.stringify(fields)
    });
    this.setCustomer(data.customer);
    return data;
  },

  // ─── 产品交付 ───
  async getDeliveries() {
    return this._fetch("/api/deliveries");
  },

  // ─── 转介绍 ───
  async createReferral() {
    return this._fetch("/api/referral/create", { method: "POST" });
  },

  async getReferrals() {
    return this._fetch("/api/referrals");
  }
};
