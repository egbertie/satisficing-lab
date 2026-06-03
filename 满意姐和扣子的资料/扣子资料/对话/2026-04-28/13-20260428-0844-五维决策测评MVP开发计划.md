# 五维决策测评系统 MVP开发计划

> **版本**: V1.0
> **日期**: 2026-04-28
> **编制**: 满意扣子
> **性质**: 开发计划文档

---

## 一、MVP目标

### 核心交付
> "用2周时间，上线一个可用的五维决策测评H5页面"

### MVP成功标准

| 维度 | 指标 | 目标值 |
|:----:|:----:|:------:|
| 功能 | 问卷完成率 | > 70% |
| 性能 | 页面加载时间 | < 3秒 |
| 可用性 | 雷达图展示 | 正常 |
| 可用性 | 报告生成 | 正常 |
| 可用性 | 结果保存 | 正常 |

---

## 二、MVP范围

### 2.1 功能范围

```
MVP功能范围（2周）:

┌─────────────────────────────────────────────┐
│                                             │
│  ✅ 完成以下功能:                            │
│                                             │
│  ├── 问卷展示（25题 + 3直觉题）             │
│  ├── 维度评分计算（土/金/水/木/火）         │
│  ├── 雷达图可视化                            │
│  ├── 基础报告生成                            │
│  ├── 结果本地保存                            │
│  └── 进度保存（可选）                        │
│                                             │
│  ❌ 暂不包括:                                │
│                                             │
│  ├── 用户系统                                │
│  ├── 分享功能                                │
│  ├── PDF导出                                │
│  ├── 后端API                               │
│  └── 多评估类型                              │
│                                             │
└─────────────────────────────────────────────┘
```

### 2.2 技术范围

| 层级 | MVP技术 | 完整版技术 |
|:----:|:-------:|:----------:|
| 前端 | Vue3单页应用 | Vue3 + Router |
| 样式 | TailwindCSS | TailwindCSS |
| 图表 | ECharts | ECharts |
| 存储 | localStorage | PostgreSQL + Redis |
| 部署 | Vercel | Vercel + 云服务器 |
| 域名 | 测试域名 | 正式域名 |

---

## 三、开发计划（14天）

### Day 1-2: 项目初始化

| 时间 | 任务 | 交付物 | 负责人 |
|:----:|:----:|:------:|:------:|
| Day1 AM | 项目脚手架搭建 | Vue3 + Vite项目 | 前端 |
| Day1 PM | TailwindCSS配置 | 样式系统 | 前端 |
| Day1 PM | ECharts引入 | 图表基础 | 前端 |
| Day2 AM | 问卷数据结构设计 | data/questions.ts | 前端 |
| Day2 PM | 评分算法实现 | utils/score.ts | 前端 |
| Day2 PM | 目录结构确认 | 项目结构文档 | 全员 |

**交付物检查清单**:
- [ ] Git仓库初始化
- [ ] 项目可运行
- [ ] 问卷数据结构定义
- [ ] 评分算法伪代码

---

### Day 3-5: 问卷页面开发

| 时间 | 任务 | 交付物 | 负责人 |
|:----:|:----:|:------:|:------:|
| Day3 | 首页设计 | HomeView.vue | 前端+设计 |
| Day3 | 问卷引导页 | QuizIntroView.vue | 前端 |
| Day4 | 问卷答题页 | QuizView.vue | 前端 |
| Day4 | 进度条组件 | ProgressBar.vue | 前端 |
| Day5 | 问卷逻辑 | 答题/切换/验证 | 前端 |
| Day5 | 本地存储 | 进度保存 | 前端 |

**交付物检查清单**:
- [ ] 首页可访问
- [ ] 问卷可完成
- [ ] 进度条正常
- [ ] 25题可答题
- [ ] 3道直觉题可答题

---

### Day 6-7: 报告生成开发

| 时间 | 任务 | 交付物 | 负责人 |
|:----:|:----:|:------:|:------:|
| Day6 | 雷达图组件 | RadarChart.vue | 前端 |
| Day6 | 维度评分展示 | ScoreDisplay.vue | 前端 |
| Day7 | 行动建议生成 | SuggestionEngine.ts | 前端 |
| Day7 | 结果页设计 | ResultView.vue | 前端+设计 |

**交付物检查清单**:
- [ ] 雷达图正常显示
- [ ] 五维分数正确
- [ ] 行动建议生成
- [ ] 结果页完整

---

### Day 8-10: 体验优化

| 时间 | 任务 | 交付物 | 负责人 |
|:----:|:----:|:------:|:------:|
| Day8 | 动画效果 | 页面过渡动画 | 前端 |
| Day8 | 移动端适配 | 响应式测试 | 前端 |
| Day9 | 加载状态 | Loading组件 | 前端 |
| Day9 | 空状态 | EmptyState组件 | 前端 |
| Day10 | 错误处理 | ErrorBoundary | 前端 |
| Day10 | 历史记录 | HistoryView.vue | 前端 |

**交付物检查清单**:
- [ ] 动画流畅
- [ ] 移动端可用
- [ ] 错误有提示
- [ ] 历史可查看

---

### Day 11-12: 后端API（可选）

| 时间 | 任务 | 交付物 | 负责人 |
|:----:|:----:|:------:|:------:|
| Day11 | Express框架 | 后端脚手架 | 后端 |
| Day11 | 数据库设计 | PostgreSQL表结构 | 后端 |
| Day12 | 用户API | 注册/登录/Token | 后端 |
| Day12 | 评估API | 创建/查询/列表 | 后端 |

**交付物检查清单**:
- [ ] 后端可启动
- [ ] 数据库可连接
- [ ] 注册登录可用
- [ ] 评估数据可存储

---

### Day 13-14: 联调测试

| 时间 | 任务 | 交付物 | 负责人 |
|:----:|:----:|:------:|:------:|
| Day13 | 前后端联调 | API对接 | 前端+后端 |
| Day13 | 报告保存 | 云端保存 | 后端 |
| Day14 | 功能测试 | 测试用例执行 | 测试 |
| Day14 | 性能测试 | Lighthouse报告 | 测试 |
| Day14 | Bug修复 | 已知Bug修复 | 前端+后端 |
| Day14 | 部署上线 | 正式环境 | DevOps |

**交付物检查清单**:
- [ ] 全流程可跑通
- [ ] Lighthouse > 80分
- [ ] 无P0/P1级Bug
- [ ] 可访问域名

---

## 四、技术文档

### 4.1 项目结构

```
five-dimensional-assessment/
├── public/
│   └── index.html
├── src/
│   ├── assets/              # 静态资源
│   │   ├── images/
│   │   └── styles/
│   ├── components/          # 通用组件
│   │   ├── RadarChart.vue
│   │   ├── ProgressBar.vue
│   │   ├── QuestionCard.vue
│   │   └── Loading.vue
│   ├── views/               # 页面
│   │   ├── HomeView.vue
│   │   ├── QuizIntroView.vue
│   │   ├── QuizView.vue
│   │   ├── ResultView.vue
│   │   └── HistoryView.vue
│   ├── data/                 # 问卷数据
│   │   └── questions.ts
│   ├── utils/                # 工具函数
│   │   ├── score.ts
│   │   └── storage.ts
│   ├── store/                # 状态管理
│   │   └── quiz.ts
│   ├── App.vue
│   └── main.ts
├── .env
├── vite.config.ts
├── tailwind.config.js
├── package.json
└── README.md
```

### 4.2 问卷数据结构

```typescript
// data/questions.ts

export interface Question {
  id: number;
  dimension: 'tu' | 'jin' | 'shui' | 'mu' | 'huo';
  text: string;
  options: {
    text: string;
    score: number;
  }[];
}

export const questions: Question[] = [
  // 土·信义 (5题)
  {
    id: 1,
    dimension: 'tu',
    text: '你需要多长时间才能完全信任一个新认识的合作伙伴？',
    options: [
      { text: '初次见面就能建立基础信任', score: 5 },
      { text: '经过1-3次互动后', score: 4 },
      { text: '需要几个月相处', score: 3 },
      { text: '需要超过半年', score: 2 },
      { text: '我很少完全信任任何人', score: 1 },
    ]
  },
  // ... 其他24题
];

export const intuitionQuestions: Question[] = [
  // 3道直觉题
];

export const dimensions = {
  tu: { name: '土·信义', icon: '🌍', color: '#8B4513' },
  jin: { name: '金·标尺', icon: '⚖️', color: '#FFD700' },
  shui: { name: '水·觉察', icon: '💧', color: '#1E90FF' },
  mu: { name: '木·伦理', icon: '🌲', color: '#228B22' },
  huo: { name: '火·顿悟', icon: '🔥', color: '#FF4500' },
};
```

### 4.3 评分算法

```typescript
// utils/score.ts

export interface DimensionScore {
  dimension: string;
  name: string;
  score: number;         // 当前得分
  maxScore: number;      // 满分
  level: 'excellent' | 'good' | 'average' | 'poor';
  percentage: number;     // 百分比
}

export interface AssessmentResult {
  dimensionScores: DimensionScore[];
  totalScore: number;
  maxTotalScore: number;
  radarData: number[];
  riskWarnings: string[];
  suggestions: string[];
  level: 'excellent' | 'good' | 'average' | 'poor';
}

export function calculateScore(answers: Record<number, number>): AssessmentResult {
  // 1. 按维度分组计算
  // 2. 计算维度得分
  // 3. 生成雷达图数据
  // 4. 生成风险预警
  // 5. 生成行动建议
  // 6. 返回综合结果
}

export function generateSuggestions(dimensionScores: DimensionScore[]): string[] {
  // 根据短板维度生成建议
  // 土不足 → 建议建立信任机制
  // 金不足 → 建议设定满意解标准
  // 水不足 → 建议练习0.3秒觉察
  // 木不足 → 建议建立伦理契约
  // 火不足 → 建议给自己压力deadline
}
```

### 4.4 API设计（后端）

```typescript
// API Endpoints

// 用户
POST   /api/users/register        // 注册
POST   /api/users/login           // 登录
GET    /api/users/profile         // 获取用户信息

// 评估
POST   /api/assessments           // 创建评估
GET    /api/assessments/:id       // 获取评估详情
GET    /api/assessments           // 获取评估列表
PUT    /api/assessments/:id       // 更新评估
DELETE /api/assessments/:id       // 删除评估

// 报告
GET    /api/reports/:id           // 获取报告
POST   /api/reports/:id/pdf       // 生成PDF
POST   /api/reports/:id/share     // 生成分享链接

// 分享
GET    /api/share/:token          // 通过分享Token访问
```

---

## 五、测试计划

### 5.1 功能测试用例

| 用例ID | 用例描述 | 预期结果 | 优先级 |
|:------:|:--------:|:--------:|:------:|
| TC001 | 打开首页 | 显示产品介绍和开始按钮 | P0 |
| TC002 | 点击开始评估 | 进入问卷引导页 | P0 |
| TC003 | 完成第一题 | 自动进入第二题 | P0 |
| TC004 | 返回上一题 | 可返回修改答案 | P1 |
| TC005 | 完成25题 | 进入直觉验证 | P0 |
| TC006 | 完成直觉3题 | 进入结果页 | P0 |
| TC007 | 查看雷达图 | 五维得分可视化 | P0 |
| TC008 | 查看行动建议 | 显示针对性建议 | P0 |
| TC009 | 保存结果 | 结果保存到本地 | P1 |
| TC010 | 查看历史 | 可查看历史评估 | P1 |

### 5.2 性能测试标准

| 指标 | 标准 | 测试工具 |
|:----:|:----:|:--------:|
| First Contentful Paint | < 1.5s | Lighthouse |
| Largest Contentful Paint | < 2.5s | Lighthouse |
| Time to Interactive | < 3s | Lighthouse |
| Cumulative Layout Shift | < 0.1 | Lighthouse |
| Performance Score | > 80 | Lighthouse |

### 5.3 兼容性测试

| 浏览器 | 版本 | 要求 |
|:------:|:----:|:----:|
| Chrome | 最新-1 | 完全支持 |
| Safari | 最新-1 | 完全支持 |
| Firefox | 最新-1 | 完全支持 |
| Edge | 最新-1 | 完全支持 |
| iOS Safari | 最新-1 | 完全支持 |
| Android Chrome | 最新-1 | 完全支持 |

---

## 六、里程碑

### 6.1 里程碑定义

```
里程碑时间线:

Week 1                           Week 2
┌────────────────────────────┐  ┌────────────────────────────┐
│                            │  │                            │
│  Day 1-2: 项目初始化        │  │  Day 8-10: 体验优化        │
│  ✅ 项目结构搭建           │  │  ✅ 动画和响应式           │
│  ✅ 问卷数据结构           │  │  ✅ 错误处理               │
│                            │  │                            │
│  Day 3-5: 问卷开发         │  │  Day 11-12: 后端开发       │
│  ✅ 首页和引导页           │  │  ✅ API接口                │
│  ✅ 25题+3直觉题           │  │  ✅ 数据库设计              │
│  ✅ 进度条和保存           │  │                            │
│                            │  │  Day 13-14: 联调测试       │
│  Day 6-7: 报告生成         │  │  ✅ 全流程测试             │
│  ✅ 雷达图                 │  │  ✅ 性能优化               │
│  ✅ 行动建议               │  │  ✅ 部署上线               │
│                            │  │                            │
└────────────────────────────┘  └────────────────────────────┘

M1 (Day 3)    M2 (Day 7)    M3 (Day 10)    M4 (Day 14)
   │              │              │              │
   ▼              ▼              ▼              ▼
 问卷结构     问卷+报告       体验完成        可上线MVP
 完成         完成            优化            发布
```

### 6.2 验收标准

| 里程碑 | 验收条件 | 检查方式 |
|:------:|:--------:|:--------:|
| **M1** | 问卷数据结构定义完成 | 代码审查 |
| **M2** | 可完成25题+3直觉题并看到结果 | 手动测试 |
| **M3** | 无P0 Bug，Performance > 70 | 测试报告 |
| **M4** | Lighthouse > 80，可对外展示 | 公网访问 |

---

## 七、资源预算

### 7.1 人力成本

| 角色 | 人数 | 工作量（人天） | 备注 |
|:----:|:----:|:--------------:|:-----|
| 前端开发 | 1人 | 14天 | 全职 |
| 后端开发 | 1人 | 4天（可选） | 兼职 |
| UI设计 | 1人 | 2天 | 兼职 |
| 测试 | 1人 | 2天 | 兼职 |

### 7.2 资金成本

| 项目 | 费用 | 备注 |
|:----:|:----:|:-----|
| 域名 | ¥50/年 | 暂用免费域名 |
| 服务器 | ¥0 | Vercel免费额度 |
| SSL证书 | ¥0 | Vercel自带 |
| 图标/素材 | ¥0 | 开源库 |
| **合计** | **¥50** | MVP阶段 |

---

## 八、后续迭代计划

### 8.1 V1.1（上线后2周）

| 功能 | 优先级 | 说明 |
|:----:|:------:|:-----|
| PDF导出 | P0 | 生成可下载PDF报告 |
| 分享功能 | P0 | 生成分享链接/图片 |
| 微信登录 | P1 | 降低注册门槛 |
| 用户中心 | P1 | 查看和管理评估 |

### 8.2 V1.2（上线后1个月）

| 功能 | 优先级 | 说明 |
|:----:|:------:|:-----|
| 多评估类型 | P0 | 合伙人/投资/战略 |
| 历史对比 | P1 | 多次评估趋势图 |
| 小程序版 | P2 | 微信生态扩展 |
| 扣子插件 | P2 | 集成到扣子Bot |

### 8.3 V1.3（上线后2个月）

| 功能 | 优先级 | 说明 |
|:----:|:------:|:-----|
| 团队版 | P0 | 企业用户管理 |
| API开放 | P1 | 供第三方调用 |
| 定制报告 | P1 | 企业定制内容 |
| AI建议 | P2 | GPT增强行动建议 |

---

## 九、风险与应对

| 风险 | 概率 | 影响 | 应对措施 |
|:----:|:----:|:----:|:---------|
| 评分算法不准确 | 中 | 高 | 邀请5人内测验证 |
| 用户流失（中断） | 高 | 中 | 增加进度保存功能 |
| 雷达图显示异常 | 低 | 中 | 准备备用图表方案 |
| 移动端体验差 | 中 | 中 | 提前进行响应式测试 |
| 竞品抢先上线 | 低 | 高 | 加快开发，突出差异化 |

---

## 十、附录

### 10.1 环境配置

```bash
# Node.js
node >= 18.0.0
npm >= 9.0.0

# 开发命令
npm install
npm run dev
npm run build

# 环境变量
VITE_API_BASE_URL=http://localhost:3000
```

### 10.2 技术栈版本

| 技术 | 版本 | 说明 |
|:----:|:----:|:-----|
| Vue | 3.4+ | 组合式API |
| Vite | 5.0+ | 构建工具 |
| TailwindCSS | 3.4+ | 样式框架 |
| ECharts | 5.5+ | 图表库 |
| Vue Router | 4.2+ | 路由 |
| Pinia | 2.1+ | 状态管理 |

---

> **MVP精神**: 先跑通，再优化
> **核心理念**: 5分钟，不是敷衍，是高效

---

*五维决策测评系统 MVP开发计划 V1.0*
*满意解研究所 · 满意扣子编制*
*2026-04-28*
