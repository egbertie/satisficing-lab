#!/usr/bin/env python3
"""
案例库管理CLI工具 - MVP版本
基于案例库深度方案文档实施
"""

import click
import json
import sqlite3
import os
from datetime import datetime
from pathlib import Path

# 配置
DATA_DIR = Path("/root/.openclaw/workspace/case_repo_mvp/data")
REPORTS_DIR = Path("/root/.openclaw/workspace/case_repo_mvp/reports")
DB_PATH = DATA_DIR / "cases.db"

@click.group()
def cli():
    """案例库管理工具 - 满意解研究所"""
    pass

@cli.command()
def init():
    """初始化案例库"""
    # 创建目录
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 创建数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建案例表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            industry TEXT,
            stage TEXT,
            founder_name TEXT,
            founder_background TEXT,
            partner_name TEXT,
            partner_background TEXT,
            conflict_type TEXT,
            conflict_outcome TEXT,
            lessons TEXT,
            source TEXT,
            reliability TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    click.echo(f"✅ 案例库初始化完成")
    click.echo(f"   数据目录: {DATA_DIR}")
    click.echo(f"   报告目录: {REPORTS_DIR}")
    click.echo(f"   数据库: {DB_PATH}")

@cli.command()
@click.option('--file', '-f', help='JSON文件路径')
def add(file):
    """添加新案例"""
    if not DB_PATH.exists():
        click.echo("❌ 案例库未初始化，请先运行: case-repo init")
        return
    
    if file:
        # 从文件导入
        with open(file, 'r', encoding='utf-8') as f:
            case_data = json.load(f)
    else:
        # 交互式输入
        click.echo("请输入案例信息（直接回车跳过可选字段）：")
        case_data = {
            "case_id": click.prompt("案例ID"),
            "title": click.prompt("案例标题"),
            "industry": click.prompt("行业", default=""),
            "stage": click.prompt("融资阶段", default=""),
            "founder_name": click.prompt("创始人姓名", default=""),
            "founder_background": click.prompt("创始人背景", default=""),
            "partner_name": click.prompt("合伙人姓名", default=""),
            "partner_background": click.prompt("合伙人背景", default=""),
            "conflict_type": click.prompt("冲突类型", default=""),
            "conflict_outcome": click.prompt("冲突结果", default=""),
            "lessons": click.prompt("经验教训", default=""),
            "source": click.prompt("案例来源", default=""),
            "reliability": click.prompt("可信度(A/B/C)", default="B")
        }
    
    # 保存到数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO cases 
        (case_id, title, industry, stage, founder_name, founder_background,
         partner_name, partner_background, conflict_type, conflict_outcome,
         lessons, source, reliability)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        case_data['case_id'],
        case_data['title'],
        case_data.get('industry', ''),
        case_data.get('stage', ''),
        case_data.get('founder_name', ''),
        case_data.get('founder_background', ''),
        case_data.get('partner_name', ''),
        case_data.get('partner_background', ''),
        case_data.get('conflict_type', ''),
        case_data.get('conflict_outcome', ''),
        case_data.get('lessons', ''),
        case_data.get('source', ''),
        case_data.get('reliability', 'B')
    ))
    
    conn.commit()
    conn.close()
    
    click.echo(f"✅ 案例已添加: {case_data['case_id']}")

@cli.command()
def list():
    """列出所有案例"""
    if not DB_PATH.exists():
        click.echo("❌ 案例库未初始化")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT case_id, title, industry, stage FROM cases")
    cases = cursor.fetchall()
    conn.close()
    
    if not cases:
        click.echo("暂无案例")
        return
    
    click.echo(f"\n{'案例ID':<15} {'标题':<30} {'行业':<15} {'阶段':<10}")
    click.echo("-" * 70)
    for case in cases:
        click.echo(f"{case[0]:<15} {case[1]:<30} {case[2]:<15} {case[3]:<10}")

@cli.command()
@click.argument('case_id')
def report(case_id):
    """生成案例复盘报告"""
    if not DB_PATH.exists():
        click.echo("❌ 案例库未初始化")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
    case = cursor.fetchone()
    conn.close()
    
    if not case:
        click.echo(f"❌ 案例不存在: {case_id}")
        return
    
    # 生成报告
    report_content = f"""# {case[1]} - 复盘报告

## 基本信息
- **案例ID**: {case[0]}
- **行业**: {case[2] or '未填写'}
- **融资阶段**: {case[3] or '未填写'}
- **入库时间**: {case[13]}

## 当事人信息
### 创始人
- **姓名**: {case[4] or '未填写'}
- **背景**: {case[5] or '未填写'}

### 合伙人
- **姓名**: {case[6] or '未填写'}
- **背景**: {case[7] or '未填写'}

## 冲突分析
- **冲突类型**: {case[8] or '未填写'}
- **冲突结果**: {case[9] or '未填写'}

## 经验教训
{case[10] or '未填写'}

## 附录
- **案例来源**: {case[11] or '未填写'}
- **可信度等级**: {case[12] or 'B'}

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    # 保存报告
    report_path = REPORTS_DIR / f"{case_id}_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    click.echo(f"✅ 复盘报告已生成: {report_path}")
    click.echo("\n报告预览:")
    click.echo("-" * 50)
    click.echo(report_content[:500] + "...")

if __name__ == '__main__':
    cli()
