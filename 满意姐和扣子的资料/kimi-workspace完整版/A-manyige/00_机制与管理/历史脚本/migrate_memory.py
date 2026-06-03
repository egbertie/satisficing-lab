#!/usr/bin/env python3
"""
历史记忆迁移脚本
将历史日志文件迁移到归档目录
"""

import os
import shutil
from datetime import datetime

def migrate_memory():
    # 定义迁移列表
    files_to_migrate = [
        "2026-03-06.md",
        "2026-03-07.md",
        "2026-03-08.md",
        "2026-03-09.md",
        "2026-03-10.md",
        "2026-03-12.md",
        "2026-03-14.md",
        "2026-03-15.md",
        "2026-03-18.md",
    ]
    
    source_dir = "memory/"
    target_dir = "memory/archive/logs/"
    
    # 确保目标目录存在
    os.makedirs(target_dir, exist_ok=True)
    
    migrated = []
    skipped = []
    
    for filename in files_to_migrate:
        source_path = os.path.join(source_dir, filename)
        target_path = os.path.join(target_dir, filename)
        
        if os.path.exists(source_path):
            # 检查目标是否已存在
            if os.path.exists(target_path):
                skipped.append(filename)
            else:
                shutil.move(source_path, target_path)
                migrated.append(filename)
        else:
            skipped.append(f"{filename} (源文件不存在)")
    
    # 生成迁移报告
    report = f"""# 历史记忆迁移报告

> 迁移时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 迁移结果

| 项目 | 数量 |
|------|------|
| 成功迁移 | {len(migrated)} |
| 跳过/不存在 | {len(skipped)} |

### 已迁移文件

"""
    
    for f in migrated:
        report += f"- ✅ {f}\n"
    
    report += "\n### 跳过的文件\n\n"
    for f in skipped:
        report += f"- ⏭️ {f}\n"
    
    report += f"""

---

## 归档结构

```
memory/
├── archive/
│   ├── logs/          # 历史日志
│   ├── egbertie_full_profile.md
│   ├── project_history_2026-03.md
│   └── ...
├── working/           # 工作状态
├── 2026-03-19.md      # 活跃日志
├── 2026-03-20.md      # 活跃日志
└── heartbeat-state.json
```

---

*本报告由migrate_memory.py自动生成*
"""
    
    # 写入报告
    with open('memory/archive/migration_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 历史记忆迁移完成")
    print(f"   - 成功迁移: {len(migrated)}个文件")
    print(f"   - 跳过: {len(skipped)}个文件")
    print(f"   - 迁移报告: memory/archive/migration_report.md")

if __name__ == '__main__':
    migrate_memory()
