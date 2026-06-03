---
# 知识元数据 (5标准化)
knowledge_id: W11-06EE19
title: Marketing Content Generator
category: 11_Skill文档
source: skills/.archive_marketing-content-generator/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 9762
week: 11
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Marketing Content Generator

> **知识ID**: W11-06EE19  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_marketing-content-generator/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: marketing-content-generator
description: Unified marketing content generation suite - Ad copy, landing pages, social media content, cross-border marketing, Chinese copywriting. Replaces adwords, copywriting, and copywriting-zh-pro with integrated marketing workflow. Use for: writing ad copy, landing page copy, social media posts, product descriptions, email sequences, A/B test variants, cross-border e-commerce copy.
triggers: ["copywriting", "文案", "广告", "营销", "landing page", "social media", "小红书", "公众号", "cross-border", "电商", "亚马逊", "独立站"]
---

# Marketing Content Generator

**统一营销内容生成套件** - 从广告文案到落地页，从社媒内容到跨境营销的一站式内容创作解决方案。

> 🎯 替代: adwords + copywriting + copywriting-zh-pro

---

## 核心能力

| 功能模块 | 覆盖场景 |
|---------|---------|
| **广告文案** | Google Ads, Facebook Ads, TikTok Ads, 信息流广告 |
| **落地页** | Landing Page文案、销售页、官网首页 |
| **社媒内容** | 小红书、公众号、朋友圈、抖音脚本 |
| **电商文案** | 亚马逊、Shopify、独立站、详情页 |
| **邮件营销** | 邮件序列、营销邮件、自动化邮件 |
| **A/B测试** | 多版本文案生成、测试建议 |

---

## 快速开始

### 1. 广告文案

```bash
# Google Ads文案
mcg ad google --product "AI写作工具" --audience "内容创作者" --goal "signup"

# Facebook Ads文案
mcg ad facebook --product "在线教育课程" --angle "pain" --cta "立即试听"

# 通用广告文案 (多平台适配)
mcg ad --product "智能家居系统" --platforms google,facebook,tiktok --variants 5
```

### 2. 落地页文案

```bash
# 完整落地页
mcg landing --product "SaaS项目管理工具" --angle "效率提升" --output full

# 销售页
mcg sales --product "高端摄影课程" --price 2999 --objections time,money,trust
```

### 3. 社媒内容

```bash
# 小红书文案
mcg social xiaohongshu --topic "职场效率工具" --style "种草" --cta "收藏"

# 公众号文章
mcg social wechat --topic "AI趋势分析" --length long --tone professional

# 抖音脚本
mcg social douyin --hook "震惊体" --product "护肤产品" --duration 60

# 朋友圈文案
mcg social moments --content "产品上新" --tone soft
```

### 4. 电商文案

```bash
# 亚马逊Listing
mcg ecommerce amazon --product "无线耳机" --keywords "noise cancelling, bluetooth 5.3"

# 独立站产品页
mcg ecommerce shopify --product "手工皮具" --story brand --objections quality

# 详情页 (中文电商)
mcg ecommerce detail --product "空气净化器" --highlights "除甲醛,静音,智能" --faqs 5
```

---

## 命令详解

### `mcg ad` - 广告文案

```bash
mcg ad [platform] [options]

Platforms: google, facebook, tiktok, baidu, bytedance, universal

Options:
  --product <name>          产品/服务名称
  --audience <desc>         目标受众描述
  --goal <action>           目标行动: click, signup, purchase, download
  --angle <type>            切入角度: benefit, pain, curiosity, authority
  --cta <text>              行动号召
  --variants <n>            生成变体数量
  --tone <style>            语调: professional, casual, urgent, friendly
  --platforms <list>        多平台生成
  --output <format>         输出格式: text, json, csv
```

**广告文案公式库:**

| 公式 | 说明 | 示例 |
|------|------|------|
| AIDA | 注意-兴趣-欲望-行动 | 标准广告结构 |
| PAS | 问题-激化-解决 | 痛点驱动 |
| FAB | 特性-优势-收益 | 产品导向 |
| 4P | 画面-承诺-证明-推动 | 快速转化 |
| QUEST | 限定-理解-教育-刺激-转化 | 长文案适用 |

**示例:**

```bash
# Google Ads (搜索广告)
mcg ad google --product "企业级CRM系统" \
  --audience "中小企业销售团队" \
  --goal "signup" \
  --angle "benefit" \
  --variants 3

# 输出:
# 标题1: 免费试用CRM系统 - 提升销售效率300%
# 标题2: 企业CRM解决方案 - 自动化您的销售流程
# 描述: 一站式客户管理平台，自动化跟进、智能报表、团队协作...

# Facebook Ads (信息流)
mcg ad facebook --product "在线瑜伽课程" \
  --audience "25-40岁职场女性" \
  --angle "transformation" \
  --cta "立即领取7天免费"

# 多平台批量生成
mcg ad --product "AI写作助手" \
  --platforms google,facebook,tiktok \
  --variants 5 \
  --output campaign_assets.json
```

### `mcg landing` - 落地页文案

```bash
mcg landing [options]

Options:
  --product <name>          产品名称
  --tagline <text>          核心卖点
  --audience <desc>         目标用户
  --angle <type>            切入角度
  --sections <list>         包含模块: hero,problem,solution,features,testimonials,pricing,faq,cta
  --tone <style>            语调风格
  --length <size>           长度: short, medium, long
  --output <format>         输出: full, outline, json
```

**落地页模块:**

```bash
# 完整落地页
cmcg landing --product "AI数据分析平台" \
  --tagline "让数据说话，让决策更简单" \
  --audience "企业数据分析师和决策者" \
  --sections hero,problem,solution,features,testimonials,pricing,faq,cta \
  --length long \
  --output full

# 简化版
cmcg landing --product "个人记账App" \
  --angle "理财自由" \
  --sections hero,features,cta \
  --length short
```

**输出结构:**
```
1. Hero Section (首屏)
   - 主标题 (3个备选)
   - 副标题
   - CTA按钮文案

2. Problem Section (痛点)
   - 问题描述
   - 痛点放大

3. Solution Section (解决方案)
   - 产品介绍
   - 核心优势

4. Features Section (功能特性)
   - 功能点 + 用户收益

5. Testimonials Section (客户证言)
   - 3-5条评价模板

6. Pricing Section (定价)
   - 价格锚点
   - 套餐对比

7. FAQ Section (常见问题)
   - 5-8个典型问题

8. CTA Section (最终行动)
   - 紧迫感营造
   - 最终CTA
```

### `mcg social` - 社媒内容

```bash
mcg social <platform> [options]

Platforms: xiaohongshu, wechat, douyin, moments, weibo, bilibili

Options:
  --topic <subject>         内容主题
  --style <type>            风格:种草,干货,故事,测评,盘点
  --tone <style>            语调:亲切,专业,幽默,正式
  --length <size>           长度:short,medium,long
  --cta <action>            行动号召:收藏,评论,私信,关注
  --hashtags <n>            生成标签数量
  --hook <type>             钩子类型:悬念,数字,痛点,反差
```

**平台特化:**

```bash
# 小红书 - 种草文
mcg social xiaohongshu --topic "早八人5分钟妆容" \
  --style "种草" \
  --hook "数字" \
  --cta "收藏" \
  --hashtags 5

# 输出结构:
# 标题: 被同事问爆的5分钟早八妆！懒人必看✨
# 正文: ...
# 标签: #早八妆容 #快速出门妆 #懒人化妆...

# 公众号 - 深度文章
mcg social wechat --topic "2024年AI投资趋势分析" \
  --length long \
  --tone professional \
  --sections intro,analysis,cases,conclusion

# 抖音 - 短视频脚本
mcg social douyin --product "洗面奶" \
  --hook "震惊体" \
  --duration 60 \
  --style "测评"

# 输出:
# 【0-3秒】钩子: 用了这款洗面奶，我彻底放弃了大牌...
# 【3-15秒】问题: 以前买洗面奶只看品牌...
# 【15-45秒】解决方案: 直到我发现了...
# 【45-60秒】CTA: 评论区告诉我...

# 朋友圈 - 软性文案
mcg social moments --content "产品上新通知" \
  --tone soft \
  --cta "私信了解"
```

### `mcg ecommerce` - 电商文案

```bash
mcg ecommerce <platform> [options]

Platforms: amazon, shopify, taobao, jd, pdd, universal

Options:
  --product <name>          产品名称
  --category <type>         产品类别
  --keywords <list>         关键词列表
  --features <list>         产品卖点
  --audience <desc>         目标人群
  --price <amount>          价格
  --objections <list>       需解决的顾虑
  --language <lang>         语言: zh, en, bilingual
```

**跨境电商平台:**

```bash
# 亚马逊Listing
mcg ecommerce amazon --product "Bluetooth Headphones" \
  --category "Electronics" \
  --keywords "wireless,noise cancelling,long battery" \
  --features "40h battery,ANC,comfortable fit" \
  --language en

# 输出:
# Title: Bluetooth Headphones Wireless - 40H Playtime Active Noise Cancelling...
# Bullets:
# - [沉浸式音效] 40mm驱动单元...
# - [主动降噪] 阻隔95%环境噪音...
# ...
# Description: HTML格式完整描述

# 独立站 (中英双语)
mcg ecommerce shopify --product "手工皮具钱包" \
  --story brand \
  --objections quality,price \
  --language bilingual

# 中文详情页
mcg ecommerce detail --product "智能扫地机器人" \
  --features "激光导航,自动集尘,APP控制" \
  --objections "噪音,清洁效果,价格" \
  --faqs 8
```

### `mcg email` - 邮件营销

```bash
mcg email <type> [options]

Types: sequence, newsletter, promotional, abandoned_cart, welcome

Options:
  --product <name>          产品/服务
  --goal <action>           邮件目标
  --sequence <n>            序列邮件数量
  --tone <style>            语调
  --personalization <bool>  是否个性化
```

```bash
# 欢迎邮件序列 (5封)
mcg email sequence --type welcome \
  --product "SaaS工具" \
  --sequence 5 \
  --goal "activation"

# 购物车挽回邮件
mcg email abandoned_cart --product "电商网站" \
  --sequence 3 \
  --urgency high

# 促销邮件
mcg email promotional --campaign "黑五大促" \
  --discount "30% OFF" \
  --deadline "3天后"
```

### `mcg abtest` - A/B测试

```bash
mcg abtest [options]

Options:
  --original <text>         原始文案
  --element <type>          测试元素: headline, cta, body, angle
  --variants <n>            变体数量
  --hypothesis <desc>       测试假设
```

```bash
# 测试不同标题
mcg abtest --element headline \
  --original "提升销售效率" \
  --variants 4 \
  --angle "pain,benefit,curiosity,authority"

# 输出:
# A: 你还在手动处理销售数据吗？ (痛点)
# B: 让销售效率提升300%的秘密 (收益)
# C: 这个工具改变了我们的销售方式 (好奇)
# D: 500强企业都在用的销售工具 (权威)

# 完整测试方案
mcg abtest --campaign "landing_page" \
  --elements headline,cta,hero_image \
  --variants 3 \
  --output abtest_plan.json
```

---

## 文案框架库

### 英文框架

```bash
# AIDA框架
mcg framework aida --product "CRM Software" --output template

# PAS框架
mcg framework pas --problem "低转化率" --agitate "每月损失客户" --solution "A/B测试工具"

# FAB框架
mcg framework fab --feature "AI自动化" --advantage "节省时间" --benefit "专注核心业务"
```

### 中文框架

```bash
# 痛点-方案-收益
mcg framework 痛点方案 --痛点 "加班做报表" --方案 "自动化工具" --收益 "每天节省2小时"

# 场景-冲突-解决
mcg framework 场景冲突 --场景 "周末带娃" --冲突 "工作消息不断" --解决 "自动回复助手"
```

---

## 内容优化

```bash
# 改进现有文案
mcg improve --input original.txt --goal "提高点击率" --audience "年轻妈妈"

# 多语言翻译+本地化
mcg localize --input copy_en.txt --target zh --market china

# 检测敏感词
mcg check --input draft.txt --platform wechat

# 生成文案评分
mcg score --input copy.txt --criteria clarity,persuasion,cta
```

---

## Python API

```python
from marketing_content_generator import MCG

mcg = MCG()

# 生成广告文案
ads = mcg.generate_ads(
    product="AI写作助手",
    platform="google",
    audience="内容创作者",
    variants=3
)

# 生成落地页
landing = mcg.generate_landing(
    product="项目管理工具",
    sections=["hero", "features", "pricing", "cta"]
)

# 生成社媒内容
xiaohongshu = mcg.generate_social(
    platform="xiaohongshu",
    topic="职场效率",
    style="种草"
)

# A/B测试变体
variants = mcg.generate_variants(
    original="立即购买",
    element="cta",
    n=5
)
```

---

## 与原有Skill的兼容

| 原Skill | 功能 | 新命令 | 状态 |
|---------|------|--------|------|
| adwords | 标题公式、广告文案 | `mcg ad` | ✅ 替代 |
| adwords | 落地页文案 | `mcg landing` | ✅ 替代 |
| copywriting | AIDA/PAS/FAB框架 | `mcg framework` | ✅ 替代 |
| copywriting | 英文营销文案 | `mcg ad --language en` | ✅ 替代 |
| copywriting-zh-pro | 中文文案 | `mcg ad --language zh` | ✅ 替代 |
| copywriting-zh-pro | 小红书/公众号 | `mcg social` | ✅ 替代 |
| copywriting-zh-pro | 跨境电商 | `mcg ecommerce` | ✅ 替代 |

---

**状态**: ✅ 生产就绪
**自建替代计数**: +3 (adwords, copywriting, copywriting-zh-pro)
