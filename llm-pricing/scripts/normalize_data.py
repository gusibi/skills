#!/usr/bin/env python3
"""
normalize_data.py - 规范化 LLM 定价数据

功能：
- 模型名转小写，空格/下划线转 -
- 价格单位统一转换为"每百万 token"
- 过滤无效数据行
"""

import json
import argparse
import re
from pathlib import Path
from typing import Optional


def normalize_model_name(name: str) -> str:
    """规范化模型名称：小写，空格/下划线转 -"""
    if not name:
        return ""
    # 转小写
    name = name.lower()
    # 替换空格和下划线为 -
    name = re.sub(r'[\s_]+', '-', name)
    # 移除多余的 -
    name = re.sub(r'-+', '-', name)
    # 移除首尾的 -
    name = name.strip('-')
    return name


def convert_price_to_per_million(price: float, unit: str) -> float:
    """将价格转换为每百万 token"""
    if price is None or price == 0:
        return 0.0
    
    unit_lower = unit.lower() if unit else ""
    
    # 每千 token -> 每百万 token (x1000)
    if 'k' in unit_lower or '千' in unit_lower or '1000' in unit_lower:
        return price * 1000
    # 每万 token -> 每百万 token (x100)
    elif '万' in unit_lower or '10000' in unit_lower or '10k' in unit_lower:
        return price * 100
    # 已经是每百万 token
    elif 'm' in unit_lower or '百万' in unit_lower or '1000000' in unit_lower:
        return price
    # 默认假设是每千 token
    else:
        return price * 1000


def normalize_entry(entry: dict) -> Optional[dict]:
    """规范化单条数据"""
    # 过滤无效条目
    if not entry.get('model'):
        return None
    
    # 模型名不应该是纯数字或价格
    model = str(entry.get('model', ''))
    if re.match(r'^[\d.,¥$€]+$', model):
        return None
    
    raw_unit = entry.get('raw_unit', 'per 1K tokens')
    
    normalized = {
        'provider': normalize_model_name(entry.get('provider', '')),
        'model': normalize_model_name(entry.get('model', '')),
        'input_price_per_million': convert_price_to_per_million(
            entry.get('input_price_per_million', 0) or entry.get('input_price', 0),
            raw_unit
        ),
        'output_price_per_million': convert_price_to_per_million(
            entry.get('output_price_per_million', 0) or entry.get('output_price', 0),
            raw_unit
        ),
        'currency': entry.get('currency', 'CNY'),
        'source_url': entry.get('source_url', ''),
        'retrieved_at': entry.get('retrieved_at', ''),
        'raw_unit': raw_unit,
        'raw_text': entry.get('raw_text', ''),
    }
    
    # 可选字段
    if entry.get('cache_price_per_million') or entry.get('cache_price'):
        normalized['cache_price_per_million'] = convert_price_to_per_million(
            entry.get('cache_price_per_million', 0) or entry.get('cache_price', 0),
            raw_unit
        )
    
    if entry.get('context_length'):
        normalized['context_length'] = entry.get('context_length')
    
    if entry.get('tags'):
        normalized['tags'] = entry.get('tags')
    
    return normalized


def normalize_data(input_path: str, output_path: str = None) -> list:
    """规范化整个数据文件"""
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        data = [data]
    
    normalized = []
    for entry in data:
        result = normalize_entry(entry)
        if result:
            normalized.append(result)
    
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(normalized, f, ensure_ascii=False, indent=2)
        print(f"✅ 已规范化 {len(normalized)} 条数据，保存至 {output_path}")
    
    return normalized


def main():
    parser = argparse.ArgumentParser(description='规范化 LLM 定价数据')
    parser.add_argument('input', help='输入 JSON 文件路径')
    parser.add_argument('--output', '-o', help='输出 JSON 文件路径（默认覆盖原文件）')
    
    args = parser.parse_args()
    
    output_path = args.output or args.input
    normalize_data(args.input, output_path)


if __name__ == '__main__':
    main()
