# 模块04: Step1 — 海啸导入实战

> **编号**: SSW-613
> **时长**: 30分钟
> **产出**: 文件索引 + 扫描报告

---

## 操作步骤

```bash
# 运行海啸导入
python3 scripts/tsunami-ingest.py \
  --input /path/to/your/files \
  --output ./out/01_ingest \
  --batch-size 1000 \
  --verbose
```

## 验证检查

- [ ] 01_初始索引.json 存在且非空
- [ ] 02_文件元数据.csv 有统计数字
- [ ] 00_扫描报告.md 人类可读

## 常见错误

1. **路径不存在**: 确认 `--input` 路径正确
2. **权限不足**: `chmod -R 755` 输入目录
3. **内存溢出**: 减小 `--batch-size` 到 500

## 本节产出

扫描报告 + 对文件总量的认知

---

*模块04版本: V1.0*
*编号: SSW-613*
