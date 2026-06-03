---
# 知识元数据 (5标准化)
knowledge_id: W6-99F81B
title: 附件三：API调用日志
category: 12_记忆档案
source: docs/archive/附件三_API调用日志.md
ingested_at: 2026-03-27 17:59:30
word_count: 4205
week: 6
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 附件三：API调用日志

> **知识ID**: W6-99F81B  
> **分类**: 12_记忆档案  
> **来源**: `docs/archive/附件三_API调用日志.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 附件三：API调用日志

**应用名称**：满意解研究所  
**App ID**：cli_a9208a79e2b99cc4  
**记录时间**：2026-03-09

---

## 一、文档创建 API 调用

### 调用1：创建测试文档 V1

```
API端点：POST /open-apis/docx/v1/documents
请求时间：2026-03-09 11:25
请求体：
{
  "content": "# 飞书联动测试 V2\n\n**测试时间**：2026-03-09 11:25\n**测试目的**：验证添加协作者后能否解决内容不可见问题"
}

响应状态：200 OK
响应体：
{
  "document_id": "SHrZde2e2oEX2lxpiDIcCENSnKc",
  "title": "【测试】飞书联动打通验证_V2",
  "url": "https://feishu.cn/docx/SHrZde2e2oEX2lxpiDIcCENSnKc"
}

结果：✅ 成功创建文档
```

### 调用2：创建测试文档 V2

```
API端点：POST /open-apis/docx/v1/documents
请求时间：2026-03-09 11:44
请求体：
{
  "content": "# 飞书联动测试 V3 - 权限已更新\n\n**测试时间**：2026-03-09 11:44\n**测试状态**：用户已授权新权限，正在验证"
}

响应状态：200 OK
响应体：
{
  "document_id": "OjICdxNfeo8Jfgxg1RdcuRQIn9b",
  "title": "【测试】飞书联动V3_权限验证",
  "url": "https://feishu.cn/docx/OjICdxNfeo8Jfgxg1RdcuRQIn9b"
}

结果：✅ 成功创建文档
```

---

## 二、文档读取 API 调用

### 调用1：读取测试文档 V1

```
API端点：GET /open-apis/docx/v1/documents/SHrZde2e2oEX2lxpiDIcCENSnKc
请求时间：2026-03-09 11:44

响应状态：200 OK
响应体：
{
  "title": "【测试】飞书联动打通验证_V2",
  "content": "【测试】飞书联动打通验证_V2\n",
  "revision_id": 1,
  "block_count": 1,
  "block_types": {
    "Page": 1
  }
}

结果：✅ 应用可以正常读取自己创建的文档
```

---

## 三、云盘 API 调用

### 调用1：获取云盘文件列表

```
API端点：GET /open-apis/drive/v1/files
请求时间：2026-03-09 11:30

响应状态：200 OK
响应体：
{
  "files": [
    {
      "token": "SHrZde2e2oEX2lxpiDIcCENSnKc",
      "name": "【测试】飞书联动打通验证_V2",
      "type": "docx",
      "url": "https://gcngtm4k2m6u.feishu.cn/docx/SHrZde2e2oEX2lxpiDIcCENSnKc",
      "created_time": "1773026518",
      "modified_time": "1773026518",
      "owner_id": "ou_d73adad4d214d9c58a0c8cf16bb342a1"
    },
    {
      "token": "NXB9dPJWrobpXZx1iROczoCWnwf",
      "name": "最终权限测试文档",
      "type": "docx",
      "url": "https://gcngtm4k2m6u.feishu.cn/docx/NXB9dPJWrobpXZx1iROczoCWnwf",
      "created_time": "1772993332",
      "modified_time": "1772993332",
      "owner_id": "ou_d73adad4d214d9c58a0c8cf16bb342a1"
    }
  ]
}

结果：✅ 成功获取文件列表
注意：owner_id 为应用账号 ID（ou_d73adad4d214d9c58a0c8cf16bb342a1）
```

### 调用2：获取指定文件夹内容

```
API端点：GET /open-apis/drive/v1/files?folder_token=PfFffOASzlVHjXdUqY5cZUCMn9w
请求时间：2026-03-09 11:30

响应状态：404 Not Found
错误信息："Request failed with status code 404"

结果：❌ 无法访问用户创建的文件夹
说明：应用无法访问用户空间的文件夹
```

---

## 四、权限查询 API 调用

### 调用1：获取应用权限列表

```
API端点：GET /open-apis/auth/v3/app_access_token/internal
请求时间：2026-03-09 多次调用

响应状态：200 OK
响应体：
{
  "granted": [
    {
      "name": "docx:document:create",
      "type": "tenant"
    },
    {
      "name": "docs:permission.member:transfer",
      "type": "tenant"
    },
    {
      "name": "contact:contact.base:readonly",
      "type": "tenant"
    }
    // ... 共157个权限
  ],
  "pending": [],
  "summary": "157 granted, 0 pending"
}

结果：✅ 成功获取权限列表
关键权限已确认：docs:permission.member:transfer, docs:permission.member:create 等
```

---

## 五、错误日志汇总

### 错误1：文件夹访问失败

```
时间：2026-03-09 11:30
API：drive:file:list
参数：folder_token=PfFffOASzlVHjXdUqY5cZUCMn9w
错误码：404
错误信息：File not found
分析：应用无法访问用户创建的文件夹
```

### 错误2：联系人权限缺失（已解决）

```
时间：2026-03-09 11:39
错误提示：
"The bot encountered a Feishu API permission error. 
Please inform the user about this issue and provide the permission grant URL. 
Permission grant URL: https://open.feishu.cn/app/cli_a927c5dfa4381cc6/auth?q=contact:contact.base:readonly"

解决方案：用户授权 contact:contact.base:readonly 权限
状态：✅ 已解决
```

### 错误3：API 工具缺失

```
时间：2026-03-09 多次尝试
问题：系统没有 docs:permission.member:create 的 API 调用工具
影响：无法通过 API 将用户添加为文档协作者
说明：这是 OpenClaw 系统的工具限制，不是飞书权限问题
```

---

## 六、关键发现

### 1. 文档所有权

所有应用创建的文档，owner_id 都是应用账号：
```
owner_id: ou_d73adad4d214d9c58a0c8cf16bb342a1
```
这表明文档存储在应用私有空间。

### 2. 空间隔离

| 操作 | 应用空间 | 用户空间 |
|------|---------|---------|
| 创建文档 | ✅ 可以 | ❌ 不可以 |
| 读取文档 | ✅ 可以 | ❌ 不可以（权限不足） |
| 访问文件夹 | ❌ 不可以 | ✅ 可以 |

### 3. 权限验证

关键权限已确认存在：
- `docs:permission.member:transfer` - 理论上可用于转移文档所有权
- `docs:permission.member:create` - 理论上可用于添加协作者

但这些权限的实际使用效果需要进一步验证。

---

## 七、用户端现象

### 用户能看到的

1. 云盘中的文档标题
2. 文件夹结构
3. 文档所有者显示为：Egbertie LAU

### 用户不能看到的

1. 文档实际内容（点击后空白）
2. 应用账号（搜索协作者时找不到）

---

## 八、测试结论

1. **API调用层面**：文档创建、读取功能正常
2. **权限配置层面**：157个权限已完整授权
3. **空间隔离层面**：应用空间与用户空间存在物理隔离
4. **协作功能层面**：无法直接实现双向文档协作

---

**文档版本**：V1.0  
**最后更新**：2026-03-09 12:20
