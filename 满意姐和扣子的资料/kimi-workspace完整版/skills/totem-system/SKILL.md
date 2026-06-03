> 生成时间: 2026-04-03 14:00+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

003e **状态**: ✅ **FIN**（4/4基础测试通过，可生产使用）

# Skill: 五路图腾体系 (Totem System)

## 触发条件

当用户需要：
- 执行晨间/黄昏图腾仪式
- 激活五路图腾工作框架
- 进行每日工作启动/收尾
- 提到"图腾"、"仪式"、"晨间"、"黄昏"

## 执行流程

### 晨间仪式 (09:00)

```bash
python3 skills/totem-system/morning-ritual.py
```

**功能**：
1. 激活6图腾（刘禹锡/司马贺/观自在/孔子/六祖慧能 + 刘禹锡-MIRROR）
2. 加载当日工作框架
3. 生成晨间仪式记录

**输出**：
- 终端输出仪式状态
- 文件保存到 `memory/totem-rituals/YYYY-MM-DD-morning.json`

### 黄昏仪式 (18:00)

```bash
python3 skills/totem-system/evening-ritual.py
```

**功能**：
1. 归档当日收获
2. 质量检查
3. 生成明日风险预警

**输出**：
- 终端输出仪式状态
- 文件保存到 `memory/totem-rituals/YYYY-MM-DD-evening.json`

## 物理验证

**脚本存在性**：
```bash
ls -la skills/totem-system/*.py
```

**可运行性验证**：
```bash
python3 skills/totem-system/morning-ritual.py --dry-run
python3 skills/totem-system/evening-ritual.py --dry-run
```

## 状态

- **创建时间**：2026-03-22
- **最后验证**：2026-03-30
- **可运行性**：🔄 已验证

## 依赖

- Python 3.8+
- 依赖文件：`memory/totem-rituals/` 目录

---

*此SKILL.md于2026-03-30补充，整改P0-001审计发现的问题*

## 知识内化记录
**内化时间**: 2026-03-31 | **状态**: ✅ 已内化
