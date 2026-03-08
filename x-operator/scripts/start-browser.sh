#!/bin/bash
#
# X.com Operator — Start BrowserWing Service
#
# Starts a BrowserWing Executor instance using a dedicated browser (default: Brave).
# The browser uses its own default profile, so login sessions persist naturally.
#
# Usage:
#   bash <skill-dir>/scripts/start-browser.sh              # use default browser (Brave)
#   bash <skill-dir>/scripts/start-browser.sh --browser chrome  # use specific browser
#   bash <skill-dir>/scripts/start-browser.sh --list        # list available browsers
#

set -e

# Resolve directory paths (relative to this script)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Configuration
XCOM_DIR="$HOME/.x-com-operator"
CONFIG_FILE="$XCOM_DIR/config.toml"
LOG_DIR="$XCOM_DIR/log"
DATA_DIR="$XCOM_DIR/data"
PORT=9222
HOST="127.0.0.1"

# ─── Browser Detection ───────────────────────────────────────────────────────

get_browser_path() {
  case "$1" in
    "brave")    echo "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" ;;
    "chromium") echo "/Applications/Chromium.app/Contents/MacOS/Chromium" ;;
    "chrome")   echo "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ;;
    "arc")      echo "/Applications/Arc.app/Contents/MacOS/Arc" ;;
    "edge")     echo "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" ;;
    "vivaldi")  echo "/Applications/Vivaldi.app/Contents/MacOS/Vivaldi" ;;
    "opera")    echo "/Applications/Opera.app/Contents/MacOS/Opera" ;;
    *)          echo "" ;;
  esac
}

# Get browser's REAL default profile directory on macOS
get_browser_profile_dir() {
  local support="$HOME/Library/Application Support"
  case "$1" in
    "brave")    echo "$support/BraveSoftware/Brave-Browser" ;;
    "chromium") echo "$support/Chromium" ;;
    "chrome")   echo "$support/Google/Chrome" ;;
    "arc")      echo "$support/Arc/User Data" ;;
    "edge")     echo "$support/Microsoft Edge" ;;
    "vivaldi")  echo "$support/Vivaldi" ;;
    "opera")    echo "$support/com.operasoftware.Opera" ;;
    *)          echo "" ;;
  esac
}


# Default priority: Brave first (dedicated browser for this skill)
BROWSER_PRIORITY=("brave" "chromium" "chrome" "arc" "edge" "vivaldi" "opera")

detect_browsers() {
  local found=""
  for name in "${BROWSER_PRIORITY[@]}"; do
    local path
    path=$(get_browser_path "$name")
    if [ -f "$path" ]; then
      found="$found $name"
    fi
  done
  echo "$found"
}

list_browsers() {
  echo "🔍 Detecting available Chromium-based browsers..."
  echo ""
  local any_found=false
  for name in "${BROWSER_PRIORITY[@]}"; do
    local path
    path=$(get_browser_path "$name")
    if [ -f "$path" ]; then
      echo "  ✅  $name  →  $path"
      any_found=true
    else
      echo "  ❌  $name  →  (not installed)"
    fi
  done
  echo ""
  if [ "$any_found" = true ]; then
    echo "Usage: bash $0 --browser <name>"
    echo "Default: first available in order [${BROWSER_PRIORITY[*]}]"
  else
    echo "⚠️  No supported Chromium-based browser found."
  fi
}

select_browser() {
  local requested="$1"

  if [ -n "$requested" ]; then
    requested=$(echo "$requested" | tr '[:upper:]' '[:lower:]')
    local path
    path=$(get_browser_path "$requested")
    if [ -z "$path" ]; then
      echo "❌ Unknown browser: $requested"
      echo "   Supported: ${BROWSER_PRIORITY[*]}"
      exit 1
    fi
    if [ ! -f "$path" ]; then
      echo "❌ $requested is not installed at: $path"
      exit 1
    fi
    BROWSER_NAME="$requested"
    BROWSER_PATH="$path"
    BROWSER_PROFILE_DIR=$(get_browser_profile_dir "$requested")
    return
  fi

  # Auto-detect: pick first available
  local available
  available=$(detect_browsers)
  if [ -z "$available" ]; then
    echo "❌ No supported Chromium-based browser found."
    echo "   Run with --list to see details."
    exit 1
  fi

  local first
  first=$(echo "$available" | awk '{print $1}')
  BROWSER_NAME="$first"
  BROWSER_PATH=$(get_browser_path "$first")
  BROWSER_PROFILE_DIR=$(get_browser_profile_dir "$first")
}

# ─── Parse Arguments ─────────────────────────────────────────────────────────

REQUESTED_BROWSER=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --list|-l)
      list_browsers
      exit 0
      ;;
    --browser|-b)
      REQUESTED_BROWSER="$2"
      shift 2
      ;;
    --port|-p)
      PORT="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--list] [--browser <name>] [--port <port>]"
      exit 1
      ;;
  esac
done

# ─── Main ────────────────────────────────────────────────────────────────────

select_browser "$REQUESTED_BROWSER"

# Create directories if needed
mkdir -p "$LOG_DIR" "$DATA_DIR"

# Create config (NO user_data_dir — use browser's default profile)
cat > "$CONFIG_FILE" << EOF
debug = false
llms = []
assets_dir = '$DATA_DIR'

[server]
port = '$PORT'
host = '$HOST'
mcp_host = ''
mcp_port = ''

[database]
path = '$DATA_DIR/browserwing.db'

[browser]
bin_path = '$BROWSER_PATH'
user_data_dir = '$BROWSER_PROFILE_DIR'
flags = [
  '--disable-blink-features=AutomationControlled',
  '--disable-infobars',
  '--no-sandbox',
  '--disable-setuid-sandbox',
  '--ignore-certificate-errors',
  '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
  '--lang=en-US,en;q=0.9'
]

[log]
level = 'info'
file = '$LOG_DIR/browserwing.log'

[auth]
enabled = false
app_key = 'default-secret-key-change-in-production'
default_username = 'admin'
default_password = 'admin123'
EOF

# Check if already running
if curl -s "http://$HOST:$PORT/api/v1/executor/help" > /dev/null 2>&1; then
  echo "✅ X.com Operator BrowserWing service is already running on port $PORT"
  exit 0
fi

# Check if browserwing is installed
if ! command -v browserwing &> /dev/null; then
  echo "📦 BrowserWing not found. Installing..."
  npm install -g browserwing
fi

# Start BrowserWing
echo "🚀 Starting X.com Operator BrowserWing on port $PORT..."
echo "   Browser: $BROWSER_NAME → $BROWSER_PATH"
echo "   Profile: $BROWSER_PROFILE_DIR"
echo "   Config:  $CONFIG_FILE"

cd "$XCOM_DIR"
nohup browserwing -host "$HOST" -port "$PORT" > "$LOG_DIR/startup.log" 2>&1 &
BW_PID=$!

# Wait for service to start
echo "⏳ Waiting for service to start..."
for i in {1..10}; do
  sleep 1
  if curl -s "http://$HOST:$PORT/api/v1/executor/help" > /dev/null 2>&1; then
    echo "✅ Service started successfully (PID: $BW_PID)"
    echo ""
    echo "📌 Make sure you've logged in to x.com in $BROWSER_NAME beforehand."
    echo ""
    echo "🔗 API endpoint: http://$HOST:$PORT/api/v1/executor"
    exit 0
  fi
done

echo "❌ Service failed to start within 10 seconds."
echo "Check logs at: $LOG_DIR/startup.log"
cat "$LOG_DIR/startup.log" 2>/dev/null
exit 1
