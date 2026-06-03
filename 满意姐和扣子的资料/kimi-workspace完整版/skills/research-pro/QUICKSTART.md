# ResearchPro 快速入门

3 分钟完成配置，立即开始专业市场调研。

---

## 第一步：获取 API Key（2 分钟）

### 方案 A：仅 Tavily（推荐新手）

**适合：** 个人用户、低频使用、快速上手

**步骤：**
1. 访问 https://app.tavily.com
2. 注册账号（邮箱 + 密码）
3. Dashboard → API Keys → Create New Key
4. 复制密钥（格式：`tvly-xxxxxxxx`）

**免费额度：** 1000 次/月 ≈ 每日 33 次

---

### 方案 B：Tavily + 腾讯云（推荐专业用户）

**适合：** 商业调研、覆盖微信生态、提高审核通过率

**步骤：**
1. 完成方案 A 的 Tavily 配置
2. 访问 https://console.cloud.tencent.com
3. 微信扫码登录 → 实名认证
4. 搜索"内容安全" → 开通服务
5. 访问管理 → API 密钥管理 → 新建密钥
6. 复制 SecretId 和 SecretKey

**免费额度：** 新用户¥300 代金券（6 个月有效）

---

## 第二步：配置技能（30 秒）

运行配置向导：

```bash
python main.py --setup
```

按提示输入 API Key：

```
🎯 欢迎使用 ResearchPro！

【步骤 1】配置 Tavily API Key（必选）
请输入 Tavily API Key: tvly-xxxxxxxxxxxx
✓ 已保存

【步骤 2】配置腾讯云 API Key（可选）
是否需要配置腾讯云 API Key? (y/n): y
请输入 SecretId: AKIDxxxxxxxx
请输入 SecretKey: xxxxxxxx
✓ 已保存

✅ 配置完成！
```

---

## 第三步：开始调研（10 秒）

### 基础用法

```bash
python main.py --query "2026 年 AI 芯片市场趋势"
```

### 使用模板

```bash
# 学术研究
python main.py --template academic --query "生成式 AI 在医疗领域的应用"

# 商业调研
python main.py --template commercial --query "中国新能源汽车竞争格局"

# 快速验证
python main.py --template quick --query "今天苹果发布会主要内容"

# 微信生态
python main.py --template wechat --query "知识付费行业最新动态"
```

### 指定输出格式

```bash
# 简报摘要（默认）
python main.py -q "量子计算发展现状"

# 完整报告
python main.py -q "半导体产业链分析" -o report

# CSV 导出
python main.py -q "头部 VC 投资案例" -o csv
```

---

## 第四步：查看结果

### 简报示例

```markdown
## 📊 调研简报：2026 年 AI 芯片市场趋势

### 核心发现
• 全球 AI 芯片市场规模预计达$1200 亿，年增长率 35%
• NVIDIA 占据数据中心 GPU 市场 80% 份额
• 中国本土厂商崛起，华为昇腾、寒武纪增速显著

### 关键数据
| 指标 | 数值 | 来源 |
|------|------|------|
| 市场规模 | $1200 亿 | Gartner 2026Q1 |
| 增长率 | 35% YoY | IDC 报告 |
| 头部玩家 | NVIDIA(80%) | 财报分析 |

### 信息来源
✅ S 级权威源：8 篇（政府/学术/权威媒体）
✅ A 级行业报告：5 篇（券商/咨询机构）
⚠️  B 级垂直媒体：3 篇（已交叉验证）
```

---

## 常用命令速查

```bash
# 配置向导
python main.py --setup

# 快速调研
python main.py -q "你的主题"

# 使用模板
python main.py -t commercial -q "市场分析"

# 导出 CSV
python main.py -o csv -q "数据搜集" > output.csv

# 查看统计
python main.py --stats

# 测试连接
python test_connection.py

# 列出模板
python main.py --list-templates
```

---

## 故障排查

### 问题 1: "未配置 API Key"

**解决：**
```bash
python main.py --setup
```

---

### 问题 2: "Invalid API Key"

**原因：** Key 不正确或包含空格

**解决：**
1. 重新运行 `python main.py --setup`
2. 确保复制完整的 Key
3. 不要包含前后空格

---

### 问题 3: "Quota exceeded"

**原因：** 免费额度用完

**解决：**
- 等待下月 1 号重置
- 升级到付费方案
- 配置自己的腾讯云 API

---

### 问题 4: 网络超时

**解决：**
```bash
# 检查网络连接
ping api.tavily.com

# 使用缓存模式
# 编辑 ~/.researchpro/config.json
# "enable_cache": true
```

---

## 下一步

- 📖 **详细文档：** 阅读 `README.md` 了解完整功能
- 🔑 **API 指南：** `API_KEY_GUIDE.md` 详细说明密钥配置
- 🧪 **测试工具：** `python test_connection.py` 验证连接
- 📦 **打包上传：** `python package_skill.py` 准备提交 SkillHub

---

## 获取帮助

遇到问题？

1. 查阅 `API_KEY_GUIDE.md` - 90% 的问题都有解答
2. 运行 `python test_connection.py` - 自动诊断问题
3. 邮件 support@researchpro.ai - 24h 内回复

---

**祝你调研顺利！** 🚀
