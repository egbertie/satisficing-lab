Page({
  data: {
    current: 0,
    selectedIndex: null,
    progress: 0,
    answers: {},
    questions: [
      // 时间轴
      { dim:"T", text:"短期利益和长期利益冲突时，我通常会选短期。", options:[
        {label:"1",desc:"非常符合"},{label:"2",desc:"符合"},{label:"3",desc:"一般"},{label:"4",desc:"不符合"},{label:"5",desc:"非常不符合"}
      ]},
      { dim:"T", text:"投资人催赶窗口、合伙人想冲，你更倾向于：", options:[
        {label:"1",desc:"合伙人说得对"},{label:"2",desc:"有道理"},{label:"3",desc:"中立"},{label:"4",desc:"需冷静"},{label:"5",desc:"需冷静评估"}
      ]},
      { dim:"T", text:"过去一年因'等不及'在没准备好的情况下做决定的次数：", options:[
        {label:"1",desc:"5次以上"},{label:"2",desc:"3-4次"},{label:"3",desc:"2次"},{label:"4",desc:"1次"},{label:"5",desc:"0次"}
      ]},
      // 可行域
      { dim:"D", text:"我清楚自己在合伙人决策上最多能承受的损失是多少。", options:[
        {label:"1",desc:"完全不知道"},{label:"2",desc:"大概知道"},{label:"3",desc:"有点概念"},{label:"4",desc:"比较清楚"},{label:"5",desc:"很清楚"}
      ]},
      { dim:"D", text:"技术大牛要求超出预算的股权，说'值这个价'。你：", options:[
        {label:"1",desc:"觉得有道理"},{label:"2",desc:"有点犹豫"},{label:"3",desc:"中立"},{label:"4",desc:"超出就是超出"},{label:"5",desc:"坚决不行"}
      ]},
      { dim:"D", text:"在合伙人谈判中临时改变过底线的次数：", options:[
        {label:"1",desc:"每次都变"},{label:"2",desc:"经常"},{label:"3",desc:"偶尔"},{label:"4",desc:"极少"},{label:"5",desc:"从来没有"}
      ]},
      // 身心流
      { dim:"B", text:"做重要决策时，我会注意身体的感觉并纳入考虑。", options:[
        {label:"1",desc:"几乎不"},{label:"2",desc:"偶尔"},{label:"3",desc:"有时"},{label:"4",desc:"经常"},{label:"5",desc:"决策的一部分"}
      ]},
      { dim:"B", text:"连续高强度后重大决策需立刻做。你：", options:[
        {label:"1",desc:"现在决定"},{label:"2",desc:"快速判断"},{label:"3",desc:"犹豫"},{label:"4",desc:"想休息再做"},{label:"5",desc:"知道影响，先休息"}
      ]},
      { dim:"B", text:"近三个月身体警报（失眠/头痛/胃痛）但继续冲的次数：", options:[
        {label:"1",desc:"每周都有"},{label:"2",desc:"经常"},{label:"3",desc:"偶尔"},{label:"4",desc:"极少"},{label:"5",desc:"0次"}
      ]},
      // 信义观
      { dim:"X", text:"我能说出合伙人的三件让我放心的事和三件让我打鼓的事。", options:[
        {label:"1",desc:"说不上来"},{label:"2",desc:"1-2件"},{label:"3",desc:"模糊有感觉"},{label:"4",desc:"能说大部分"},{label:"5",desc:"非常清晰"}
      ]},
      { dim:"X", text:"发现合伙人把'你们的'成绩说成'我的'。你：", options:[
        {label:"1",desc:"小事，忍了"},{label:"2",desc:"不舒服但算了"},{label:"3",desc:"记在心里"},{label:"4",desc:"要找机会谈"},{label:"5",desc:"信任问题，必须谈"}
      ]},
      { dim:"X", text:"因'不好意思'推迟和合伙人必须发生的艰难对话：", options:[
        {label:"1",desc:"推迟了多次"},{label:"2",desc:"几次"},{label:"3",desc:"一两次"},{label:"4",desc:"几乎没有"},{label:"5",desc:"从不推迟"}
      ]},
      // 直觉阈
      { dim:"Z", text:"数据和直觉打架时，我通常会听数据的。", options:[
        {label:"1",desc:"非常符合"},{label:"2",desc:"符合"},{label:"3",desc:"看情况"},{label:"4",desc:"有点抗拒"},{label:"5",desc:"非常不符合"}
      ]},
      { dim:"Z", text:"见潜在合伙人，表面完美但心里有个声音说'不对'。你：", options:[
        {label:"1",desc:"忽略"},{label:"2",desc:"记下但不管"},{label:"3",desc:"犹豫"},{label:"4",desc:"当回事"},{label:"5",desc:"深度背调"}
      ]},
      { dim:"Z", text:"有过'第一反应对但被人说服然后果然出问题'的次数：", options:[
        {label:"1",desc:"5次以上"},{label:"2",desc:"3-4次"},{label:"3",desc:"2次"},{label:"4",desc:"1次"},{label:"5",desc:"0次"}
      ]},
      // 开放题
      { dim:"开放", text:"做完这份问卷，哪个问题让你'停了一下'？", type:"text" },
      { dim:"开放", text:"你认为你的合伙人在哪个维度上和你最不同？", type:"text" },
      { dim:"开放", text:"如果只能改进一个维度，你选哪个？", type:"text" },
      // 收束
      { dim:"收束", text:"你现在对合伙人决策的危机感是：", options:[
        {label:"1",desc:"不急了"},{label:"2",desc:"还好"},{label:"3",desc:"需要关注"},{label:"4",desc:"比想的严重"},{label:"5",desc:"需要马上处理"}
      ]},
    ],
    dimNames: { T:"时间轴", D:"可行域", B:"身心流", X:"信义观", Z:"直觉阈", "开放":"开放式提问", "收束":"自我评估" }
  },

  onLoad() {
    this.updateProgress()
  },

  selectOption(e) {
    const idx = e.currentTarget.dataset.index
    const q = this.data.questions[this.data.current]
    if (!q.options) return  // 文本题跳过
    this.setData({ 
      selectedIndex: idx,
      [`answers.${this.data.current}`]: q.options[idx].label
    })
  },

  nextQuestion() {
    if (this.data.selectedIndex === null) return
    const next = this.data.current + 1
    this.setData({ current: next, selectedIndex: null })
    this.restoreAnswer(next)
    this.updateProgress()
  },

  prevQuestion() {
    const prev = this.data.current - 1
    this.setData({ current: prev, selectedIndex: null })
    this.restoreAnswer(prev)
    this.updateProgress()
  },

  restoreAnswer(idx) {
    const a = this.data.answers[idx]
    if (a) {
      const q = this.data.questions[idx]
      if (q.options) {
        const optIdx = q.options.findIndex(o => o.label === a)
        if (optIdx >= 0) this.setData({ selectedIndex: optIdx })
      }
    }
  },

  updateProgress() {
    const pct = Math.round((this.data.current / this.data.questions.length) * 100)
    this.setData({ progress: pct })
  },

  submit() {
    if (this.data.selectedIndex === null && this.data.questions[this.data.current].options) return
    
    // 保存最后一题
    const q = this.data.questions[this.data.current]
    if (q.options) {
      this.setData({ [`answers.${this.data.current}`]: q.options[this.data.selectedIndex].label })
    }

    // 计算五维得分
    const dimScores = {}
    const dimCounts = {}
    this.data.questions.forEach((q, i) => {
      if (!q.options) return
      const dim = q.dim
      if (!dimScores[dim]) { dimScores[dim] = 0; dimCounts[dim] = 0 }
      const val = parseInt(this.data.answers[i]) || 3
      dimScores[dim] += val
      dimCounts[dim]++
    })

    const scores = {}
    Object.keys(dimScores).forEach(d => {
      if (dimCounts[d] > 0) {
        scores[d] = parseFloat((dimScores[d] / dimCounts[d]).toFixed(2))
      }
    })

    // 导航到结果页
    const app = getApp()
    app.globalData.scores = scores
    wx.navigateTo({ url: '/pages/result/result' })
  }
})
