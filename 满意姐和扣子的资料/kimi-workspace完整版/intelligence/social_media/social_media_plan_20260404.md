# 新媒体情报采集计划 - 2026-04-04

## 执行策略
**核心原则**: 不直接对抗平台反爬，通过聚合源+RSS-Bridge实现Token友好的轻量监控。

## 监控主题
- 硬科技创业
- 合伙人匹配
- 创始人决策

## 平台配置

### 微信公众号 (`wechat`)
- **推荐数据源**: 新榜, 清博指数, RSS-Bridge(WeChat)
- **关键词**: 硬科技, 合伙人, 创业, 融资
- **限制说明**: 由于微信反爬严格，建议使用新榜/清博的公开榜单或RSS-Bridge

### 小红书 (`xiaohongshu`)
- **推荐数据源**: 千瓜数据, 新红数据
- **关键词**: 创业干货, 合伙人选择, 创始人IP
- **限制说明**: 小红书无公开API，建议通过第三方数据平台获取趋势报告

### B站 (`bilibili`)
- **推荐数据源**: B站公开搜索, RSS-Bridge
- **关键词**: 创业, 科技, 商业思维
- **限制说明**: 可通过B站搜索API获取前10条结果

### 抖音 (`douyin`)
- **推荐数据源**: 巨量算数, 蝉妈妈
- **关键词**: 商业思维, 合伙人
- **限制说明**: 抖音无公开API，依赖第三方数据平台

## RSS-Bridge 部署建议
```bash
# 1. 使用 RSS-Bridge 公共实例或自建
# 2. 配置 WeChat/Bilibili/Douyin 的 Bridge
# 3. 产出 RSS feed 后，由 intelligence_collection_system.py 统一抓取
```

## GitHub Actions 自动化参考
```yaml
name: 新媒体情报采集
on:
  schedule:
    - cron: '0 8 * * *'  # 每天08:00
jobs:
  collect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: 运行情报采集
        run: python3 social_media_collector.py
```
