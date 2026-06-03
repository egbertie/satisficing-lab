---
# 知识元数据 (5标准化)
knowledge_id: W5-05F11F
title: OpenClaw Skills 测试框架指南
category: 01_研究报告
source: docs/TESTING_FRAMEWORK_GUIDE.md
ingested_at: 2026-03-27 17:59:30
word_count: 11827
week: 5
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# OpenClaw Skills 测试框架指南

> **知识ID**: W5-05F11F  
> **分类**: 01_研究报告  
> **来源**: `docs/TESTING_FRAMEWORK_GUIDE.md`  
> **入库时间**: 2026-03-27

---

## 正文

# OpenClaw Skills 测试框架指南

> **参考对象**: pytest官方最佳实践 + Clean Architecture测试模式 + Google测试策略

---

## 1. 测试框架概述

### 1.1 为什么需要测试框架

在L3维护期，我们发现以下问题需要系统化解决：

| 问题 | 影响 | 测试解决方案 |
|------|------|-------------|
| zero-idle-enforcer发现3次bug | 系统稳定性风险 | 边界条件测试覆盖 |
| 缺乏回归测试 | 修复引入新问题 | 自动化测试套件 |
| 手动验证成本高 | 占用开发时间 | CI/CD自动化 |
| 代码质量难以量化 | 技术债务累积 | 覆盖率指标 |

### 1.2 测试框架目标

1. **P0-Skill全覆盖** - zero-idle-enforcer、token-budget-enforcer、blue-sentinel
2. **自动化运行** - 每次更新自动验证
3. **失败阻断部署** - 测试不通过禁止合并
4. **覆盖率追踪** - 目标≥80%

---

## 2. 快速开始

### 2.1 安装

```bash
cd /root/.openclaw/workspace/skills/testing-framework
pip install -r requirements.txt
```

### 2.2 运行测试

```bash
# 运行所有测试
python run_tests.py

# 运行关键测试（P0）
python run_tests.py --critical

# 运行特定Skill测试
python run_tests.py --skill zero_idle
python run_tests.py --skill token_budget
python run_tests.py --skill blue_sentinel

# 生成完整报告
python run_tests.py --report

# 检查覆盖率
python run_tests.py --coverage 80
```

### 2.3 使用pytest直接运行

```bash
# 运行所有测试
pytest tests/

# 运行特定标记的测试
pytest -m critical          # 关键测试
pytest -m zero_idle         # zero-idle-enforcer测试
pytest -m "not slow"        # 排除慢测试

# 生成覆盖率报告
pytest --cov=skills --cov-report=html

# 失败即停止
pytest -x

# 重新运行失败的测试
pytest --lf
```

---

## 3. 测试设计方法论

### 3.1 测试金字塔

```
      /\
     /  \   E2E测试 (5%)  - 完整用户流程
    /____\  
   /      \  集成测试 (15%) - 组件交互
  /________\
 /          \ 单元测试 (80%) - 函数/方法
/____________\
```

### 3.2 测试用例设计原则

#### 3.2.1 四种必测场景

每个功能点必须覆盖：

| 场景类型 | 目的 | 示例 |
|----------|------|------|
| **正常输入** | 验证基本功能 | 有效时间戳返回正确结果 |
| **边界条件** | 捕获边界bug | 空闲时间=2小时边界 |
| **异常输入** | 验证鲁棒性 | 损坏的JSON文件 |
| **状态一致性** | 验证数据完整性 | 保存后读取结果一致 |

#### 3.2.2 Given-When-Then格式

```python
def test_feature_under_condition(self):
    """测试在特定条件下的功能行为"""
    # Given - 设置初始状态
    state = Builder().with_condition().build()
    
    # When - 执行操作
    result = function_under_test(state)
    
    # Then - 验证结果
    assert result == expected
```

### 3.3 优先级标记

| 标记 | 含义 | 何时运行 |
|------|------|----------|
| `@pytest.mark.critical` | P0-关键 | 每次提交、PR、部署前 |
| `@pytest.mark.unit` | 单元测试 | 开发时、CI中 |
| `@pytest.mark.integration` | 集成测试 | 功能合并前 |
| `@pytest.mark.e2e` | 端到端 | 发布前 |
| `@pytest.mark.slow` | 慢测试 | 夜间定时运行 |

---

## 4. 关键Skill测试详解

### 4.1 zero-idle-enforcer (P0 - 3次bug记录)

**风险点**：
- 时间计算错误
- 状态文件损坏处理
- 边界条件判断

**测试覆盖**：

```python
# 测试文件: tests/unit/zero-idle-enforcer/test_enforcer.py

class TestNormalInputs:
    """正常输入测试"""
    def test_get_last_user_activity_from_heartbeat()  # 从心跳读取
    def test_get_last_user_activity_from_file_mtime() # 从文件mtime推断
    def test_get_token_level_normal()                  # 正常Token级别
    def test_get_token_level_low()                     # 低Token级别
    def test_get_token_level_critical()                # 临界Token级别

class TestBoundaryConditions:
    """边界条件测试"""
    def test_idle_time_exactly_2_hours()               # 正好2小时空闲
    def test_idle_time_just_under_2_hours()            # 略低于2小时
    def test_fill_time_exactly_2_hours_ago()           # 正好2小时前补位
    def test_token_level_at_30_percent_boundary()      # 30%Token边界
    def test_extreme_idle_time_over_30_days()          # 异常空闲时间

class TestInvalidInputs:
    """异常输入测试"""
    def test_heartbeat_state_corrupted_json()          # JSON损坏
    def test_future_activity_time()                    # 未来时间戳
    def test_zero_or_negative_activity_time()          # 零/负时间戳

class TestStateConsistency:
    """状态一致性测试"""
    def test_save_fill_time_updates_state_file()       # 保存更新状态
    def test_enforce_zero_idle_returns_correct_structure()  # 返回结构
```

### 4.2 token-budget-enforcer (P0 - 关键治理)

**风险点**：
- 预算计算错误
- 熔断机制失效
- 阈值判断错误

**测试覆盖**：

```python
# 测试文件: tests/unit/token-budget-enforcer/test_enforcer.py

class TestNormalInputs:
    """正常输入测试"""
    def test_show_budget_displays_correct_totals()     # 预算显示
    def test_estimate_task_for_research_task()         # 研究任务预估
    def test_estimate_task_for_report_task()           # 报告任务预估

class TestBoundaryConditions:
    """边界条件测试"""
    def test_budget_status_at_70_percent_boundary()    # 70%预算边界
    def test_budget_status_at_90_percent_boundary()    # 90%预算边界
    def test_budget_status_at_100_percent_boundary()   # 100%预算边界

class TestStateConsistency:
    """状态一致性测试"""
    def test_budget_calculations_are_consistent()      # 计算一致性
    def test_budget_pools_sum_to_total()               # 预算池求和
```

### 4.3 blue-sentinel (P1 - 5个Skill管理)

**风险点**：
- YAML配置错误
- 审计规则缺失
- 文件结构不一致

**测试覆盖**：

```python
# 测试文件: tests/unit/blue-sentinel/test_sentinel.py

class TestConfigurationStructure:
    """配置结构测试"""
    def test_adversarial_generator_yaml_exists()
    def test_meta_auditor_yaml_is_valid()
    def test_post_hoc_autopsy_yaml_is_valid()
    # ... 其他4个skill

class TestYAMLContentValidation:
    """YAML内容验证"""
    def test_adversarial_generator_has_required_fields()
    def test_all_configs_have_triggers_or_conditions()

class TestCognitiveAuditChecklist:
    """审计检查清单测试"""
    def test_checklist_contains_cognitive_biases()
    def test_checklist_has_structure()
```

---

## 5. 测试工具箱

### 5.1 数据Builders

使用Builder模式创建测试数据：

```python
from tests.base import (
    TokenBudgetBuilder,
    HeartbeatStateBuilder,
    ZeroIdleStateBuilder
)

# Token预算 - 正常状态
token_data = TokenBudgetBuilder().normal().build()

# Token预算 - 临界状态
token_data = TokenBudgetBuilder().critical().build()

# Token预算 - 自定义百分比
token_data = TokenBudgetBuilder().with_percentage(45).build()

# 心跳状态 - 特定空闲时间
state_data = HeartbeatStateBuilder().with_idle_time(7200).build()

# Zero-Idle状态 - 最近补位
idle_state = ZeroIdleStateBuilder().recently_filled(minutes_ago=30).build()
```

### 5.2 Fixtures

conftest.py提供的共享fixtures：

```python
# 临时目录
def test_with_temp_dir(temp_dir: Path):
    file_path = temp_dir / "test.txt"
    file_path.write_text("content")

# Mock状态文件
def test_with_state(mock_heartbeat_state, mock_token_weekly_monitor):
    result = get_last_user_activity()
    assert result > 0

# Mock时间
def test_with_time(mock_time):
    mock_time.return_value = 1704067200
    result = timestamp_function()
    assert result == 1704067200
```

### 5.3 断言辅助

```python
from tests.base import AssertHelpers

# 范围断言
AssertHelpers.assert_within_range(value, expected, tolerance=0.01)

# 时间戳有效性
AssertHelpers.assert_is_valid_timestamp(timestamp, max_age_seconds=60)

# JSON结构
AssertHelpers.assert_json_structure(data, ["key1", "key2", "key3"])

# 文件内容
AssertHelpers.assert_file_contains(file_path, "expected substring")

# 日志条目
AssertHelpers.assert_valid_log_entry(log_line, expected_level="INFO")
```

---

## 6. CI/CD集成

### 6.1 GitHub Actions工作流

**文件**: `.github/workflows/skills-test.yml`

**触发条件**：
- Push到main/develop/feature/*分支
- 修改skills/目录的Pull Request
- 每日定时运行（UTC 18:00）
- 手动触发

**任务流程**：

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  预检查      │────▶│  单元测试    │────▶│  关键测试    │
│ (检测变更)   │     │ (并行5个)   │     │   (P0)      │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                                │
                       ┌───────────────────────┘
                       ▼
               ┌─────────────┐     ┌─────────────┐
               │  覆盖率检查  │────▶│  报告生成    │
               │  (≥80%)     │     │  &通知       │
               └─────────────┘     └─────────────┘
```

### 6.2 失败处理

**测试失败时**：
1. CI/CD流程停止
2. PR禁止合并
3. 发送通知（Issue/邮件）
4. 生成详细日志供调试

**覆盖率不足时**：
1. 同样阻断部署
2. 显示未覆盖代码行
3. 提供改进建议

### 6.3 查看测试报告

每次运行后生成：

| 报告类型 | 位置 | 用途 |
|----------|------|------|
| HTML测试报告 | `reports/test_report.html` | 可视化测试结果 |
| 覆盖率报告 | `reports/coverage/index.html` | 代码覆盖详情 |
| JSON数据 | `reports/test_results.json` | 程序化分析 |
| JUnit XML | `reports/junit.xml` | CI/CD集成 |

---

## 7. 编写新测试指南

### 7.1 为新Skill添加测试

**步骤1**: 创建目录结构

```bash
mkdir -p tests/unit/my-new-skill
touch tests/unit/my-new-skill/__init__.py
touch tests/unit/my-new-skill/test_main.py
```

**步骤2**: 编写测试类

```python
# tests/unit/my-new-skill/test_main.py
import pytest
from tests.base import SkillTestCase

@pytest.mark.my_new_skill  # 添加标记
class TestMyNewSkill(SkillTestCase):
    """My New Skill测试类"""
    
    SKILL_NAME = "my-new-skill"
    
    def setup_method(self):
        """测试前设置"""
        super().setup_method()
        # 自定义设置
    
    # === 正常输入测试 ===
    def test_normal_operation(self):
        """测试正常操作"""
        pass
    
    # === 边界条件测试 ===
    def test_boundary_condition(self):
        """测试边界条件"""
        pass
    
    # === 异常输入测试 ===
    def test_invalid_input(self):
        """测试异常输入"""
        pass
    
    # === 状态一致性测试 ===
    def test_state_consistency(self):
        """测试状态一致性"""
        pass
```

**步骤3**: 注册标记

在`pyproject.toml`中添加：

```toml
[tool.pytest.ini_options]
markers = [
    # ... 现有标记
    "my_new_skill: my-new-skill tests",
]
```

**步骤4**: 更新CI/CD（可选）

在`.github/workflows/skills-test.yml`中添加：

```yaml
strategy:
  matrix:
    skill: [zero-idle-enforcer, token-budget-enforcer, blue-sentinel, my-new-skill]
```

### 7.2 测试最佳实践

#### ✅ 应该做的

- **使用描述性名称**: `test_idle_time_exactly_2_hours` 而不是 `test1`
- **一个测试一个概念**: 每个测试只验证一件事
- **使用Builders**: 而不是硬编码测试数据
- **独立测试**: 测试之间不应有依赖
- **快速执行**: 单元测试应该 < 100ms

#### ❌ 避免的做法

- **不要**: 在一个测试中验证多个不相关的行为
- **不要**: 依赖测试执行顺序
- **不要**: 使用sleep等待
- **不要**: 访问真实的外部服务
- **不要**: 忽略测试失败（除非已记录问题）

---

## 8. 故障排查

### 8.1 测试不通过

```bash
# 查看详细错误
pytest -v --tb=long tests/unit/zero-idle-enforcer/

# 进入pdb调试
pytest --pdb

# 仅运行失败的测试
pytest --lf -v
```

### 8.2 覆盖率不足

```bash
# 查看未覆盖代码
pytest --cov=skills --cov-report=term-missing

# 生成HTML报告查看
pytest --cov=skills --cov-report=html:reports/coverage
# 然后打开 reports/coverage/index.html
```

### 8.3 Fixture问题

```bash
# 列出所有可用的fixtures
pytest --fixtures

# 查看fixture详细信息
pytest --fixtures-per-test
```

---

## 9. 维护与扩展

### 9.1 定期任务

| 频率 | 任务 | 负责人 |
|------|------|--------|
| 每日 | 检查CI/CD状态 | 自动化 |
| 每周 | 审查覆盖率趋势 | 技术负责人 |
| 每月 | 评估测试有效性 | 团队 |
| 每季 | 更新测试框架版本 | 技术负责人 |

### 9.2 添加新测试类型

如需添加集成测试：

```bash
mkdir -p tests/integration/my-skill
touch tests/integration/my-skill/test_integration.py
```

在测试中使用`@pytest.mark.integration`标记。

### 9.3 性能测试

如需添加性能测试：

```python
import pytest

@pytest.mark.benchmark
@pytest.mark.slow
def test_performance(benchmark):
    """性能测试"""
    result = benchmark(function_to_test, data)
    assert result is not None
```

---

## 10. 参考资源

### 10.1 测试理论

- [测试金字塔 (Martin Fowler)](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Given-When-Then](https://martinfowler.com/bliki/GivenWhenThen.html)
- [Arrange-Act-Assert](http://wiki.c2.com/?ArrangeActAssert)

### 10.2 pytest资源

- [pytest官方文档](https://docs.pytest.org/)
- [pytest最佳实践](https://docs.pytest.org/en/latest/explanation/goodpractices.html)
- [pytest fixtures](https://docs.pytest.org/en/latest/how-to/fixtures.html)

### 10.3 Python测试

- [Python测试指南](https://realpython.com/python-testing/)
- [Mock对象指南](https://realpython.com/python-mock-library/)

---

## 附录: 快速参考卡

### 常用命令

```bash
# 安装
pip install -r requirements.txt

# 运行
python run_tests.py
python run_tests.py --critical
python run_tests.py --skill zero_idle
python run_tests.py --coverage 80
python run_tests.py --report

# pytest直接
pytest tests/
pytest -m critical
pytest -x
pytest --lf
pytest -v --tb=short
```

### 测试模板

```python
import pytest
from tests.base import SkillTestCase, TokenBudgetBuilder

@pytest.mark.my_skill
@pytest.mark.critical
class TestMySkill(SkillTestCase):
    
    def test_normal_case(self):
        # Arrange
        data = TokenBudgetBuilder().normal().build()
        # Act
        result = my_function(data)
        # Assert
        assert result == expected
    
    def test_boundary(self):
        pass
    
    def test_invalid(self):
        pass
    
    def test_consistency(self):
        pass
```

---

*文档版本: v1.0.0*  
*更新日期: 2026-03-21*  
*作者: 满意解研究所*
