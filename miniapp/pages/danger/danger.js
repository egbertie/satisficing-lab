Page({
  data: {
    current: 0, selectedIndex: null, progress: 0, answers: {},
    showResult: false, result: {}, resultAvg: 0, resultBarColor: '', signalCounts: [],
    questions: [
      {text:"你多久和合伙人进行一次深度沟通（不是群聊、不是邮件、不是开会）？", options:["每周","每月","每季度","半年","几乎不"]},
      {text:"合伙人有没有过「说好了这样，但后来做的又不一样」的情况？", options:["从来没有","偶尔一次","有过几次","经常","几乎每次都这样"]},
      {text:"你们两个对「成功」的定义一样吗？", options:["完全一样","大致一样","有点不同","很不同","完全不一样"]},
      {text:"如果公司明天估值翻十倍，他还会留吗？", options:["肯定会","大概率会","不确定","可能不会","肯定不会"]},
      {text:"你跟别人聊天时，抱怨过这个合伙人的次数？", options:["从来没有","极少","偶尔","经常","每周都在抱怨"]},
      {text:"他有没有在你不在场的场合，把团队的功劳说成自己的？", options:["从来没有","偶尔一次","有过几次","经常","几乎只说自己"]},
      {text:"你信任他多还是他信任你多？", options:["完全互相信任","我信任他更多","差不多","他信任我更多","都不太信任"]},
      {text:"你有过「想和他谈这件事，但觉得算了」的时刻吗？", options:["从来没有","极少","偶尔","经常","几乎每次都是"]},
      {text:"如果公司亏钱了，他会怎么反应？", options:["一起扛","想办法解决","先分析原因","开始推责任","他大概率会走"]},
      {text:"他的家庭（或伴侣）对他在公司的投入怎么看？", options:["全力支持","支持","一般","有点意见","多次吵架"]},
      {text:"你们有没有因为对「钱该怎么分」有分歧而吵过？", options:["从来没有","偶尔讨论","有过小分歧","吵过几次","现在还在吵"]},
      {text:"他现在对公司的热情，跟最初比是？", options:["更热情了","一样热情","差不多","稍微淡了","明显降温了"]},
      {text:"如果有一个更好的机会，你觉得他会怎么选？", options:["他会先跟我说","他会和我商量","他自己决定","他可能不会说","他已经有别的想法"]},
      {text:"在「用人」这件事上，你们的判断一致吗？", options:["几乎完全一致","大部分一致","有时不一致","经常不一致","完全不一致"]},
      {text:"你回答这些问题的时候，心里慌吗？", options:["完全不慌","有点慌","挺慌的","很慌","我现在需要喝一杯"]}
    ],
    conflictTypes: {
      low: {name:"相对健康",icon:"🟢",desc:"你的合伙人关系正处在健康区间。没有明显的系统风险信号。建议定期做踩雷检测，保持现状。",action:"继续保持沟通频率，每季度做一次踩雷复检。"},
      mid: {name:"需要关注",icon:"🟡",desc:"你的合伙人关系存在一些需要关注的信号。不是紧急的，但不能再忽视了。建议尽早做一次坦诚的深度对话。",action:"本周内找合伙人进行一场深度沟通，不谈业务，只谈关系。"},
      high: {name:"高危预警",icon:"🔴",desc:"你的合伙人关系存在多个危险信号。这些问题不会自己消失——只会积累到爆发。建议暂停重大决策，先解决合伙人关系问题。",action:"强烈建议启动蓝军审计。找一个第三方，以独立视角审视你们的合伙关系。"}
    }
  },
  onLoad() { this.updateProgress() },
  selectOption(e) {
    this.setData({ selectedIndex: e.currentTarget.dataset.index, [`answers.${this.data.current}`]: e.currentTarget.dataset.index + 1 })
  },
  next() {
    if (this.data.selectedIndex === null) return
    this.setData({ current: this.data.current + 1, selectedIndex: null })
    this.updateProgress()
  },
  prev() {
    this.setData({ current: this.data.current - 1, selectedIndex: null })
    this.updateProgress()
  },
  updateProgress() {
    this.setData({ progress: Math.round(this.data.current / this.data.questions.length * 100) })
  },
  submit() {
    if (this.data.selectedIndex === null) return
    this.setData({ [`answers.${this.data.current}`]: this.data.selectedIndex + 1 })
    const vals = Object.values(this.data.answers)
    const total = vals.reduce((a,b)=>a+b,0)
    const avg = Math.round(total / (vals.length * 5) * 100)
    
    let result, barColor
    if (avg <= 40) { result = this.data.conflictTypes.low; barColor = '#10B981' }
    else if (avg <= 65) { result = this.data.conflictTypes.mid; barColor = '#F59E0B' }
    else { result = this.data.conflictTypes.high; barColor = '#EF4444' }

    // 信号分布
    const signals = [
      {label:"信任信号", idxs:[0,6,7,12]},
      {label:"沟通信号", idxs:[1,4,5,10]},
      {label:"承诺信号", idxs:[2,3,8,11]},
      {label:"压力信号", idxs:[9,13,14]}
    ]
    const signalCounts = signals.map(s => ({
      label: s.label,
      count: vals.filter((_,i) => s.idxs.includes(i) && vals[i] >= 4).length,
      total: s.idxs.length
    }))

    this.setData({ showResult: true, result, resultAvg: avg, resultBarColor: barColor, signalCounts })
  },
  retake() {
    this.setData({ current: 0, selectedIndex: null, progress: 0, answers: {}, showResult: false })
  }
})
