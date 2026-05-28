/**
 * 资产飞轮引擎 V1.0 · Flywheel Engine
 * 
 * 五元飞轮: Prompt → Workflow → Case → Skill → Memory
 * 四层循环: 积累 → 提炼 → 应用 → 反馈 → 再积累
 * 
 * 原理: 注入到每个HTML页面底部，自动从localStorage采集/汇总/反馈
 * 对标: 满意姐资产飞轮方案V1.0 · 54天实践纪
 */

const FlywheelEngine = {
  // ===== 积累层: 自动采集 =====
  accumulate: function(page, action, data) {
    // 1. 使用日志
    let log = JSON.parse(localStorage.getItem('sri_usage_log') || '[]');
    log.push({
      page: page,
      action: action,
      data: data ? JSON.stringify(data).substring(0, 200) : null,
      time: new Date().toISOString()
    });
    if (log.length > 1000) log = log.slice(-500); // 保留最近500条
    localStorage.setItem('sri_usage_log', JSON.stringify(log));

    // 2. 产品热度计数
    let heatmap = JSON.parse(localStorage.getItem('sri_heatmap') || '{}');
    heatmap[page] = (heatmap[page] || 0) + 1;
    localStorage.setItem('sri_heatmap', JSON.stringify(heatmap));

    // 3. 客户画像归因
    let profile = JSON.parse(localStorage.getItem('sri_profile') || '{}');
    if (profile.customerId) {
      let behaviors = JSON.parse(localStorage.getItem('sri_customer_behaviors') || '{}');
      let cid = profile.customerId;
      behaviors[cid] = behaviors[cid] || { pages: new Set(), total: 0, last: null };
      behaviors[cid].pages.add(page);
      behaviors[cid].total++;
      behaviors[cid].last = new Date().toISOString();
      // Convert Set to Array for storage
      behaviors[cid].pages = [...behaviors[cid].pages];
      localStorage.setItem('sri_customer_behaviors', JSON.stringify(behaviors));
    }
  },

  // ===== 提炼层: 自动汇总 =====
  refine: function() {
    let summary = {};
    
    // 1. 使用统计
    let log = JSON.parse(localStorage.getItem('sri_usage_log') || '[]');
    summary.totalUsage = log.length;
    summary.lastUsage = log.length > 0 ? log[log.length-1].time : null;
    
    // 2. 产品热度
    let heat = JSON.parse(localStorage.getItem('sri_heatmap') || '{}');
    summary.topProducts = Object.entries(heat)
      .sort((a,b) => b[1]-a[1])
      .slice(0, 5)
      .map(([k,v]) => ({page:k, hits:v}));
    summary.totalProducts = Object.keys(heat).length;
    
    // 3. NPS基线
    let nps = localStorage.getItem('sri_nps_score');
    summary.nps = nps ? parseInt(nps) : null;
    
    // 4. K-factor (分享归因)
    let refCount = parseInt(localStorage.getItem('sri_ref_count') || '0');
    let shares = 0;
    for (let k in localStorage) {
      if (k.startsWith('sri_fb_tally_')) {
        let d = JSON.parse(localStorage.getItem(k) || '{}');
        shares += (d.shares || 0) + (d.up || 0);
      }
    }
    summary.kFactor = shares > 0 ? (refCount / shares).toFixed(2) : null;
    summary.totalShares = shares;
    
    // 5. 反馈收集
    let feedbackCount = 0;
    for (let k in localStorage) {
      if (k.startsWith('sri_fb_tally_')) {
        let d = JSON.parse(localStorage.getItem(k) || '{}');
        feedbackCount += (d.up || 0) + (d.text || 0);
      }
    }
    summary.feedbackCount = feedbackCount;

    // 6. 客户活跃度
    let behaviors = JSON.parse(localStorage.getItem('sri_customer_behaviors') || '{}');
    let activeClients = Object.values(behaviors).filter(b => {
      let daysSinceLast = (Date.now() - new Date(b.last).getTime()) / 86400000;
      return daysSinceLast <= 30;
    }).length;
    summary.activeClients30d = activeClients;
    summary.totalClients = Object.keys(behaviors).length;
    
    return summary;
  },

  // ===== 应用层: 自动触发产品动作 =====
  apply: function(summary) {
    let actions = [];
    
    // 1. 产品热度 → 自动推荐
    if (summary.topProducts && summary.topProducts.length > 0) {
      let top = summary.topProducts[0].page;
      if (top !== 'go.html') {
        actions.push({
          type: 'promote',
          product: top,
          reason: '最受欢迎工具'
        });
      }
    }
    
    // 2. 低活跃 → 重测提醒增强
    if (summary.totalUsage > 0 && summary.totalUsage < 5) {
      actions.push({
        type: 'nudge',
        message: '你刚开始探索——要不要试试最受欢迎的工具？'
      });
    }
    
    // 3. NPS低分 → 反馈入口
    if (summary.nps !== null && summary.nps < 7) {
      actions.push({
        type: 'improve',
        message: '你的反馈对我们很重要——告诉我们哪里可以改进'
      });
    }
    
    // 4. 高活跃 → 转介绍/认证升级提示
    if (summary.totalUsage >= 10) {
      actions.push({
        type: 'upgrade',
        message: '你已经深度体验了满意解——邀请朋友解锁认证引导师'
      });
    }
    
    return actions;
  },

  // ===== 反馈层: 自动闭环通知 =====
  feedback: function(actions) {
    let now = new Date().toISOString();
    let report = {
      generated: now,
      summary: this.refine(),
      actions: actions,
      cycle: this.getCycleCount()
    };
    
    // 存储飞轮报告
    let reports = JSON.parse(localStorage.getItem('sri_flywheel_reports') || '[]');
    reports.push(report);
    if (reports.length > 100) reports = reports.slice(-50);
    localStorage.setItem('sri_flywheel_reports', JSON.stringify(reports));
    
    return report;
  },

  // ===== 飞轮循环计数 =====
  getCycleCount: function() {
    let reports = JSON.parse(localStorage.getItem('sri_flywheel_reports') || '[]');
    return reports.length;
  },

  // ===== 主入口: 每次页面加载自动运行 =====
  spin: function() {
    let page = window.location.pathname.split('/').pop() || 'go.html';
    
    // 1. 积累: 记录本次访问
    this.accumulate(page, 'pageview');
    
    // 2. 提炼: 每10次访问触发一次汇总
    let log = JSON.parse(localStorage.getItem('sri_usage_log') || '[]');
    if (log.length % 10 === 0 && log.length > 0) {
      let summary = this.refine();
      let actions = this.apply(summary);
      let report = this.feedback(actions);
      console.log('🔄 资产飞轮 · 第' + report.cycle + '轮', summary);
      
      // 如果飞轮跑了50轮，触发深度提炼标记
      if (report.cycle % 50 === 0) {
        localStorage.setItem('sri_flywheel_milestone', JSON.stringify({
          cycle: report.cycle,
          time: new Date().toISOString(),
          summary: summary
        }));
      }
    }

    // 3. 暴露方法到全局，方便在UI展示
    window.FlywheelEngine = this;
    return page;
  }
};

// 自动启动
(function(){
  FlywheelEngine.spin();
})();
