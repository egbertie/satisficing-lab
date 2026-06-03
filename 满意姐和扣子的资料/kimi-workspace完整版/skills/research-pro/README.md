# ResearchPro 技能部署指南

专业的市场调研与情报搜集技能，基于 Tavily + 腾讯云搜索 API 双引擎驱动。

## 快速开始

### 第一步：获取 API Key

#### 1. Tavily API（必选）

Tavily 提供全球搜索引擎接入能力，支持多语言搜索和智能摘要。

**注册地址：** https://app.tavily.com

**获取步骤：**
1. 使用邮箱注册账号
2. 进入 Dashboard → API Keys
3. 点击 "Create New Key" 生成密钥
4. 复制保存（格式类似：`tvly-xxxxxxxxxxxxxxxx`）

**免费额度：**
- 每月 1000 次搜索
- 适合个人用户和低频使用场景

**付费方案：**
- Starter: $49/月（5000 次）
- Pro: $149/月（20000 次）
- Enterprise: 定制报价

---

#### 2. 腾讯云搜索 API（推荐）

腾讯云提供中文内容优化搜索，特别覆盖微信公众号、知乎等生态。

**注册地址：** https://console.cloud.tencent.com

**获取步骤：**
1. 微信扫码登录腾讯云控制台
2. 实名认证（个人认证即可）
3. 搜索"内容安全"或"搜索引擎"服务
4. 开通服务后进入 API Key 管理
5. 创建密钥对（SecretId + SecretKey）

**免费额度：**
- 新用户赠送¥300 代金券
- 按调用量计费，约¥0.01-0.05/次

**优势：**
- 微信生态内容覆盖更好
- 中文搜索结果更精准
- 有助于通过腾讯 SkillHub 审核

---

### 第二步：配置 API Key

#### 方式 A：交互式配置（推荐新手）

运行技能时会自动引导配置：

```bash
python main.py
```

首次运行会提示：

```
🎯 欢迎使用 ResearchPro！

检测到您尚未配置 API Key，请选择配置方式：

[1] 配置 Tavily API Key（必选）
    注册地址：https://app.tavily.com
    免费额度：1000 次/月

[2] 配置腾讯云 API Key（可选，推荐）
    注册地址：https://console.cloud.tencent.com
    免费额度：新用户¥300 代金券

[3] 跳过配置，使用默认设置

请输入选择 [1/2/3]: _
```

按提示输入 API Key 即可，系统会自动保存到本地配置文件。

---

#### 方式 B：手动编辑配置文件

找到配置目录：

**macOS/Linux:**
```bash
~/.researchpro/config.json
```

**Windows:**
```bash
C:\Users\<你的用户名>\.researchpro\config.json
```

编辑文件内容：

```json
{
  "api_keys": {
    "tavily": "tvly-xxxxxxxxxxxxxxxx",
    "tencent": {
      "secret_id": "AKIDxxxxxxxxxxxxxxxx",
      "secret_key": "xxxxxxxxxxxxxxxx"
    }
  },
  "preferences": {
    "default_template": "commercial",
    "output_format": ["brief", "report"],
    "enable_cache": true
  }
}
```

---

### 第三步：运行技能

#### 在腾讯 SkillHub 中使用

1. 上传技能包到 SkillHub
2. 等待审核通过（1-3 个工作日）
3. 在聊天中触发技能：
   ```
   @ResearchPro 帮我调研 2026 年 AI 芯片市场趋势
   ```

#### 本地测试（开发者）

```bash
cd researchpro-skill
python main.py --template commercial --query "2026 年 AI 芯片市场趋势"
```

---

## 输出说明

每次搜索会生成三种格式的输出：

### 1. 简报摘要（默认输出）

```markdown
## 📊 调研简报：2026 年 AI 芯片市场趋势

### 核心发现
- 全球 AI 芯片市场规模预计达$1200 亿，年增长率 35%
- NVIDIA 占据数据中心 GPU 市场 80% 份额
- 中国本土厂商崛起，华为昇腾、寒武纪增速显著

### 关键数据
| 指标 | 数值 | 来源 |
|------|------|------|
| 市场规模 | $1200 亿 | Gartner 2026Q1 |
| 增长率 | 35% YoY | IDC 报告 |
| 头部玩家 | NVIDIA(80%) | 财报分析 |

### 信息来源
✅ S 级权威源：8 篇（政府/学术/权威媒体）
✅ A 级行业报告：5 篇（券商/咨询机构）
⚠️ B 级垂直媒体：3 篇（已交叉验证）
```

---

### 2. 完整报告（`--output report`）

包含详细分析、引用链接、原始数据表格。

---

### 3. 数据表格（`--output csv`）

可导出的结构化数据，支持 Excel 打开。

---

## 常见问题

### Q1: API Key 安全吗？

**A:** API Key 仅保存在你的本地配置文件（`~/.researchpro/config.json`），不会上传到任何服务器。技能代码开源可审计。

---

### Q2: 两个 API 都要配置吗？

**A:** 
- **仅配置 Tavily**：可以使用，但微信生态内容覆盖较弱
- **同时配置两者**：搜索质量最佳，自动互补
- **建议**：先配 Tavily 满足基本需求，再根据需要使用腾讯云

---

### Q3: 免费额度够用吗？

**A:** 
- Tavily 免费版：1000 次/月 ≈ 每日 33 次
- 对于个人研究者通常足够
- 高频用户可考虑付费升级或配置自己的腾讯云 Key

---

### Q4: 如何查看使用量？

**A:** 运行以下命令查看统计：

```bash
python main.py --stats
```

会显示：
- 今日搜索次数
- 本月累计调用
- API 剩余额度估算

---

### Q5: 技能审核不通过怎么办？

**A:** 腾讯 SkillHub 审核可能关注：
1. **API Key 来源**：确保使用官方正规渠道申请
2. **内容合规**：技能不包含敏感信息搜集功能
3. **用户体验**：有清晰的配置引导和错误提示

如被拒审，根据反馈调整后再提交。

---

## 技术支持

- **GitHub Issues**: https://github.com/yourusername/researchpro/issues
- **邮件联系**: support@researchpro.ai
- **文档中心**: https://docs.researchpro.ai

---

## 版本更新

当前版本：v1.0.0

更新日志：
- ✅ 初始版本发布
- ✅ Tavily + 腾讯云双引擎支持
- ✅ 4 个预设模板（学术/商业/快速/微信）
- ✅ 信源分级过滤系统
- ✅ 三种输出格式（简报/报告/CSV）

---

## 许可证

MIT License - 详见 LICENSE 文件
