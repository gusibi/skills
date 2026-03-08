#!/bin/bash
#
# Stop the Xiaohongshu Operator BrowserWing service
#

PORT=9222

# Find existing browserwing port
EXISTING_PORT=$(lsof -i -P -n | grep LISTEN | grep browserwi | awk '{print $9}' | cut -d: -f2 | head -n 1)
if [ -n "$EXISTING_PORT" ]; then
  PORT=$EXISTING_PORT
fi

PID=$(lsof -ti tcp:$PORT 2>/dev/null)

if [ -z "$PID" ]; then
  echo "ℹ️  No service running on port $PORT"
  exit 0
fi

echo "🛑 Stopping Xiaohongshu Operator BrowserWing (PID: $PID)..."
kill $PID 2>/dev/null
sleep 2

# Check if still running
if lsof -ti tcp:$PORT > /dev/null 2>&1; then
  echo "⚠️  Graceful stop failed. Force killing..."
  kill -9 $PID 2>/dev/null
  sleep 1
fi

echo "✅ Service stopped."
