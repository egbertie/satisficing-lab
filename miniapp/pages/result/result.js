Page({
  data: {
    names: { T:"时间轴", D:"可行域", B:"身心流", X:"信义观", Z:"直觉阈" },
    colors: { T:"#3B82F6", D:"#10B981", B:"#F59E0B", X:"#EF4444", Z:"#8B5CF6" },
    dimOrder: ["T","D","B","X","Z"],
    scores: {},
    avgScore: 0,
    pattern: null
  },

  onLoad() {
    const app = getApp()
    if (!app.globalData.scores) {
      wx.showToast({ title: '请先完成测评', icon: 'none' })
      setTimeout(() => wx.navigateBack(), 1500)
      return
    }

    const scores = app.globalData.scores
    const vals = Object.values(scores)
    const avg = vals.length ? parseFloat((vals.reduce((a,b)=>a+b,0)/vals.length).toFixed(2)) : 0

    const levels = {}
    for (let d in scores) {
      const s = scores[d]
      if (s >= 4.5) levels[d] = '🟢卓越'
      else if (s >= 3.5) levels[d] = '🟢健康'
      else if (s >= 2.5) levels[d] = '🟡临界'
      else if (s >= 1.5) levels[d] = '🟠关注'
      else levels[d] = '🔴高危'
    }

    const pattern = this.detectPattern(scores)

    this.setData({ scores, levels, avgScore: avg, pattern })
    this.drawRadar(scores)
  },

  detectPattern(scores) {
    const vs = Object.values(scores).sort((a,b)=>a-b)
    const range = vs[vs.length-1] - vs[0]
    if (range < 1.0) return { icon:"⚖️", name:"均衡型", desc:"五维得分接近，决策风格均衡，无系统盲区。", recommend:"使用全能组卡牌，关注脱轨因子检测。" }
    if (vs[vs.length-1] - vs[vs.length-2] > 1.2) return { icon:"⛰️", name:"单峰型", desc:"某一维度显著突出，可能过度依赖该维度。", recommend:"使用广度拓展组卡牌，刻意练习其他维度。" }
    if (vs[1] - vs[0] > 1.2) return { icon:"🕳️", name:"缺口型", desc:"某一维度显著落后，存在系统盲区。", recommend:"使用缺口补防组卡牌，配置合伙人补偿机制。" }
    return { icon:"🔀", name:"锯齿型", desc:"高低交替明显，有依赖维度也有回避维度。", recommend:"用强项维度带动弱项，使用针对性补弱组卡牌。" }
  },

  drawRadar(scores) {
    const query = wx.createSelectorQuery()
    query.select('#radarCanvas').fields({ node: true, size: true }).exec((res) => {
      if (!res[0]) return
      const canvas = res[0].node
      const ctx = canvas.getContext('2d')
      const dpr = wx.getSystemInfoSync().pixelRatio
      const w = res[0].width
      const h = res[0].height
      canvas.width = w * dpr
      canvas.height = h * dpr
      ctx.scale(dpr, dpr)

      const cx = w / 2, cy = h / 2 - 10
      const maxR = Math.min(w, h) * 0.35
      const dims = ["T","D","B","X","Z"]
      const n = dims.length
      const angles = dims.map((_,i)=> Math.PI*1.5 + 2*Math.PI*i/n)

      // 网格
      for (let lvl = 1; lvl <= 5; lvl++) {
        const r = maxR * lvl / 5
        ctx.beginPath()
        angles.forEach((a,i) => {
          const x = cx + r*Math.cos(a), y = cy + r*Math.sin(a)
          i === 0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y)
        })
        ctx.closePath()
        ctx.strokeStyle = lvl === 5 ? '#475569' : '#334155'
        ctx.lineWidth = lvl === 5 ? 1.5 : 0.5
        ctx.stroke()
      }

      // 轴线
      angles.forEach(a => {
        ctx.beginPath()
        ctx.moveTo(cx, cy)
        ctx.lineTo(cx + maxR*Math.cos(a), cy + maxR*Math.sin(a))
        ctx.strokeStyle = '#334155'
        ctx.lineWidth = 0.5
        ctx.stroke()
      })

      // 数据面
      ctx.beginPath()
      dims.forEach((d,i) => {
        const s = scores[d] || 3
        const r = maxR * s / 5
        const x = cx + r*Math.cos(angles[i]), y = cy + r*Math.sin(angles[i])
        i === 0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y)
      })
      ctx.closePath()
      ctx.fillStyle = 'rgba(194,59,34,0.15)'
      ctx.fill()
      ctx.strokeStyle = '#C23B22'
      ctx.lineWidth = 2
      ctx.stroke()

      // 点+值
      dims.forEach((d,i) => {
        const s = scores[d] || 3
        const r = maxR * s / 5
        const x = cx + r*Math.cos(angles[i]), y = cy + r*Math.sin(angles[i])
        ctx.beginPath()
        ctx.arc(x, y, 6, 0, Math.PI*2)
        ctx.fillStyle = this.data.colors[d]
        ctx.fill()
        ctx.fillStyle = '#0f172a'
        ctx.arc(x, y, 3, 0, Math.PI*2)
        ctx.fill()
        ctx.font = 'bold 12px sans-serif'
        ctx.fillStyle = this.data.colors[d]
        ctx.textAlign = 'center'
        ctx.fillText(s.toFixed(1), x, y - 14)
      })

      // 标签
      const lr = maxR + 30
      ctx.font = 'bold 13px sans-serif'
      ctx.textAlign = 'center'
      dims.forEach((d,i) => {
        const lx = cx + lr*Math.cos(angles[i]), ly = cy + lr*Math.sin(angles[i])
        ctx.fillStyle = this.data.colors[d]
        ctx.fillText(this.data.names[d], lx, ly + 5)
      })
    })
  },

  retake() {
    wx.navigateBack()
  }
})
