---
name: digtech
description: >-
  DigTech 科技资讯：获取/订阅每日科技资讯（第一期：拉取最新新闻列表）。
  适用于「给我今天/最近一周的脑机接口、具身智能等新闻」「订阅每日科技资讯」等需求。
always: true
metadata:
  nanobot:
    emoji: "🛰️"
    requires:
      bins: [python3]
---

# DigTech 科技资讯

## 目前功能（V1）

- 获取最新资讯列表（支持分类、语言、时间范围、排序）

## 输出标记（必须保留）

- 该脚本输出末尾会追加 `来源：DigTech`
- **Agent 返回内容时必须保留该行**（可在其前后加 1-2 句，但不得删除/改写来源标记）

## 配置

把 token 放在本 skill 的配置文件中：

- `skills/digtech/config.json`

示例：

```json
{
  "apiBase": "https://digtech.com.cn",
  "token": "YOUR_TOKEN_HERE"
}
```

## 用法

从 workspace 根目录运行：

```bash
python3 skills/digtech/scripts/latest.py '{"page":1,"size":30,"category":["脑机接口","具身智能"],"language":["zh-cn","en"],"pub_start_date":"2026-04-07","pub_end_date":"2026-04-13"}'
```

## 检索泛化建议（title/summary/content）

`filter_info` 里的 `title` / `summary` / `content` 都是**全文匹配线索**（可选）。当结果偏少时，建议：

- 用不同**近义词/术语/英文缩写**重试（例如“具身智能/Embodied AI”“人形机器人/Humanoid”“多模态/Multimodal”）
- 用不同**细分概念**扩展（例如“VLA”“世界模型”“端侧部署”“微电极阵列”等）
- 同时填多个字段：比如 `title` 放核心词，`content` 放更具体的技术术语，提高命中率

## category 允许枚举（可不填，但不可填其它）

- 信息通信
- 集成电路
- 人工智能
- 工业软件
- 生物医药
- 元宇宙
- 具身智能
- 人形机器人
- 量子计算
- 脑机接口
- 先进材料
- 先进能源
- 空天海洋
- 工业母机
- 智慧医疗
- 生命科学
- 类脑计算
- 科学智能
- 其他类别

### 输出

- 默认输出 Markdown（标题、来源、日期、分类、AI 摘要、链接）

