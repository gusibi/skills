#!/bin/bash
# 火山引擎 Ark Bot API (字节跳动) — 中文生活/实时信息
# Usage: ./ark_search.sh '{"query": "今天北京天气怎么样"}'

set -e

JSON_INPUT="$1"

if [ -z "$JSON_INPUT" ]; then
    echo "Usage: ./ark_search.sh '<json>'"
    echo ""
    echo "火山引擎 Ark Bot API (字节跳动)"
    echo "脚本: scripts/search.py"
    echo ""
    echo "Required:"
    echo "  query: string - 搜索关键词/问题"
    echo ""
    echo "Environment:"
    echo "  ARK_API_KEY - Required. 火山引擎 API Key"
    echo ""
    echo "Example:"
    echo "  ./ark_search.sh '{"query": "苹果公司股价"}'"
    exit 1
fi

if [ -z "$ARK_API_KEY" ]; then
    echo "Error: ARK_API_KEY environment variable is required"
    exit 1
fi

# Validate JSON
if ! echo "$JSON_INPUT" | jq empty 2>/dev/null; then
    echo "Error: Invalid JSON input"
    exit 1
fi

QUERY=$(echo "$JSON_INPUT" | jq -r '.query // empty')

if [ -z "$QUERY" ]; then
    echo "Error: 'query' field is required"
    exit 1
fi

# Get the directory of the current script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Call the python script and format output
# We use --no-stream to capture the output cleanly in the wrapper
echo "--- Summary ---"
python3 "$DIR/search.py" --no-stream "$QUERY"
