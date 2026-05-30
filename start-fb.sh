#!/bin/bash
# 文件浏览器服务管理脚本
# 用法:
#   ./start-fb.sh           启动文件浏览器 (后台)
#   ./start-fb.sh stop      停止文件浏览器
#   ./start-fb.sh status    检查状态
#   ./start-fb.sh restart   重启

PORT=8765
ROOT="$(cd "$(dirname "$0")" && pwd)"
PIDFILE="$ROOT/.fb-pid"
LOGFILE="$ROOT/.fb-log"

case "${1:-start}" in
  stop)
    if [ -f "$PIDFILE" ]; then
      PID=$(cat "$PIDFILE")
      if kill -0 "$PID" 2>/dev/null; then
        echo "Stopping file browser (PID: $PID)..."
        kill "$PID"
        rm -f "$PIDFILE"
        echo "Stopped"
      else
        echo "Process $PID not running, removing stale PID file"
        rm -f "$PIDFILE"
      fi
    else
      echo "No PID file found"
      # 尝试按端口查杀
      PID=$(lsof -ti :$PORT 2>/dev/null)
      if [ -n "$PID" ]; then
        echo "Found process on port $PORT (PID: $PID), killing..."
        kill "$PID"
        echo "Killed"
      fi
    fi
    ;;

  status)
    if [ -f "$PIDFILE" ]; then
      PID=$(cat "$PIDFILE")
      if kill -0 "$PID" 2>/dev/null; then
        echo "File browser is RUNNING (PID: $PID) on port $PORT"
        echo "URL: http://localhost:$PORT"
        exit 0
      else
        echo "PID file exists but process is dead"
        rm -f "$PIDFILE"
      fi
    fi
    PID=$(lsof -ti :$PORT 2>/dev/null)
    if [ -n "$PID" ]; then
      echo "File browser is RUNNING (PID: $PID) on port $PORT (no PID file)"
      echo "URL: http://localhost:$PORT"
    else
      echo "File browser is NOT running"
    fi
    ;;

  restart)
    "$0" stop
    sleep 1
    "$0" start
    ;;

  start|*)
    # 检查是否已经在运行
    if [ -f "$PIDFILE" ]; then
      PID=$(cat "$PIDFILE")
      if kill -0 "$PID" 2>/dev/null; then
        echo "File browser already running (PID: $PID)"
        echo "URL: http://localhost:$PORT"
        exit 0
      fi
    fi
    PID=$(lsof -ti :$PORT 2>/dev/null)
    if [ -n "$PID" ]; then
      echo "File browser already running on port $PORT (PID: $PID)"
      echo "URL: http://localhost:$PORT"
      exit 0
    fi

    echo "Starting file browser..."
    echo "Root: $ROOT"
    echo "Port: $PORT"
    nohup python3 "$ROOT/file-browser.py" >> "$LOGFILE" 2>&1 &
    PID=$!
    echo "$PID" > "$PIDFILE"
    sleep 1
    if kill -0 "$PID" 2>/dev/null; then
      echo "Started! (PID: $PID)"
      echo "URL: http://localhost:$PORT"
      # 局域网 IP
      LAN_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)
      if [ -n "$LAN_IP" ]; then
        echo "LAN:  http://$LAN_IP:$PORT"
      fi
    else
      echo "Failed to start (check $LOGFILE)"
      rm -f "$PIDFILE"
      exit 1
    fi
    ;;
esac
