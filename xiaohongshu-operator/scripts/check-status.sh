#!/bin/bash
#
# Check the status of the Xiaohongshu Operator BrowserWing service
#

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

PORT=9222
HOST="127.0.0.1"

# Dynamically find existing browserwing port if any
EXISTING_PORT=$(lsof -i -P -n | grep LISTEN | grep browserwi | awk '{print $9}' | cut -d: -f2 | head -n 1)
if [ -n "$EXISTING_PORT" ]; then
  PORT=$EXISTING_PORT
fi

API="http://$HOST:$PORT/api/v1/executor"

echo "🔍 Checking Xiaohongshu Operator status..."

# Check if service is running
if ! curl -s "$API/help" > /dev/null 2>&1; then
  echo "❌ BrowserWing service is NOT running on port $PORT"
  echo "   Run: bash $SCRIPT_DIR/start-browser.sh"
  exit 1
fi

echo "✅ BrowserWing service is running on port $PORT"

# Check current page
PAGE_URL=$(curl -s "$API/page-info" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('url','unknown'))" 2>/dev/null || echo "unknown")
echo "📄 Current page: $PAGE_URL"

if echo "$PAGE_URL" | grep -q "login\|sign-in"; then
  echo "⚠️  Browser appears to be on a login page"
  echo "   Please open Brave manually and log in to xiaohongshu.com first"
else
  echo "✅ Browser is on a content page"
fi

echo ""
echo "📊 Service details:"
echo "   API endpoint: $API"
echo "   Config: ~/.xiaohongshu-operator/config.toml"
echo "   Logs:   ~/.xiaohongshu-operator/log/"
