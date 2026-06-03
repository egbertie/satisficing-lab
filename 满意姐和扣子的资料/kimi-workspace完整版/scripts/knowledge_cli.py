#!/usr/bin/env python3
"""
SRI Agent OS 知识内化系统 CLI
执行五重门内化流程：登记→通读→笔记→总结→验证
"""

import click
import json
import yaml
import os
import sys
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, '/root/.openclaw/workspace/docs/assets')

from knowledge_ingestion import KnowledgeIngestionEngine, FileMetadata


class Config:
    def __init__(self, config_path='/root/.openclaw/workspace/config/sri_agent_os.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.db_config = self.config['database']
        self.redis_config = self.config['redis']
        self.storage_config = self.config['storage']
        self.kimi_config = self.config['kimi']
        self.internalization_config = self.config['internalization']


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.option('--config', '-c', default='/root/.openclaw/workspace/config/sri_agent_os.yaml',
              help='配置文件路径')
@click.pass_context
def cli(ctx, config):
    """SRI Agent OS 知识内化系统"""
    ctx.ensure_object(Config)
    ctx.obj = Config(config)


@cli.command()
@click.argument('file_path')
@click.option('--source', '-s', default='cli', help='文件来源')
@click.option('--created-by', '-u', default='sri-agent', help='创建者')
@pass_config
def ingest(config, file_path, source, created_by):
    """执行知识内化（五重门流程）"""
    
    click.echo(f"🚀 开始知识内化: {file_path}")
    click.echo(f"   来源: {source}")
    click.echo(f"   创建者: {created_by}")
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        click.echo(f"❌ 文件不存在: {file_path}", err=True)
        return
    
    # 初始化引擎（简化版，实际应传入真实客户端）
    engine = KnowledgeIngestionEngine(
        local_llm_client=None,
        kimi_client=None,  # 实际使用时应初始化真实客户端
        db_client=None,
        storage_client=None
    )
    
    try:
        result = engine.ingest(file_path, source, created_by)
        
        click.echo(f"\n{'='*60}")
        click.echo(f"✅ 知识内化完成!")
        click.echo(f"   文件ID: {result['file_id']}")
        click.echo(f"   状态: {result['status']}")
        click.echo(f"   验证得分: {result['verification_score']}")
        click.echo(f"   可复用资产: {len(result['reusable_assets'])}个")
        click.echo(f"   处理时间: {result['processing_time']}")
        
        if result['status'] == 'verified':
            click.echo(f"\n🎉 验证通过，已归档!")
        else:
            click.echo(f"\n⚠️  验证未通过，需要改进")
        
    except Exception as e:
        click.echo(f"❌ 内化失败: {str(e)}", err=True)


@cli.command()
@click.argument('file_id')
@pass_config
def status(config, file_id):
    """查询内化状态"""
    click.echo(f"📊 查询文件状态: {file_id}")
    # 实际实现应查询数据库
    click.echo("   状态: processing")
    click.echo("   当前阶段: pass_2_notes")


@cli.command()
@click.option('--limit', '-l', default=10, help='显示最近N条记录')
@pass_config
def list(config, limit):
    """列出最近内化记录"""
    click.echo(f"📋 最近{limit}条内化记录:")
    click.echo("-" * 60)
    # 实际实现应查询数据库
    click.echo("暂无记录（系统刚初始化）")


@cli.command()
@click.argument('file_path')
@pass_config
def demo(config, file_path):
    """运行知识内化演示"""
    
    click.echo("🎬 运行知识内化演示（简化版）")
    click.echo("="*60)
    
    # 模拟五重门流程
    stages = [
        ("门1: 登记门", "文件指纹 + 五图腾分类 + 3-2-1备份", 3),
        ("门2: 通读门", "理解核心，生成结构大纲", 5),
        ("门3: 笔记门", "五图腾五维分析", 10),
        ("门4: 总结门", "内化输出，形成可复用资产", 8),
        ("门5: 验证门", "5题抽查，80分通过", 4)
    ]
    
    total_time = 0
    for stage_name, description, duration in stages:
        click.echo(f"\n⏳ {stage_name}")
        click.echo(f"   {description}")
        click.echo(f"   预计耗时: {duration}分钟")
        total_time += duration
    
    click.echo(f"\n{'='*60}")
    click.echo(f"✅ 演示完成!")
    click.echo(f"   总预计耗时: {total_time}分钟")
    click.echo(f"   文件: {file_path}")


if __name__ == '__main__':
    cli()
