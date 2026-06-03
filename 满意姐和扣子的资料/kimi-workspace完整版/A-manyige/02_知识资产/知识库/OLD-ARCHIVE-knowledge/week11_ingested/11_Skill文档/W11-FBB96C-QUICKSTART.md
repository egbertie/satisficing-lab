---
# 知识元数据 (5标准化)
knowledge_id: W11-FBB96C
title: Marketing Content Generator - 快速参考卡
category: 11_Skill文档
source: skills/.archive_marketing-content-generator/QUICKSTART.md
ingested_at: 2026-03-27 17:59:30
word_count: 2742
week: 11
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Marketing Content Generator - 快速参考卡

> **知识ID**: W11-FBB96C  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_marketing-content-generator/QUICKSTART.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Marketing Content Generator - 快速参考卡

## 🚀 一键启动

```bash
# 查看所有功能
mcg help

# 查看特定功能帮助
mcg help ad
mcg help social
mcg help ecommerce
mcg help framework
```

---

## 🎯 100个标题公式

```bash
# 查看全部100个
mcg headline --all

# 按类型查看
mcg headline --type digital      # 数字型(1-15)
mcg headline --type question     # 问题型(16-30)
mcg headline --type benefit      # 好处型(31-45)
mcg headline --type urgent       # 紧迫型(46-60)
mcg headline --type story        # 故事型(61-75)
mcg headline --type authority    # 权威型(76-90)
mcg headline --type unique       # 独特型(91-100)
```

---

## 📝 文案框架 (AIDA/PAS/FAB/4P/BAB)

```bash
# AIDA框架
mcg framework aida

# PAS框架
mcg framework pas

# FAB框架
mcg framework fab

# 4P框架
mcg framework 4p

# BAB框架
mcg framework bab

# 中文框架
mcg framework 痛点方案
mcg framework 场景冲突
```

---

## 📢 广告文案

```bash
# Google Ads
mcg ad --product "产品名" --platform google --variants 5

# Facebook Ads
mcg ad --product "产品名" --platform facebook --variants 5

# 多平台批量生成
mcg ad --product "产品名" --platform universal --variants 10
```

---

## 📱 社媒内容

```bash
# 小红书种草文
mcg social xiaohongshu

# 公众号文章
mcg social wechat

# 抖音短视频脚本
mcg social douyin

# 朋友圈文案
mcg social moments

# 微博文案
mcg social weibo

# B站脚本
mcg social bilibili
```

---

## 🛒 电商文案

```bash
# 亚马逊Listing
mcg ecommerce amazon

# Shopify独立站
mcg ecommerce shopify

# 中文详情页
mcg ecommerce detail

# 淘宝/京东/拼多多
mcg ecommerce taobao
mcg ecommerce jd
mcg ecommerce pdd
```

---

## 🌍 跨境营销

```bash
# Meta广告(Facebook/Instagram)
mcg crossborder meta_ads

# Google广告
mcg crossborder google_ads

# TikTok广告
mcg crossborder tiktok_ads
```

---

## 🏗️ 落地页文案

```bash
# 完整落地页
mcg landing --product "产品名" --style full

# 简化版
mcg landing --product "产品名" --style minimal
```

---

## 💡 实用示例

### 示例1: 生成10个产品标题
```bash
mcg headline --type benefit --count 10
# 输出15个好处型标题公式
```

### 示例2: 小红书种草文案模板
```bash
mcg social xiaohongshu
# 输出完整的文案结构和标题建议
```

### 示例3: 亚马逊Listing模板
```bash
mcg ecommerce amazon
# 输出标题、五点描述、产品描述模板
```

### 示例4: AIDA框架填空
```bash
mcg framework aida
# 输出完整的AIDA框架，只需填空
```

---

## 📊 功能对照表

| 原Skill | 原功能 | 新命令 |
|---------|--------|--------|
| adwords | 100标题公式 | `mcg headline` |
| adwords | AIDA框架 | `mcg framework aida` |
| adwords | 落地页 | `mcg landing` |
| copywriting | PAS/FAB框架 | `mcg framework pas/fab` |
| copywriting-zh-pro | 小红书 | `mcg social xiaohongshu` |
| copywriting-zh-pro | 公众号 | `mcg social wechat` |
| copywriting-zh-pro | 抖音 | `mcg social douyin` |
| copywriting-zh-pro | 朋友圈 | `mcg social moments` |
| copywriting-zh-pro | 跨境电商 | `mcg ecommerce amazon/shopify` |

---

## ✅ 部署状态

- [x] 100个标题公式
- [x] AIDA/PAS/FAB/4P/BAB框架
- [x] 中文文案增强(小红书/公众号/抖音/朋友圈)
- [x] 跨境营销文案(亚马逊/独立站/Meta/Google/TikTok)
- [x] 广告文案生成
- [x] 落地页文案
- [x] 统一入口 `mcg`
- [x] 完整文档和模板

**状态: ✅ 生产就绪**
