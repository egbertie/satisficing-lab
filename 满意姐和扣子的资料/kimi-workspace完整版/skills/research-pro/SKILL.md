---
name: ResearchPro
description: 专业市场调研与情报搜集技能。基于 Tavily+腾讯云双引擎搜索，支持学术研究/商业调研/快速验证/微信生态四种模板，自动信源分级过滤，输出简报/报告/CSV 三种格式。当用户需要市场调研、竞品分析、行业研究、信息搜集、数据验证时使用。
license: MIT
---

# ResearchPro - 专业市场调研技能

## 快速开始

### 首次使用配置

运行技能后会自动引导配置 API Key：

```
🎯 欢迎使用 ResearchPro！

检测到您尚未配置 API Key，请按提示完成配置。

【步骤 1】配置 Tavily API Key（必选）
注册地址：https://app.tavily.com
免费额度：1000 次/月

请输入 Tavily API Key: tvly-xxxxxxxxxxxx
✓ 已保存

【步骤 2】配置腾讯云 API Key（可选）
注册地址：https://console.cloud.tencent.com
免费额度：新用户¥300 代金券

是否需要配置腾讯云 API Key? (y/n): y
✓ 已保存

✅ 配置完成！
```

---

## 使用方式

### 基础用法

```
@ResearchPro 帮我调研 2026 年 AI 芯片市场趋势
```

### 指定模板

```
@ResearchPro --template academic 生成式 AI 在医疗领域的应用研究
@ResearchPro --template commercial 中国新能源汽车竞争格局分析
@ResearchPro --template quick 今天苹果发布会主要内容
@ResearchPro --template wechat 知识付费行业最新动态
```

### 指定输出格式

```
@ResearchPro --output report 全球量子计算发展现状
@ResearchPro --output csv 半导体产业链上下游企业名单
```

---

## 模板说明

| 模板 | 适用场景 | 时间范围 | 信源等级 |
|------|---------|---------|---------|
| **academic** | 学术论文、文献综述 | 最近 5 年 | S/A 级 |
| **commercial** | 市场分析、竞品研究 | 最近 2 年 | S/A/B 级 |
| **quick** | 快速核实、获取概览 | 最近 1 年 | S/A 级 |
| **wechat** | 微信公众号、小程序 | 最近 1 年 | S/A/B 级 |

---

## 输出格式

### 简报摘要（默认）

自动生成包含核心发现、关键数据、信源统计的简报。

### 完整报告（`--output report`）

详细分析报告，包含完整引用、数据表格、深度洞察。

### CSV 导出（`--output csv`）

结构化数据表格，可用 Excel 打开进行二次分析。

---

## 信源分级体系

### S 级（权威信源）
- 政府网站 (.gov.cn)
- 学术机构 (.ac.cn, .edu.cn)
- 权威媒体 (新华网、人民网)
- 顶级期刊 (Nature, Science, IEEE)

**策略：** ✅ 免过滤，直接使用

---

### A 级（行业权威）
- 咨询公司 (McKinsey, BCG, Deloitte)
- 研究机构 (Gartner, IDC)
- 财经媒体 (财新、36 氪)

**策略：** ✅ 轻度过滤，建议保留

---

### B 级（垂直媒体）
- 专业博客 (知乎、简书、Medium)
- 技术社区 (GitHub, CSDN)
- 自媒体 (头条号、公众号)

**策略：** ⚠️  严格过滤，需交叉验证

---

### C 级（未认证）
- 个人网站
- 未知来源

**策略：** ❌ 默认排除

---

## API Key 管理

### 查看当前配置

```bash
python main.py --stats
```

### 重新配置

```bash
python main.py --setup
```

### 手动编辑配置文件

文件位置：`~/.researchpro/config.json`

```json
{
  "api_keys": {
    "tavily": "tvly-xxxxxxxxxxxx",
    "tencent": {
      "secret_id": "AKIDxxxxxxxx",
      "secret_key": "xxxxxxxx"
    }
  },
  "preferences": {
    "default_template": "commercial",
    "enable_cache": true
  }
}
```

---

## 常见问题

### Q: API Key 安全吗？

A: API Key 仅保存在本地配置文件，不会上传到任何服务器。代码开源可审计。

---

### Q: 必须配置两个 API 吗？

A: 
- 仅 Tavily：可以使用，满足基本需求
- 两者都配：搜索质量最佳，覆盖更全面
- 建议：先配 Tavily，再根据需要加腾讯云

---

### Q: 免费额度够用吗？

A: 
- Tavily 免费版：1000 次/月 ≈ 每日 33 次
- 个人研究者通常足够
- 高频用户可升级付费或自备 Key

---

### Q: 如何降低 API 调用成本？

A: 
1. **启用缓存**：相同查询不重复调用（默认开启）
2. **使用快速模板**：`--template quick` 减少搜索量
3. **合理设计查询**：避免过于宽泛的主题

---

## 开发者扩展

### 添加新模板

编辑 `main.py` 中的 `TEMPLATES` 字典：

```python
TEMPLATES = {
    "custom": {
        "name": "自定义模板",
        "description": "我的定制模板",
        "time_range": "1y",
        "sources": ["S", "A"],
        "output_depth": "brief",
        "prompt_template": "自定义 Prompt..."
    }
}
```

---

### 自定义信源白名单

编辑 `SourceFilter` 类中的域名列表：

```python
S_LEVEL_DOMAINS = [
    "gov.cn", "ac.cn", 
    "your-custom-domain.com"  # 添加自定义权威域名
]
```

---

## 版本历史

### v1.0.0 (2026-04-11)
- ✅ 初始版本发布
- ✅ Tavily + 腾讯云双引擎
- ✅ 4 个预设模板
- ✅ 信源分级过滤
- ✅ 三种输出格式

---

## 技术支持

- GitHub: https://github.com/yourusername/researchpro
- 文档：https://docs.researchpro.ai
- 邮箱：support@researchpro.ai
