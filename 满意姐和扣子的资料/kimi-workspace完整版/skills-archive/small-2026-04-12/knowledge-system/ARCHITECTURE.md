> 生成时间: 2026-04-01 14:13+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# Knowledge System V1.0 - 统一知识管理系统

> 整合：super-knowledge-ingest + knowledge-ingestion + knowledge-graph + knowledge-graph-framework
> 原则：功能不丢失，架构更统一
> 创建时间：2026-03-28

---

## 一、统一架构设计

### 1.1 四层架构

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: 输入层 (Input Layer)                               │
│  功能：文档接收 + 格式检测 + 预处理                          │
│  来源：knowledge-ingestion                                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: 处理层 (Processing Layer)                          │
│  功能：7层标准处理 (S1-S7)                                   │
│  来源：super-knowledge-ingest V6.0                           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: 存储层 (Storage Layer)                             │
│  功能：三层知识架构 (Session/Project/Asset)                  │
│  来源：knowledge-graph + knowledge-graph-framework           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: 服务层 (Service Layer)                             │
│  功能：查询 + 可视化 + 更新                                  │
│  来源：knowledge-graph-framework                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 功能映射（确保不丢失）

| 原Skill | 核心功能 | 在新架构中的位置 |
|---------|----------|------------------|
| **super-knowledge-ingest** | 7层标准处理 | Layer 2: ProcessingEngine |
| **knowledge-ingestion** | 文档转换+分类+入库流程 | Layer 1: InputHandler + Layer 2: 流程整合 |
| **knowledge-graph** | 三层存储(Session/Project/Asset) | Layer 3: TripleStorage |
| **knowledge-graph-framework** | 实体关系定义+查询+可视化 | Layer 3: Schema + Layer 4: QueryService |

---

## 二、核心模块设计

### 2.1 Layer 1: InputHandler（输入层）

```python
class InputHandler:
    """输入层：接收各种来源的知识"""
    
    def __init__(self):
        self.converters = {
            'docx': DocxConverter(),
            'pdf': PdfConverter(),
            'html': HtmlConverter(),
            'md': MdPassthrough(),
        }
    
    def ingest(self, source, source_type='auto'):
        """
        统一入口
        
        功能来源：knowledge-ingestion
        """
        # 1. 检测格式
        if source_type == 'auto':
            source_type = self._detect_format(source)
        
        # 2. 转换为MD
        if source_type in self.converters:
            md_content = self.converters[source_type].convert(source)
        else:
            md_content = source  # 已经是MD
        
        # 3. 生成元数据
        metadata = {
            'source': source,
            'source_type': source_type,
            'converted_at': time.time(),
            'size_bytes': len(md_content.encode()),
            'checksum': hashlib.md5(md_content.encode()).hexdigest()[:8]
        }
        
        return {
            'content': md_content,
            'metadata': metadata
        }
```

**继承自 knowledge-ingestion 的功能：**
- ✅ 6种来源支持（DOCX, PDF, 网页, 对话, 脚本, 外部链接）
- ✅ 自动格式检测
- ✅ 转换为统一MD格式
- ✅ 元数据提取（来源/大小/校验和）

---

### 2.2 Layer 2: ProcessingEngine（处理层）

```python
class ProcessingEngine:
    """处理层：7层标准处理"""
    
    def __init__(self, output_dir='knowledge/processed'):
        self.output_dir = output_dir
        self.cache = {}  # 内存缓存
        os.makedirs(output_dir, exist_ok=True)
    
    def process(self, input_data):
        """
        7层标准处理
        
        功能来源：super-knowledge-ingest V6.0（完整保留）
        """
        content = input_data['content']
        metadata = input_data['metadata']
        
        # S1: 输入定义（扩展）
        s1 = self._s1_define_input(content, metadata)
        
        # S2: 内容处理（完整保留）
        s2 = self._s2_extract_content(content)
        
        # S3: 知识结构化（增强：整合图谱实体提取）
        s3 = self._s3_structure_knowledge(content, s2)
        
        # S4: 自动化集成（完整保留）
        s4_result = self._s4_auto_integrate(s1, s2, s3)
        
        # S5: 准确性验证（完整保留）
        s5 = self._s5_validate(s1, s2, s3, s4_result)
        
        # S6: 局限标注（完整保留）
        s6 = self._s6_annotate_limits()
        
        # S7: 对抗测试（完整保留）
        s7 = self._s7_adversarial_test(content)
        
        result = {
            's1': s1,
            's2': s2,
            's3': s3,
            's4': s4_result,
            's5': s5,
            's6': s6,
            's7': s7,
            '_': {'v': '1.0', 'ts': time.time()}
        }
        
        return result
```

**继承自 super-knowledge-ingest V6.0 的功能（完整保留）：**
- ✅ S1-S7 完整7层标准
- ✅ 结构缓存 + 磁盘持久化
- ✅ 正则提取（章节/语录/案例）
- ✅ gzip压缩 + base64编码
- ✅ 验证机制（结构/内容/可恢复）
- ✅ 0.13ms缓存命中性能

**增强功能（来自 knowledge-graph）：**
- ✅ 实体提取（人名、术语）
- ✅ 关系抽取（共现关系）
- ✅ 图统计（实体数/关系数/密度）

---

### 2.3 Layer 3: TripleStorage（存储层）

```python
class TripleStorage:
    """存储层：三层知识架构 + 三元组存储"""
    
    def __init__(self, base_path='knowledge'):
        self.base_path = base_path
        # 三层架构（来自knowledge-graph）
        self.layers = {
            'session': SessionLayer(f'{base_path}/session'),      # 短期
            'project': ProjectLayer(f'{base_path}/project'),      # 中期
            'asset': AssetLayer(f'{base_path}/asset')             # 长期
        }
    
    def store(self, processed_data, target_layer='auto'):
        """
        智能分层存储
        
        功能来源：knowledge-graph三层架构 + knowledge-graph-framework三元组
        """
        # 自动判断存储层级
        if target_layer == 'auto':
            target_layer = self._determine_layer(processed_data)
        
        # 存储到对应层级
        layer = self.layers[target_layer]
        
        # 1. 存储文档（7层标准JSON）
        doc_id = layer.store_document(processed_data)
        
        # 2. 提取并存储实体（来自knowledge-graph-framework）
        entities = self._extract_entities(processed_data)
        for entity in entities:
            layer.store_entity(entity)
        
        # 3. 提取并存储关系（来自knowledge-graph-framework）
        relations = self._extract_relations(processed_data)
        for relation in relations:
            layer.store_relation(relation)
        
        # 4. 更新索引
        layer.update_index(doc_id, entities, relations)
        
        return {
            'doc_id': doc_id,
            'layer': target_layer,
            'entities_stored': len(entities),
            'relations_stored': len(relations)
        }
    
    def _determine_layer(self, data):
        """自动判断存储层级"""
        # 会话级：临时对话生成内容
        if data.get('source_type') == 'conversation':
            return 'session'
        
        # 项目级：与当前项目相关的文档
        if data.get('project_code'):
            return 'project'
        
        # 资产级：长期知识资产
        return 'asset'


class SessionLayer:
    """短期层：当前会话缓存（来自knowledge-graph）"""
    
    def __init__(self, path):
        self.path = path
        self.retention = 'current_conversation_only'
        self.limit = '2000_tokens'
    
    def store_document(self, data):
        # 轻量级存储，自动清理
        pass


class ProjectLayer:
    """中期层：项目上下文（来自knowledge-graph）"""
    
    def __init__(self, path):
        self.path = path
        self.tagging = 'project_code/sprint/type'
    
    def store_document(self, data):
        # 按项目标签组织
        pass


class AssetLayer:
    """长期层：知识资产（来自knowledge-graph + framework）"""
    
    def __init__(self, path):
        self.path = path
        # 三元组存储（来自knowledge-graph-framework）
        self.triples = []
        self.entities = {}
        self.relations = {}
    
    def store_entity(self, entity):
        """存储实体（来自knowledge-graph-framework）"""
        self.entities[entity['id']] = entity
    
    def store_relation(self, relation):
        """存储关系（来自knowledge-graph-framework）"""
        self.relations[relation['id']] = relation
        self.triples.append({
            'subject': relation['source'],
            'predicate': relation['type'],
            'object': relation['target']
        })
```

**继承自 knowledge-graph 的功能：**
- ✅ 三层架构（Session/Project/Asset）
- ✅ 自动分层判断
- ✅ 分层存储策略
- ✅ 索引更新

**继承自 knowledge-graph-framework 的功能：**
- ✅ 实体定义（Person/Project/Skill/Concept/Document/Event）
- ✅ 关系定义（created_by/depends_on/related_to/part_of/uses）
- ✅ 三元组存储（Subject-Predicate-Object）
- ✅ 基础实体类型（6类）
- ✅ 基础关系类型（5类）

---

### 2.4 Layer 4: QueryService（服务层）

```python
class QueryService:
    """服务层：查询 + 可视化"""
    
    def __init__(self, storage):
        self.storage = storage
    
    def search(self, query, layer='all'):
        """
        统一查询接口
        
        功能来源：knowledge-graph-framework查询功能
        """
        results = []
        
        # 查询范围
        layers = ['session', 'project', 'asset'] if layer == 'all' else [layer]
        
        for layer_name in layers:
            layer_obj = self.storage.layers[layer_name]
            
            # 1. 文档内容搜索
            doc_results = layer_obj.search_documents(query)
            
            # 2. 实体搜索
            entity_results = layer_obj.search_entities(query)
            
            # 3. 关系搜索
            relation_results = layer_obj.search_relations(query)
            
            results.append({
                'layer': layer_name,
                'documents': doc_results,
                'entities': entity_results,
                'relations': relation_results
            })
        
        return results
    
    def visualize(self, query=None, format='graphviz'):
        """
        可视化导出
        
        功能来源：knowledge-graph-framework可视化
        """
        if format == 'graphviz':
            return self._export_graphviz(query)
        elif format == 'json':
            return self._export_json(query)
        elif format == 'cypher':
            return self._export_cypher(query)
    
    def _export_graphviz(self, query=None):
        """导出Graphviz格式（来自knowledge-graph-framework）"""
        lines = ['digraph KnowledgeGraph {']
        lines.append('  rankdir=LR;')
        
        # 添加实体节点
        for entity_id, entity in self.storage.layers['asset'].entities.items():
            lines.append(f'  "{entity_id}" [label="{entity[\'name\']}", shape=box];')
        
        # 添加关系边
        for relation in self.storage.layers['asset'].relations.values():
            lines.append(f'  "{relation[\'source\']}" -> "{relation[\'target\']}" [label="{relation[\'type\']}"];')
        
        lines.append('}')
        return '\n'.join(lines)
```

**继承自 knowledge-graph-framework 的功能：**
- ✅ 实体查询
- ✅ 关系查询
- ✅ 多层级搜索
- ✅ Graphviz可视化导出
- ✅ JSON导出
- ✅ Cypher导出（Neo4j兼容）

---

## 三、统一入口

```python
class KnowledgeSystem:
    """
    统一知识管理系统
    
    整合4个Skill的完整功能
    """
    
    def __init__(self, base_path='knowledge'):
        # 四层架构
        self.input_handler = InputHandler()
        self.processing_engine = ProcessingEngine(f'{base_path}/processed')
        self.storage = TripleStorage(base_path)
        self.query_service = QueryService(self.storage)
    
    def ingest(self, source, source_type='auto', target_layer='auto'):
        """
        知识入库完整流程
        
        整合4个Skill的功能：
        1. knowledge-ingestion: 输入处理
        2. super-knowledge-ingest: 7层处理
        3. knowledge-graph: 分层存储
        4. knowledge-graph-framework: 实体关系
        """
        # Layer 1: 输入处理
        input_data = self.input_handler.ingest(source, source_type)
        
        # Layer 2: 7层标准处理
        processed = self.processing_engine.process(input_data)
        
        # Layer 3: 分层存储 + 图谱化
        storage_result = self.storage.store(processed, target_layer)
        
        return {
            'success': True,
            'doc_id': storage_result['doc_id'],
            'layer': storage_result['layer'],
            'entities': storage_result['entities_stored'],
            'relations': storage_result['relations_stored'],
            'processing_time_ms': processed['s4'].get('time_ms', 0),
            'cache_hit': processed['s4'].get('cache', False)
        }
    
    def search(self, query, layer='all'):
        """统一查询"""
        return self.query_service.search(query, layer)
    
    def visualize(self, query=None, format='graphviz'):
        """可视化"""
        return self.query_service.visualize(query, format)
```

---

## 四、功能完整性检查

### 4.1 原Skill功能清单

**super-knowledge-ingest** ✅
- [x] 7层标准处理（S1-S7）
- [x] 结构缓存 + 磁盘持久化
- [x] 正则提取（章节/语录/案例）
- [x] gzip压缩 + base64编码
- [x] 验证机制
- [x] 0.13ms缓存命中

**knowledge-ingestion** ✅
- [x] 6种来源支持
- [x] 自动格式检测
- [x] 转换为统一MD
- [x] 元数据提取
- [x] 分类标记

**knowledge-graph** ✅
- [x] 三层架构（Session/Project/Asset）
- [x] 自动分层
- [x] 分层存储策略
- [x] 索引更新

**knowledge-graph-framework** ✅
- [x] 6类实体定义
- [x] 5类关系定义
- [x] 三元组存储
- [x] 查询服务
- [x] Graphviz可视化
- [x] JSON/Cypher导出

### 4.2 新增整合优势

1. **流程统一**：一次调用完成入库全流程
2. **自动分层**：智能判断存储层级
3. **处理增强**：7层处理 + 实体提取一体化
4. **查询统一**：跨层搜索 + 可视化

---

## 五、下一步：五标准化实现

基于上述设计，实现完整的五标准化代码。

---

*统一架构设计完成 - 功能不丢失 - 准备五标准化实现*
