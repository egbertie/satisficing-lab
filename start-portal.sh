#!/bin/bash
# ============================================================
# 自建本地门户服务 · 管理脚本
# ============================================================

WORKSPACE="/Users/egbertielau/.openclaw/workspace"
PID_FILE="$WORKSPACE/.portal-pid"
LOG_FILE="$WORKSPACE/.portal.log"

case "$1" in
  start)
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
      echo "⚠️  已在运行 (PID $(cat $PID_FILE))"
      echo "   地址: http://localhost:8765"
      exit 0
    fi
    echo "🏠 启动门户服务..."
    cd "$WORKSPACE"
    nohup python3 portal-server.py >> "$LOG_FILE" 2>&1 &
    PID=$!
    echo $PID > "$PID_FILE"
    sleep 1
    if kill -0 $PID 2>/dev/null; then
      echo "✅ 已启动 (PID $PID)"
      echo "   📍 http://localhost:8765"
    else
      echo "❌ 启动失败，查看日志: $LOG_FILE"
    fi
    ;;

  stop)
    if [ -f "$PID_FILE" ]; then
      PID=$(cat "$PID_FILE")
      if kill "$PID" 2>/dev/null; then
        echo "🛑 已停止 (PID $PID)"
      fi
      rm -f "$PID_FILE"
    else
      echo "未在运行"
    fi
    ;;

  restart)
    $0 stop
    sleep 1
    $0 start
    ;;

  status)
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
      PID=$(cat "$PID_FILE")
      echo "✅ 运行中"
      echo "   PID: $PID"
      echo "   地址: http://localhost:8765"
      echo "   日志: $LOG_FILE"
    else
      echo "❌ 未运行"
      rm -f "$PID_FILE"
    fi
    ;;

  *)
    echo "用法: $0 {start|stop|restart|status}"
    exit 1
    ;;
esac
