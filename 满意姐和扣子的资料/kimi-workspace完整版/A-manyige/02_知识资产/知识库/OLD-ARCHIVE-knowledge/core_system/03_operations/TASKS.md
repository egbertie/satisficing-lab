# API注册三连发 - 任务追踪

## 任务总览
- **TODO-001**: GitHub Models 配置（GPT-4o免费访问）
- **TODO-002**: Perplexity 注册（免费300次/天）
- **TODO-003**: Jina AI 注册（免费1000次/天）

---

## ✅ TODO-001: GitHub Models (GPT-4o)
**状态**: 100% - 待用户完成注册
**最后更新**: 2025-03-12

### 免费额度
| 模型 | RPM | RPD | 输入Token | 输出Token |
|------|-----|-----|-----------|-----------|
| GPT-4o | 10 | 50 | 8,000 | 4,000 |
| GPT-4o-mini | 15 | 150 | 8,000 | 4,000 |
| Llama-3.1-405B | 10 | 50 | 8,000 | 4,000 |
| DeepSeek-R1 | 15 | 150 | 64K | 4,000 |

*RPM=每分钟请求数, RPD=每天请求数*

### 注册步骤
1. **确保有GitHub账号** (免费注册: github.com)
2. **申请早期访问权限** (约5天审核)
   - 访问 https://github.com/marketplace/models
   - 点击 "Get early access" 提交申请表单
3. **创建Personal Access Token**
   - 登录GitHub → 头像 → Settings
   - 左侧菜单 → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token → 勾选 `models` 权限
   - **立即复制保存** (只显示一次!)

### API配置
```
Base URL: https://models.github.ai/inference
Auth: Bearer YOUR_GITHUB_PAT
Models: gpt-4o, gpt-4o-mini, Llama-3.1-405B, DeepSeek-R1, etc.
```

### Python测试代码
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key="YOUR_GITHUB_PAT"
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "你是一个 helpful 助手。"},
        {"role": "user", "content": "你好，请介绍一下GitHub Models。"}
    ],
    max_tokens=1000
)
print(response.choices[0].message.content)
```

---

## ✅ TODO-002: Perplexity API
**状态**: 100% - 待用户完成注册
**最后更新**: 2025-03-12

### 免费额度
- **Pro用户**: 每月5美元免费积分 (约300-500次API调用)
- **免费用户**: 需要购买积分才能生成API密钥

### 注册步骤
1. **注册Perplexity账号**
   - 访问 https://www.perplexity.ai
   - 使用邮箱或Google账号注册
2. **升级Pro** (如需免费额度)
   - 订阅Pro版本 ($20/月) 可获得每月$5 API积分
3. **获取API密钥**
   - 访问 https://www.perplexity.ai/settings/api
   - 绑定信用卡 (用于后续计费)
   - 点击 "Generate API Key"
   - **立即复制保存** (格式: pplx-xxxxxxxxxxxxxxxx)

### API配置
```
Base URL: https://api.perplexity.ai
Auth: Bearer YOUR_PERPLEXITY_API_KEY
Models: sonar, sonar-pro, sonar-reasoning, etc.
```

### Python测试代码
```python
import requests

url = "https://api.perplexity.ai/chat/completions"
headers = {
    "Authorization": "Bearer YOUR_PERPLEXITY_API_KEY",
    "Content-Type": "application/json"
}
data = {
    "model": "sonar",
    "messages": [
        {"role": "system", "content": "你是一个 helpful 助手。"},
        {"role": "user", "content": "什么是量子计算？"}
    ]
}

response = requests.post(url, json=data, headers=headers)
print(response.json()["choices"][0]["message"]["content"])
```

---

## ✅ TODO-003: Jina AI API
**状态**: 100% - 待用户完成注册
**最后更新**: 2025-03-12

### 免费额度
| 服务 | 免费RPM | 免费TPM |
|------|---------|---------|
| Embeddings | 500 | 1M |
| ReRanker | 500 | 1M |
| r.reader (单URL) | 200 | - |
| s.reader (搜索) | 40 | - |
| Classifier | 200 | 500K |
| Segmenter | 200 | - |

### 注册步骤
1. **获取API密钥** (无需注册!)
   - 访问 https://jina.ai/?sui=apikey
   - 免费API密钥直接显示在页面
   - **立即复制保存**

### API配置
```
通用Auth: Bearer YOUR_JINA_API_KEY
Headers必须包含: Accept: application/json

Endpoints:
- Embeddings: https://api.jina.ai/v1/embeddings
- ReRanker: https://api.jina.ai/v1/rerank
- Classifier: https://api.jina.ai/v1/classify
- r.reader: https://r.jina.ai/http://URL
- s.reader: https://s.jina.ai/QUERY
- Segmenter: https://segment.jina.ai
```

### Python测试代码 (Embeddings)
```python
import requests

url = "https://api.jina.ai/v1/embeddings"
headers = {
    "Authorization": "Bearer YOUR_JINA_API_KEY",
    "Content-Type": "application/json",
    "Accept": "application/json"
}
data = {
    "model": "jina-embeddings-v3",
    "input": ["Jina AI是神经搜索专家", "Neural search made easy"]
}

response = requests.post(url, json=data, headers=headers)
embeddings = response.json()["data"]
print(f"生成 {len(embeddings)} 个向量")
```

### Python测试代码 (Reader - 网页抓取)
```python
import requests

# 读取单个网页内容
url = "https://r.jina.ai/https://github.com/about"
headers = {"Authorization": "Bearer YOUR_JINA_API_KEY"}

response = requests.get(url, headers=headers)
print(response.text)  # 返回Markdown格式
```

---

## 📋 下一步行动清单

### 立即执行 (优先级高)
1. [ ] **GitHub Models**: 访问 https://github.com/marketplace/models 提交早期访问申请
2. [ ] **Jina AI**: 访问 https://jina.ai/?sui=apikey 立即获取免费API密钥
3. [ ] **Perplexity**: 访问 https://www.perplexity.ai 注册并考虑是否升级Pro

### 注册完成后
1. [ ] 将三个API密钥保存到密码管理器
2. [ ] 运行测试代码验证API可用性
3. [ ] 更新 `.env` 文件或环境变量配置

---

## 🔐 API密钥安全存储建议

```bash
# 创建 .env 文件
cat > ~/.api_keys.env << 'EOF'
# API Keys - 2025-03-12
GITHUB_MODELS_PAT=ghp_xxxxxxxxxxxx
PERPLEXITY_API_KEY=pplx_xxxxxxxxxxxx
JINA_API_KEY=jina_xxxxxxxxxxxx
EOF

chmod 600 ~/.api_keys.env
```

---

*文档创建时间: 2025-03-12*  
*维护者: OpenClaw Assistant*
