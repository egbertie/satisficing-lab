# 配置验证检查清单

> **配置≠完成，本清单是完成的唯一凭证。**

---

## 使用说明

1. **每次配置任务**必须使用此清单
2. **每完成一项**打勾确认
3. **全部完成后**才能声称"任务完成"
4. **未完成项**必须说明原因和预计完成时间

---

## 通用配置验证清单

### 基础信息
- [ ] 任务名称已明确
- [ ] 配置目标已理解
- [ ] 预期输出已定义
- [ ] 截止时间已确认

### 配置阶段
- [ ] 配置文件已创建/修改
- [ ] 配置内容已检查（存在性检查）
- [ ] 配置语法已验证（语法检查）
- [ ] 配置路径正确
- [ ] 配置格式符合要求

### 权限阶段
- [ ] 文件权限设置正确
- [ ] 执行权限已赋予（如需要）
- [ ] 运行用户已确定
- [ ] 用户权限已验证

### 依赖阶段
- [ ] 所有依赖项已识别
- [ ] API密钥/凭证已配置
- [ ] 网络连接已验证（如需要）
- [ ] 依赖文件/目录已存在

### 验证阶段（强制）
- [ ] 首次执行已测试
- [ ] 输出已接收
- [ ] 输出内容已检查
- [ ] 结果符合预期
- [ ] 错误日志已检查（应无错误）

### 文档阶段
- [ ] 配置变更已记录
- [ ] 验证结果已记录
- [ ] 状态已更新为"已完成"
- [ ] 相关文档已更新

---

## Cron专项验证清单

### 额外检查项（在通用清单基础上）

**Cron表达式**
- [ ] 表达式格式正确（5或6字段）
- [ ] 执行时间符合预期
- [ ] 时区设置正确
- [ ] 已避开整点（如非必须）

**Cron特定验证**
- [ ] 已写入crontab/系统
- [ ] 服务已重启/重载（如需要）
- [ ] 下次执行时间已确认（`crontab -l`查看）
- [ ] 日志轮转已配置

**8步验证状态**
- [ ] Step 1: 配置已写入 ✅
- [ ] Step 2: 语法检查通过 ✅
- [ ] Step 3: 权限验证通过 ✅
- [ ] Step 4: 依赖检查通过 ✅
- [ ] Step 5: 首次执行触发 ✅
- [ ] Step 6: 输出接收确认 ✅
- [ ] Step 7: 结果验证通过 ✅
- [ ] Step 8: 日志记录完成 ✅

---

## API配置验证清单

### 额外检查项（在通用清单基础上）

**凭证验证**
- [ ] API Key已获取
- [ ] API Key已配置到环境变量/配置文件
- [ ] API Key格式正确
- [ ] API Key未过期

**连接验证**
- [ ] 能ping通API端点
- [ ] 测试请求返回200
- [ ] 认证通过（401/403检查）
- [ ] 速率限制已了解

**功能验证**
- [ ] 测试调用成功
- [ ] 返回格式符合预期
- [ ] 错误处理已测试

---

## 文件配置验证清单

### 额外检查项（在通用清单基础上）

**文件存在性**
- [ ] 源文件已存在
- [ ] 目标路径可写
- [ ] 备份已创建（如修改现有配置）

**内容验证**
- [ ] 内容格式正确
- [ ] 关键字段存在
- [ ] 示例值已替换为实际值
- [ ] 注释已清理（如需要）

**验证命令**
```bash
# 检查文件存在
ls -la /path/to/config

# 检查语法（JSON示例）
python3 -m json.tool config.json > /dev/null

# 检查关键字段
python3 -c "import json; d=json.load(open('config.json')); assert 'key' in d"

# 检查权限
stat -c '%a %n' config.json
```

---

## 快速验证命令集

### 文件配置验证
```bash
# 1. 存在性
ls -la /path/to/config

# 2. 语法（JSON）
python3 -m json.tool config.json > /dev/null && echo "Valid JSON"

# 3. 语法（YAML）
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))" && echo "Valid YAML"

# 4. 语法（Shell）
bash -n script.sh && echo "Valid Shell"

# 5. 权限
test -r config.json && echo "Readable"
test -x script.sh && echo "Executable"
```

### Cron配置验证
```bash
# 1. 查看当前cron
crontab -l

# 2. 检查语法
python3 -c "import croniter; croniter.croniter('*/5 * * * *')" && echo "Valid cron"

# 3. 查看cron服务状态
systemctl status cron  # Linux
sudo service cron status  # macOS

# 4. 测试下次执行时间
python3 -c "
import croniter
from datetime import datetime
cron = '*/5 * * * *'
itr = croniter.croniter(cron, datetime.now())
print('Next run:', itr.get_next(datetime))
"
```

### API配置验证
```bash
# 1. 环境变量检查
env | grep API_KEY

# 2. 连接测试
curl -s -o /dev/null -w "%{http_code}" $API_ENDPOINT

# 3. 认证测试
curl -H "Authorization: Bearer $API_KEY" $API_ENDPOINT/health

# 4. 功能测试
curl -X POST $API_ENDPOINT/test -H "Authorization: Bearer $API_KEY"
```

---

## 验证记录模板

每次验证完成后，必须记录：

```markdown
## 验证记录 - [任务名称]

- **验证时间**: YYYY-MM-DD HH:MM:SS
- **验证人**: [姓名/工具]
- **任务类型**: [Cron/API/文件配置]

### 检查结果

| 检查项 | 状态 | 备注 |
|--------|------|------|
| 配置已写入 | ✅/❌ | |
| 语法正确 | ✅/❌ | |
| 权限正确 | ✅/❌ | |
| 依赖就绪 | ✅/❌ | |
| 首次执行成功 | ✅/❌ | |
| 输出符合预期 | ✅/❌ | |

### 问题记录
- [问题描述] → [解决方案]

### 最终状态
- [ ] 已完成（8步全部通过）
- [ ] 配置中（部分通过，需继续）
- [ ] 失败（需要修复）

### 备注
[任何额外信息]
```

---

## 常见错误与解决

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 配置未生效 | 服务未重启 | 重启相关服务 |
| 权限拒绝 | 权限不足 | chmod/chown调整权限 |
| 语法错误 | 格式问题 | 使用验证工具检查 |
| 依赖缺失 | 文件/API不存在 | 检查路径/网络 |
| 输出为空 | 执行失败 | 检查错误日志 |

---

## 强制规则

1. **未完成清单 ≠ 完成任务**
   - 跳过验证 = 虚报完成
   - 后果：信任积分-5

2. **发现错误立即修复**
   - 不拖延、不隐瞒
   - 3分钟内开始整改

3. **记录必须完整**
   - 时间、结果、问题、解决方案
   - 缺一不可

---

**记住：这个清单是完成的唯一凭证。没有它，声称"完成"就是虚报。**
