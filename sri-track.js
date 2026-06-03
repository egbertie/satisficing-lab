/**
 * 满意解研究所 · 前端事件采集 SDK v2.0
 * ====================================
 * 自动追踪页面访问、产品使用、决策行为
 * 数据自动上报到后端 → 成为数据资产
 */

(function() {
  var SRI_TRACK = {
    base: "http://127.0.0.1:5000",
    sessionId: null,
    initialized: false,
    
    init: function() {
      if (this.initialized) return;
      this.initialized = true;
      
      // 生成或恢复 session ID
      this.sessionId = sessionStorage.getItem("sri_sid");
      if (!this.sessionId) {
        this.sessionId = this._uuid();
        sessionStorage.setItem("sri_sid", this.sessionId);
      }
      
      // 开始会话
      this._post("/api/session/start", {
        entry_page: window.location.pathname,
        referrer: document.referrer,
        device: this._getDevice(),
      }).catch(function(){});
      
      // 自动上报首页访问
      this.pageView(document.title);
      
      // 监听页面卸载
      var self = this;
      window.addEventListener("beforeunload", function() {
        self._post("/api/session/end", {
          session_id: self.sessionId,
          converted: !!sessionStorage.getItem("sri_converted")
        });
      });
      
      // 监听所有链接点击（产品使用追踪）
      document.addEventListener("click", function(e) {
        var el = e.target.closest("a");
        if (el) self._clickTrack(el);
      });
    },
    
    // ─── 核心方法 ───
    pageView: function(title) {
      this.track("page_view", "page_view", title, {
        page_url: window.location.pathname + window.location.search,
        referrer: document.referrer,
      });
    },
    
    productUse: function(productId, action, data) {
      this.track("product_use", action, productId, data || {});
    },
    
    conversion: function(type, data) {
      sessionStorage.setItem("sri_converted", "1");
      this.track("conversion", type, "", data || {});
    },
    
    decision: function(type, data) {
      this.track("decision", type, "", data || {});
    },
    
    track: function(category, action, label, props) {
      this._post("/api/track", {
        session_id: this.sessionId,
        category: category,
        action: action,
        label: label || "",
        page_url: window.location.pathname,
        properties: props || {},
        device: this._getDevice(),
        client_time: new Date().toISOString(),
      }).catch(function(){});  // 静默失败，不阻塞用户体验
    },
    
    // ─── 内部方法 ───
    _post: function(path, data) {
      // 附加 token（如果已登录）
      var token = localStorage.getItem("sri_token");
      var headers = {"Content-Type": "application/json"};
      if (token) headers["Authorization"] = "Bearer " + token;
      
      return fetch(this.base + path, {
        method: "POST",
        headers: headers,
        body: JSON.stringify(data),
        keepalive: true,  // 确保页面卸载时也能发送
      });
    },
    
    _clickTrack: function(el) {
      var href = el.getAttribute("href") || "";
      var text = el.textContent.trim().slice(0, 50);
      if (href && !href.startsWith("#") && !href.startsWith("javascript:")) {
        this.track("page_view", "link_click", text, {target: href});
      }
    },
    
    _getDevice: function() {
      var w = window.innerWidth;
      return w < 768 ? "mobile" : w < 1024 ? "tablet" : "desktop";
    },
    
    _uuid: function() {
      return "s" + Date.now().toString(36) + Math.random().toString(36).slice(2, 10);
    }
  };
  
  // 页面加载后自动初始化
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function() { SRI_TRACK.init(); });
  } else {
    SRI_TRACK.init();
  }
  
  // 暴露到全局
  window.SRI_TRACK = SRI_TRACK;
})();
