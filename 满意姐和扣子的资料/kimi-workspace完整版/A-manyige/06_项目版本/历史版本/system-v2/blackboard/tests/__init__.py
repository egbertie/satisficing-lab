# Blackboard V2 测试目录

包含核心组件的单元测试。

运行方式：
```bash
python tests/test_blackboard.py
```

测试覆盖：
- SharedMemory: 线程安全、命名空间隔离
- EventSystem: 发布订阅、通配符匹配
- AuditLogger: 日志记录、搜索、导出
- BlackboardManager: 核心功能、事件集成、持久化
