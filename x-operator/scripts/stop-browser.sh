#!/bin/bash
#
# Stop the X.com Operator BrowserWing service
#

PORT=9222

PID=$(lsof -ti tcp:$PORT 2>/dev/null)

if [ -z "$PID" ]; then
  echo "ℹ️  No service running on port $PORT"
  exit 0
fi

echo "🛑 Stopping X.com Operator BrowserWing (PID: $PID)..."
kill $PID 2>/dev/null
sleep 2

# Check if still running
if lsof -ti tcp:$PORT > /dev/null 2>&1; then
  echo "⚠️  Graceful stop failed. Force killing..."
  kill -9 $PID 2>/dev/null
  sleep 1
fi

echo "✅ Service stopped."
