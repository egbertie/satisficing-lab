---
kia-version: 1.0
tier: T0
title: Token优化配置文档
source: docs/assets/token_optimization.md
ingested: 2026-04-16
tags: [auto-kia, docs, BatchA-docs-01]
---

> 生成时间: 2026-04-04 00:15+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# Token优化配置文档
# 边缘预处理 + 分级处理 + 三级缓存 综合方案

## 一、边缘预处理层（节省60% Token）

### 1.1 本地LLM服务配置

```yaml
# docker-compose.local-llm.yml
services:
  local-llm:
    image: registry.cn-hangzhou.aliyuncs.com/qwen/qwen2.5:7b-instruct
    command: >
      --model /models/Qwen2.5-7B-Instruct
      --served-model-name local-preprocessor
      --max-model-len 8192
      --gpu-memory-utilization 0.8
      --tensor-parallel-size 1
      --dtype bfloat16
    ports:
      - "8000:8000"
    volumes:
      - ./models:/models
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - CUDA_VISIBLE_DEVICES=0
```

### 1.2 预处理任务清单

| 任务 | 本地LLM | Kimi | 节省 |
|------|---------|------|------|
| 文件类型识别 | ✅ | ❌ | 100% |
| 复杂度评估 | ✅ | ❌ | 100% |
| 文本清洗/去噪 | ✅ | ❌ | 100% |
| 初步摘要生成 | ✅ | ❌ | 100% |
| 关键词提取 | ✅ | ❌ | 100% |
| 五图腾分类 | ⚠️ | ✅ | 50% |
| 深度内化 | ❌ | ✅ | 0% |

### 1.3 复杂度评估算法

```python
def assess_complexity(text: str) -> Dict:
    """本地预处理：评估文档复杂度，决定处理Pipeline"""
    
    # 基础指标
    char_count = len(text)
    sentence_count = len(re.split(r'[。！？.!?]', text))
    
    # 专业术语密度
    tech_terms = ['算法', '架构', '系统', '协议', '引擎', '模型']
    term_density = sum(1 for term in tech_terms if term in text) / char_count * 1000
    
    # 结构化程度
    has_tables = '|' in text or '表格' in text
    has_code = '```' in text or 'def ' in text
    has_formulas = '$' in text or '公式' in text
    
    # 复杂度评分
    score = 0
    if char_count > 50000: score += 30
    elif char_count > 10000: score += 20
    elif char_count > 5000: score += 10
    
    if term_density > 5: score += 20
    if has_tables: score += 10
    if has_code: score += 15
    if has_formulas: score += 15
    
    # Pipeline推荐
    if score < 30:
        return {'complexity': 'low', 'pipeline': 'light', 'estimated_tokens': 150}
    elif score < 60:
        return {'complexity': 'medium', 'pipeline': 'standard', 'estimated_tokens': 300}
    else:
        return {'complexity': 'high', 'pipeline': 'deep', 'estimated_tokens': 800}
```

## 二、分级处理Pipeline（节省15% Token）

### 2.1 三级Pipeline定义

```python
class TieredProcessingPipeline:
    """分级处理：根据复杂度选择不同深度的处理策略"""
    
    def __init__(self, local_llm_url: str, kimi_api_key: str):
        self.local_llm = LocalLLMClient(local_llm_url)
        self.kimi = KimiClient(kimi_api_key)
        self.cache = TieredCache()
    
    def process(self, file_path: str) -> Dict:
        # Step 1: 本地预处理（评估复杂度）
        edge_result = self._edge_preprocess(file_path)
        pipeline = edge_result['complexity']['recommended_pipeline']
        
        # Step 2: 根据复杂度选择Pipeline
        if pipeline == 'light':
            return self._light_pipeline(edge_result)      # <150T
        elif pipeline == 'standard':
            return self._standard_pipeline(edge_result)   # <300T
        else:
            return self._deep_pipeline(edge_result)       # <800T
    
    def _light_pipeline(self, context: Dict) -> Dict:
        """轻量Pipeline：简单文档快速处理"""
        # 本地生成结构摘要
        summary = self.local_llm.generate_summary(
            context['text'],
            max_length=500,
            focus='structure'
        )
        
        # Kimi仅做质量验证（少量Token）
        validation = self.kimi.quick_check(summary, max_tokens=100)
        
        return {
            'pipeline': 'light',
            'tokens_used': context['tokens_used'],
            'output': summary,
            'validation': validation
        }
    
    def _standard_pipeline(self, context: Dict) -> Dict:
        """标准Pipeline：常规文档标准处理"""
        # 本地提取关键信息
        key_points = self.local_llm.extract_key_points(context['text'])
        
        # Kimi进行深度分析和结构化
        analysis = self.kimi.analyze_with_structure(
            context['text'],
            structure=['背景', '核心论点', '证据', '结论', '启示'],
            max_tokens=800
        )
        
        return {
            'pipeline': 'standard',
            'tokens_used': context['tokens_used'] + 800,
            'key_points': key_points,
            'analysis': analysis
        }
    
    def _deep_pipeline(self, context: Dict) -> Dict:
        """深度Pipeline：复杂文档全面内化"""
        # 本地预处理：分段、去噪、结构识别
        segments = self.local_llm.segment_document(context['text'])
        
        # Kimi进行五重门内化（完整流程）
        internalization = self.kimi.deep_internalization(
            segments,
            passes=['reading', 'notes', 'summary', 'verification'],
            totem_template=True,
            max_tokens=3000
        )
        
        return {
            'pipeline': 'deep',
            'tokens_used': context['tokens_used'] + 3000,
            'segments': segments,
            'internalization': internalization
        }
```

### 2.2 Token预算分配

| Pipeline | 本地Token | Kimi Token | 总计 | 适用场景 |
|----------|-----------|------------|------|----------|
| Light | 50 | 100 | **150** | 简单文档、会议纪要 |
| Standard | 100 | 200 | **300** | 常规报告、文章 |
| Deep | 200 | 600 | **800** | 复杂方案、技术文档 |

## 三、三级缓存系统（节省5% Token）

### 3.1 缓存架构

```python
class TieredCache:
    """三级缓存：L1内存 → L2Redis → L3语义向量"""
    
    def __init__(self, redis_client, vector_store):
        self.l1_memory = {}  # 进程内内存缓存
        self.l2_redis = redis_client
        self.l3_vector = vector_store
        self.l1_ttl = 300    # 5分钟
        self.l2_ttl = 3600   # 1小时
        self.l3_ttl = 86400  # 24小时
    
    def get(self, key: str) -> Optional[Dict]:
        # L1: 内存缓存（最快）
        if key in self.l1_memory:
            value, expiry = self.l1_memory[key]
            if time.time() < expiry:
                return {'value': value, 'source': 'L1_memory'}
        
        # L2: Redis缓存
        l2_value = self.l2_redis.get(key)
        if l2_value:
            self.l1_memory[key] = (l2_value, time.time() + self.l1_ttl)
            return {'value': l2_value, 'source': 'L2_redis'}
        
        # L3: 语义向量缓存（模糊匹配）
        similar = self.l3_vector.similarity_search(key, k=1)
        if similar and similar[0]['score'] > 0.95:
            self.l2_redis.setex(key, self.l2_ttl, similar[0]['value'])
            return {'value': similar[0]['value'], 'source': 'L3_vector'}
        
        return None
    
    def set(self, key: str, value: Dict, ttl: int = None):
        # 写入L1
        self.l1_memory[key] = (value, time.time() + self.l1_ttl)
        
        # 写入L2
        self.l2_redis.setex(key, ttl or self.l2_ttl, json.dumps(value))
        
        # 写入L3（向量化）
        embedding = self._embed(key + ' ' + str(value)[:500])
        self.l3_vector.upsert(key, embedding, value)
```

### 3.2 缓存命中率目标

| 层级 | 目标命中率 | 延迟 | 容量 |
|------|-----------|------|------|
| L1 Memory | 60% | <1ms | 1000条 |
| L2 Redis | 25% | <10ms | 10万条 |
| L3 Vector | 10% | <100ms | 100万条 |
| **总计** | **95%** | - | - |

## 四、成本对比

| 方案 | 单次入库Token | 100次/月成本 | 年度成本 |
|------|--------------|--------------|----------|
| 优化前 | 2500-4500 | ¥5250 | ¥63,000 |
| 优化后 | 430-950 | ¥1050 | ¥12,600 |
| 本地模型成本 | - | ¥2000 | ¥24,000 |
| **净节省** | **-80%** | **¥2200/月** | **¥26,400/年** |

## 五、实施清单

### 5.1 立即部署（今晚）
- [ ] 配置本地LLM服务（Qwen-7B）
- [ ] 部署Redis缓存服务
- [ ] 初始化三级缓存表结构

### 5.2 本周完成
- [ ] 集成复杂度评估算法
- [ ] 部署分级处理Pipeline
- [ ] 配置Token消耗监控

### 5.3 持续优化
- [ ] 根据实际数据校准复杂度阈值
- [ ] 优化缓存策略（命中率分析）
- [ ] A/B测试验证成本节省效果
