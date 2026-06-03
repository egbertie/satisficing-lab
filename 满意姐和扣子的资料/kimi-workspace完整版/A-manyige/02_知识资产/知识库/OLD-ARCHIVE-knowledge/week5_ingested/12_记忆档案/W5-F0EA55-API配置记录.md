---
# 知识元数据 (5标准化)
knowledge_id: W5-F0EA55
title: API配置记录
category: 12_记忆档案
source: docs/archive/API配置记录.md
ingested_at: 2026-03-27 17:59:30
word_count: 4998
week: 5
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# API配置记录

> **知识ID**: W5-F0EA55  
> **分类**: 12_记忆档案  
> **来源**: `docs/archive/API配置记录.md`  
> **入库时间**: 2026-03-27

---

## 正文

# API配置记录

> 记录所有API密钥和配置信息
> 最后更新：2026-03-13

---

## 🔑 Perplexity API

### 基本信息
| 项目 | 内容 |
|------|------|
| **服务名称** | Perplexity AI API (pplx-api) |
| **官网** | https://www.perplexity.ai |
| **API文档** | https://docs.perplexity.ai/ |
| **状态** | ⏳ 待用户完成注册 |
| **免费额度** | 300次/天（Pro用户每月$5免费积分） |

### 注册步骤（需用户自行完成）

#### 1. 注册Perplexity账户
1. 访问 https://www.perplexity.ai
2. 点击右上角 "Sign Up" 或 "Get Started"
3. 选择注册方式：
   - Google账户快捷登录
   - 邮箱注册（支持国内外邮箱）
4. 完成邮箱验证

#### 2. 升级Pro账户（可选）
- Pro用户每月可获得$5免费API积分
- 访问 https://www.perplexity.ai/settings 升级
- 如需使用API，账户余额必须非零

#### 3. 申请API访问
1. 登录Perplexity账户
2. 访问设置页面：https://www.perplexity.ai/settings
3. 点击左侧 "API" 选项卡
4. 绑定信用卡（仅用于验证，不会立即扣费）
5. 购买积分（或等待Pro用户的免费积分）

#### 4. 生成API Key
1. 在API设置页面
2. 点击 "Generate API Key"
3. 复制并保存密钥（**只显示一次**）
4. 建议立即保存到安全位置（密码管理器）

### API配置模板

```bash
# 环境变量设置
export PERPLEXITY_API_KEY="your_api_key_here"

# API端点
export PERPLEXITY_API_URL="https://api.perplexity.ai"
```

### 支持的模型
| 模型 | 说明 |
|------|------|
| sonar-small-chat | 轻量级对话模型 |
| sonar-medium-chat | 中等规模对话模型 |
| sonar-small-online | 联网搜索轻量版 |
| sonar-medium-online | 联网搜索中量版 |
| sonar-reasoning | 推理增强版 |

### 快速测试代码（Python）

```python
import requests
import os

api_key = os.getenv("PERPLEXITY_API_KEY")
url = "https://api.perplexity.ai/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "sonar-medium-online",
    "messages": [
        {"role": "system", "content": "Be precise and concise."},
        {"role": "user", "content": "What is the capital of France?"}
    ]
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
```

### 测试代码（curl）

```bash
curl -X POST https://api.perplexity.ai/chat/completions \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sonar-medium-online",
    "messages": [
      {"role": "system", "content": "Be precise and concise."},
      {"role": "user", "content": "What is the capital of France?"}
    ]
  }'
```

### 定价参考
| 模型 | 输入费用 | 输出费用 |
|------|----------|----------|
| sonar-small-chat | $0.20/1M tokens | $0.20/1M tokens |
| sonar-medium-chat | $0.60/1M tokens | $0.60/1M tokens |
| sonar-small-online | $0.20/1M tokens + $5/1K searches | - |
| sonar-medium-online | $0.60/1M tokens + $5/1K searches | - |

### 注意事项
1. **API Key保密**：不要提交到Git仓库或分享给他人
2. **余额监控**：余额不足时API将被暂停
3. **自动充值**：可设置余额低于$2时自动充值
4. **速率限制**：免费用户300次/天，Pro用户更高

### 后续更新位置
获取API Key后，请更新以下字段：
- [ ] `PERPLEXITY_API_KEY`: ________________
- [ ] `注册日期`: ________________
- [ ] `账户类型`: 免费版 / Pro版
- [ ] `状态`: ⏳ 待完成 → ✅ 已完成

---

## 🌐 Jina AI Reader API

### 基本信息
| 项目 | 内容 |
|------|------|
| **服务名称** | Jina AI Reader API |
| **官网** | https://jina.ai/reader/ |
| **API文档** | https://jina.ai/reader/ |
| **状态** | ✅ 已测试，可用（无Key模式） |
| **免费额度** | 1000万 tokens（带API Key）/ IP限制（无Key） |

### 功能说明
Jina AI Reader API 是一个强大的网页内容提取工具，可以将任意URL转换为干净的Markdown格式，非常适合：
- LLM输入预处理
- 网页内容抓取
- 文章摘要生成
- 知识库构建

### 使用方法

#### 方式一：无需API Key（快速开始）
```bash
# 直接在URL前添加 https://r.jina.ai/http://
curl "https://r.jina.ai/http://example.com"
```

#### 方式二：使用API Key（更高限额）
```bash
# 使用官方API端点
curl -H "Authorization: Bearer $JINA_API_KEY" \
  "https://r.jina.ai/http://example.com"
```

### API配置模板

```bash
# 环境变量设置
export JINA_API_KEY="your_api_key_here"

# 备用：直接使用r.jina.ai服务（无需Key）
export JINA_READER_URL="https://r.jina.ai/http://"
```

### 测试记录

#### 测试时间：2026-03-13
#### 测试结果：✅ 通过

```bash
$ curl -s "https://r.jina.ai/http://example.com" | head -20

Title: Example Domain
URL Source: http://example.com/
Published Time: Wed, 11 Mar 2026 19:06:45 GMT

Markdown Content:
Example Domain
===============

Example Domain
==============

This domain is for use in documentation examples without needing permission...
```

### 获取API Key步骤

由于浏览器控制服务暂时不可用，API Key需要手动获取：

1. **访问官网**
   - 打开 https://jina.ai/reader/
   
2. **获取API Key**
   - 在页面中找到 "Get API Key" 或 "API" 按钮
   - 点击后系统会自动生成一个API Key
   - **无需注册**即可获取免费API Key
   - 免费额度：**1000万 tokens**

3. **保存API Key**
   - 复制生成的API Key
   - 保存到安全位置（如密码管理器）
   - 更新本配置文件

### 速率限制

| 用户类型 | 限制 |
|----------|------|
| 无API Key | 按IP限制，较低频率 |
| 免费API Key | 1000万 tokens |
| 付费用户 | 更高限额 |

### 高级功能

#### 搜索模式
```bash
# 使用s.jina.ai进行网络搜索
curl "https://s.jina.ai/你的搜索关键词"
```

#### JSON输出
```bash
# 添加?format=json获取结构化输出
curl "https://r.jina.ai/http://example.com?format=json"
```

#### 图片提取
```bash
# 提取网页中的图片
curl "https://r.jina.ai/http://example.com?images=true"
```

### 注意事项
1. **API Key保密**：获取后请妥善保存，不要泄露
2. **免费额度**：1000万 tokens足够日常使用
3. **无需信用卡**：免费用户无需绑定支付方式
4. **合规使用**：遵守网站的robots.txt规则

### 后续更新位置
获取API Key后，请更新以下字段：
- [ ] `JINA_API_KEY`: ________________
- [ ] `获取日期`: ________________
- [ ] `状态`: ⏳ 待获取Key → ✅ 已配置

---

## 📋 其他API配置（预留）

### OpenAI API
```
状态：待配置
API Key：________________
```

### Kimi API (Moonshot)
```
状态：待配置
API Key：________________
```

---

*文档创建时间：2026-03-13*  
*维护者：AI助手*  
*更新周期：按需更新*
