#!/usr/bin/env python3
"""
Daily Life Search - Call Ark Bot API for daily information queries.

Usage:
    python3 search.py "今天北京天气怎么样"
    python3 search.py "今日国际新闻热点"
    python3 search.py "苹果公司股价"
    python3 search.py --no-stream "今天限行尾号"

Requires:
    - ARK_API_KEY environment variable
    - requests library (pip install requests)
"""

import argparse
import json
import os
import sys

import requests

API_URL = "https://ark.cn-beijing.volces.com/api/v3/bots/chat/completions"
MODEL = "bot-20260310183451-lpk6v"


def search(query: str, system_prompt: str = "You are a helpful assistant.", stream: bool = True) -> str:
    api_key = os.environ.get("ARK_API_KEY")
    if not api_key:
        print("Error: ARK_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "stream": stream,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
    }

    if stream:
        payload["stream_options"] = {"include_usage": True}

    response = requests.post(API_URL, headers=headers, json=payload, stream=stream, timeout=60)
    response.raise_for_status()

    if not stream:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        print(content)
        return content

    full_content = []
    for line in response.iter_lines():
        if not line:
            continue
        decoded = line.decode("utf-8")
        if not decoded.startswith("data: "):
            continue
        data_str = decoded[6:]
        if data_str.strip() == "[DONE]":
            break
        try:
            chunk = json.loads(data_str)
            delta = chunk.get("choices", [{}])[0].get("delta", {})
            text = delta.get("content", "")
            if text:
                print(text, end="", flush=True)
                full_content.append(text)
        except json.JSONDecodeError:
            continue

    print()
    return "".join(full_content)


def main():
    parser = argparse.ArgumentParser(description="Daily life search via Ark Bot API")
    parser.add_argument("query", help="Search query in natural language")
    parser.add_argument("--system", default="You are a helpful assistant.", help="System prompt")
    parser.add_argument("--no-stream", action="store_true", help="Disable streaming output")
    args = parser.parse_args()

    search(args.query, system_prompt=args.system, stream=not args.no_stream)


if __name__ == "__main__":
    main()
