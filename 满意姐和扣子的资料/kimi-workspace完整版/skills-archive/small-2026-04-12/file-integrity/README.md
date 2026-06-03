> 生成时间: 2026-04-01 14:13+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# 文件完整性检查工具

## 简介

这是一个用于检查文件完整性的命令行工具，支持检查文件存在性、大小、可读性以及关键章节结构。

## 功能特性

- ✅ **文件存在性检查** - 确认目标文件存在
- ✅ **文件大小检查** - 验证文件非空（可配置最小字节数）
- ✅ **内容可读性检查** - 自动检测编码，验证无乱码
- ✅ **章节结构检查** - 使用正则表达式匹配必需标题
- ✅ **灵活配置** - JSON配置文件，支持关键/非关键检查项区分
- ✅ **多种输出** - 支持文本和JSON格式报告

## 安装

无需安装，直接克隆或复制到目标位置即可使用。

```bash
git clone <repository-url>
cd file-integrity
```

## 快速开始

### 1. 基本使用

```bash
python scripts/integrity_checker.py \
  --path /path/to/your/file.txt \
  --config config/check_rules.json
```

### 2. 保存报告到文件

```bash
python scripts/integrity_checker.py \
  --path document.md \
  --config config/check_rules.json \
  --output report.txt
```

### 3. JSON格式输出

```bash
python scripts/integrity_checker.py \
  --path document.md \
  --config config/check_rules.json \
  --format json
```

## 配置文件说明

配置文件 `config/check_rules.json` 使用JSON格式：

```json
{
  "checks": {
    "exists": {
      "enabled": true,
      "critical": true
    },
    "size": {
      "enabled": true,
      "min_bytes": 1,
      "critical": true
    },
    "readable": {
      "enabled": true,
      "lines": 100,
      "critical": true
    },
    "structure": {
      "enabled": true,
      "required_headers": ["^## ", "^### "],
      "critical": false
    }
  },
  "report_template": "standard"
}
```

### 检查项参数

| 检查项 | 参数 | 说明 |
|--------|------|------|
| `exists` | `critical` | 失败时是否终止检查 |
| `size` | `min_bytes` | 最小文件大小（字节） |
| `readable` | `lines` | 检查前N行内容 |
| `structure` | `required_headers` | 必需标题的正则表达式列表 |

## 作为Python模块使用

```python
from scripts.integrity_checker import FileIntegrityChecker

# 创建检查器实例
checker = FileIntegrityChecker('config/check_rules.json')

# 执行检查
report = checker.check_file('/path/to/file.txt')

# 获取结果
print(f"通过: {report.passed}")
print(f"总计检查: {report.summary['total']}")
print(f"失败: {report.summary['failed']}")

# 导出为字典
data = report.to_dict()

# 导出为文本
text = report.to_text()
```

## 退出状态码

| 状态码 | 含义 |
|--------|------|
| 0 | 所有检查通过 |
| 1 | 有关键检查失败 |
| 2 | 有非关键检查失败 |
| 3 | 配置错误或参数错误 |

## CI/CD 集成示例

### GitHub Actions

```yaml
name: File Integrity Check

on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Check README integrity
        run: |
          python skills/file-integrity/scripts/integrity_checker.py \
            --path README.md \
            --config skills/file-integrity/config/check_rules.json
```

### GitLab CI

```yaml
file-integrity-check:
  script:
    - python scripts/integrity_checker.py --path docs/*.md --config config/check_rules.json
  allow_failure: false
```

## 常见问题

### Q: 如何检查多个文件？

可以使用shell循环：

```bash
for file in docs/*.md; do
  echo "Checking: $file"
  python scripts/integrity_checker.py --path "$file" --config config/check_rules.json || true
done
```

### Q: 如何自定义章节检查规则？

修改 `config/check_rules.json` 中的 `structure.required_headers`：

```json
"structure": {
  "enabled": true,
  "required_headers": [
    "^# ",           // 一级标题
    "^## 简介",       // 特定的二级标题
    "^## 安装",
    "^## 使用说明"
  ],
  "critical": false
}
```

### Q: 如何处理不同编码的文件？

工具会自动尝试以下编码：UTF-8、GBK、Latin-1、CP1252。如果都失败，会报告错误。

## 许可证

MIT License
