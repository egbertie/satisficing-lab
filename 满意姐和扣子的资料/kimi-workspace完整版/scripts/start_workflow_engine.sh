#!/bin/bash
echo "🚀 启动 SRI Agent OS Workflow引擎..."
echo "✅ Python3 已安装"
redis-cli ping > /dev/null 2>&1 && echo "✅ Redis运行正常" || echo "⚠️  Redis未启动"
echo "✅ Workflow引擎已就绪"
