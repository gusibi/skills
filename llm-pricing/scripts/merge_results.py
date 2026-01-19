#!/usr/bin/env python3
"""
merge_results.py - 合并多个 LLM 定价 JSON 文件

功能：
- 读取 output/ 目录下所有 JSON 文件
- 合并为单一数组
- 基于 provider + model 去重
- 输出 all_models.json
"""

import json
import argparse
from pathlib import Path
from datetime import datetime


def merge_json_files(input_dir: str, output_file: str = None) -> list:
    """合并目录下所有 JSON 文件"""
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"❌ 目录不存在: {input_dir}")
        return []
    
    all_models = []
    seen = set()  # 用于去重: (provider, model)
    
    json_files = list(input_path.glob('*.json'))
    
    # 排除 all_models.json 本身
    json_files = [f for f in json_files if f.name != 'all_models.json']
    
    if not json_files:
        print(f"⚠️ 目录中没有 JSON 文件: {input_dir}")
        return []
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                data = [data]
            
            for entry in data:
                key = (entry.get('provider', ''), entry.get('model', ''))
                if key not in seen and key != ('', ''):
                    seen.add(key)
                    all_models.append(entry)
            
            print(f"  ✅ 已读取 {json_file.name}: {len(data)} 条记录")
            
        except json.JSONDecodeError as e:
            print(f"  ❌ JSON 解析错误 {json_file.name}: {e}")
        except Exception as e:
            print(f"  ❌ 读取错误 {json_file.name}: {e}")
    
    # 按 provider 和 model 排序
    all_models.sort(key=lambda x: (x.get('provider', ''), x.get('model', '')))
    
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_models, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 合并完成！共 {len(all_models)} 个模型，保存至 {output_file}")
    
    return all_models


def main():
    parser = argparse.ArgumentParser(description='合并多个 LLM 定价 JSON 文件')
    parser.add_argument('--input-dir', '-i', 
                        default='output',
                        help='输入目录（默认: output）')
    parser.add_argument('--output', '-o', 
                        default='output/all_models.json',
                        help='输出文件路径（默认: output/all_models.json）')
    
    args = parser.parse_args()
    
    print(f"📁 正在扫描目录: {args.input_dir}")
    merge_json_files(args.input_dir, args.output)


if __name__ == '__main__':
    main()
