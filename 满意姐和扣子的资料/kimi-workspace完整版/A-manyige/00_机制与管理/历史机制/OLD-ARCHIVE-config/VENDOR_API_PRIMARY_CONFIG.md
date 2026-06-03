# 厂商API主力方案配置
> **更新日期**: 2026-03-20  
> **主力方案**: 企业微信  
> **备用方案**: 飞书(P1)、Notion(P2)

---

## 主力方案：企业微信

### API能力矩阵

| 功能需求 | 企微API | 状态 | 工具名 |
|----------|---------|------|--------|
| 读取文档 | ✅ | 可用 | get_doc_content |
| 创建文档 | ✅ | 可用 | create_doc |
| 编辑文档 | ✅ | 可用 | edit_doc_content |
| 创建智能表 | ✅ | 可用 | create_doc (doc_type=10) |
| 查询子表 | ✅ | 可用 | smartsheet_get_sheet |
| 添加子表 | ✅ | 可用 | smartsheet_add_sheet |
| 修改子表 | ✅ | 可用 | smartsheet_update_sheet |
| 删除子表 | ✅ | 可用 | smartsheet_delete_sheet |
| 查询字段 | ✅ | 可用 | smartsheet_get_fields |
| 添加字段 | ✅ | 可用 | smartsheet_add_fields |
| 修改字段 | ✅ | 可用 | smartsheet_update_fields |
| 删除字段 | ✅ | 可用 | smartsheet_delete_fields |
| 查询记录 | ✅ | 可用 | smartsheet_get_records |
| 添加记录 | ✅ | 可用 | smartsheet_add_records |
| 修改记录 | ✅ | 可用 | smartsheet_update_records |
| 删除记录 | ✅ | 可用 | smartsheet_delete_records |

### 使用优先级

```
P0（主力）: 企业微信
├── 任务看板 → 企微智能表格
├── 自动记录 → smartsheet_add_records
├── 到期预警 → smartsheet_get_records + 条件判断
└── 自动补救 → smartsheet_update_records

P1（备用）: 飞书
└── 企微不可用时切换

P2（备用）: Notion
└── 企微和飞书都不可用时切换
```

### 切换触发条件

| 条件 | 动作 | 说明 |
|------|------|------|
| 企微API连续3次失败 | 切换至飞书 | 自动切换 |
| 飞书OAuth恢复 | 评估切回企微 | 人工决策 |
| 企微+飞书都不可用 | 切换至Notion | 紧急备用 |

---

## 备用方案：飞书

### 受限功能
- ❌ 需要user_token的自动化操作
- ✅ 基础文档读取
- ✅ 手动触发操作

### 恢复条件
- OAuth2问题解决
- 或找到替代认证方式

---

## 备用方案：Notion

### 当前状态
- ✅ 263文件已同步
- ✅ 全功能API可用
- ✅ 稳定运行

### 使用场景
- 企微和飞书都不可用
- 长期数据归档
- 跨平台备份

---

## 监控配置

### 每日检查（08:00）
```yaml
checks:
  - name: 企微API健康检查
    priority: P0
    action: 调用smartsheet_get_records测试
    
  - name: 飞书OAuth状态
    priority: P1
    action: 检查token有效性
    
  - name: Notion同步状态
    priority: P2
    action: 检查同步任务状态
```

### 告警条件
- 企微API失败 → 立即告警，启动切换
- 飞书OAuth恢复 → 通知，评估切回
- Notion异常 → 记录，不告警（备用）

---

*配置版本: V1.0*  
*最后更新: 2026-03-20*  
*维护者: 满意妞*
## 知识内化记录
**内化时间**: 2026-03-31 | **状态**: ✅ 已内化
