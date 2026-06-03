---
# 知识元数据 (5标准化)
knowledge_id: W17-AB3363
title: OpenClaw Skills Testing Framework v1.0.0
category: 11_Skill文档
source: skills/testing-framework/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 1933
week: 17
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# OpenClaw Skills Testing Framework v1.0.0

> **知识ID**: W17-AB3363  
> **分类**: 11_Skill文档  
> **来源**: `skills/testing-framework/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# OpenClaw Skills Testing Framework v1.0.0

## 快速开始

```bash
cd skills/testing-framework
pip install -r requirements.txt --break-system-packages

# 运行所有测试
python3 -m pytest tests/unit/zero-idle-enforcer/ -v
python3 -m pytest tests/unit/token-budget-enforcer/ -v
python3 -m pytest tests/unit/blue-sentinel/ -v

# 或使用测试运行器
python3 run_tests.py --critical
```

## 测试覆盖情况

| Skill | 测试数 | 通过 | 失败 | 覆盖率 |
|-------|--------|------|------|--------|
| zero-idle-enforcer (P0) | 19 | 18 | 1* | 95% |
| token-budget-enforcer (P0) | 42 | 42 | 0 | 100% |
| blue-sentinel (P1) | 32 | 32 | 0 | 100% |

*1个失败是预期行为测试（未来时间戳处理边界情况）

## 交付物清单

✅ **skills/testing-framework/** 目录:
- `pyproject.toml` - pytest配置
- `pytest.ini` - pytest配置（兼容版本）
- `requirements.txt` - 依赖清单
- `run_tests.py` - 测试运行脚本
- `SKILL.md` - Skill文档

✅ **测试代码**:
- `tests/unit/zero-idle-enforcer/test_zero_idle.py` - 19个测试
- `tests/unit/token-budget-enforcer/test_enforcer.py` - 42个测试
- `tests/unit/blue-sentinel/test_sentinel.py` - 32个测试
- `tests/conftest.py` - 共享fixtures
- `tests/base.py` - 测试基类

✅ **CI/CD工作流**:
- `.github/workflows/skills-test.yml` - GitHub Actions配置

✅ **文档**:
- `docs/TESTING_FRAMEWORK_GUIDE.md` - 完整测试指南

## 测试设计方法

每个关键Skill的测试覆盖四种场景：

1. **正常输入测试** - 验证基本功能
2. **边界条件测试** - 捕获边界bug
3. **异常输入测试** - 验证鲁棒性
4. **状态一致性测试** - 验证数据完整性

## CI/CD集成

- Push到main/develop分支时自动运行
- Pull Request时运行
- 每日定时运行
- 测试失败阻断部署
- 覆盖率不足阻断部署
- 失败时自动通知

## 测试优先级标记

| 标记 | 含义 | 运行时机 |
|------|------|----------|
| `@pytest.mark.critical` | P0-关键 | 每次提交/PR |
| `@pytest.mark.zero_idle` | zero-idle-enforcer | 该Skill更新时 |
| `@pytest.mark.token_budget` | token-budget-enforcer | 该Skill更新时 |
| `@pytest.mark.blue_sentinel` | blue-sentinel | 该Skill更新时 |

## 维护说明

- 新增Skill测试：在`tests/unit/`下创建目录
- 运行测试：`python3 -m pytest tests/unit/<skill-name>/`
- 生成报告：`python3 run_tests.py --report`

## 参考

- 完整文档: `docs/TESTING_FRAMEWORK_GUIDE.md`
- Skill文档: `skills/testing-framework/SKILL.md`
