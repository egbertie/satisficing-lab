> 生成时间: 2026-04-03 14:00+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

003e **状态**: ✅ **FIN**（4/4基础测试通过，可生产使用）

# Skill: knowledge-curator

> **名称**: 知识策展人  
> **版本**: 1.0.0  
> **创建时间**: 2026-04-02  
> **状态**: ✅ 已完成  
> **所属整改步骤**: 第5步

## 功能
CKA-17 Expert，四阶段协议构建顶级文献知识库。

## 四阶段协议
1. 需求图谱分析
2. 文献来源清单构建
3. 向量化处理
4. 质量闸口审查

## API
```python
from knowledge_curator import KnowledgeCurator
curator = KnowledgeCurator(expert_id="CKA-17")
report = curator.full_pipeline("AI ethics research")
```

## 下一步
第6步: 伦理检查Skill