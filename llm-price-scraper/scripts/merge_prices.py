#!/usr/bin/env python3

import os
import json
import csv
import re
import argparse
import sys
from datetime import datetime

def to_model_id(model):
    if not model:
        return ""
    # Convert to lowercase
    s = model.lower()
    # Replace spaces, underscores, slashes with hyphens
    s = re.sub(r'[\s_/]+', '-', s)
    # Remove characters that are not a-z, 0-9, dot, or hyphen
    s = re.sub(r'[^a-z0-9.-]', '', s)
    # Collapse multiple hyphens
    s = re.sub(r'-+', '-', s)
    # Trim hyphens from start and end
    s = s.strip('-')
    return s

def infer_pricing_type(m):
    if m.get('pricing_type'):
        return m['pricing_type']
    
    input_price = m.get('input_price')
    output_price = m.get('output_price')
    
    if input_price == 0 and output_price == 0:
        return 'free'
    if input_price is not None or output_price is not None:
        return 'token'
    
    price = m.get('price')
    if price is not None:
        unit = m.get('price_unit')
        return f"per_{unit}" if unit else 'other'
    
    return 'unknown'

def flatten_provider_data(data):
    rows = []
    provider = data.get('provider')
    url = data.get('url')
    currency = data.get('currency')
    retrieved_at = data.get('retrieved_at')
    models = data.get('models', [])
    
    if isinstance(models, list):
        for m in models:
            pricing_type = infer_pricing_type(m)
            
            rows.append({
                'provider': provider,
                'model_id': to_model_id(m.get('model', '')),
                'model': m.get('model'),
                'pricing_type': pricing_type,
                # Token pricing fields
                'input_price': m.get('input_price'),
                'output_price': m.get('output_price'),
                'cache_price': m.get('cache_price'),
                # Non-token pricing fields
                'price': m.get('price'),
                'price_unit': m.get('price_unit'),
                # Common fields
                'context_length': m.get('context_length'),
                'currency': currency,
                'source_url': url,
                'retrieved_at': retrieved_at,
            })
    return rows

def main():
    parser = argparse.ArgumentParser(description='Merge LLM pricing files.')
    parser.add_argument('--in-dir', default='prices', help='Input directory containing JSON files')
    parser.add_argument('--out', default='prices.json', help='Output JSON path')
    parser.add_argument('--csv', default='prices.csv', help='Output CSV path')
    
    args = parser.parse_args()
    
    in_dir = args.in_dir
    out_path = args.out
    csv_path = args.csv
    
    if not os.path.exists(in_dir):
        print(f"Missing input directory: {in_dir}", file=sys.stderr)
        sys.exit(1)
        
    entries = [f for f in os.listdir(in_dir) if f.endswith('.json')]
    if not entries:
        print(f"No JSON files found in {in_dir}", file=sys.stderr)
        sys.exit(1)
        
    all_rows = []
    for name in sorted(entries):
        with open(os.path.join(in_dir, name), 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                
                # Handle new nested format with provider.models array
                if isinstance(data, dict) and 'models' in data and isinstance(data['models'], list):
                    all_rows.extend(flatten_provider_data(data))
                # Handle legacy flat array format
                elif isinstance(data, list):
                    all_rows.extend(data)
            except json.JSONDecodeError as e:
                print(f"Error parsing {name}: {e}", file=sys.stderr)

    # Save JSON
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(all_rows, f, indent=2, ensure_ascii=False)
        
    # Save CSV
    if csv_path:
        header = [
            'provider', 'model_id', 'model', 'pricing_type',
            'input_price', 'output_price', 'cache_price',
            'price', 'price_unit', 'context_length',
            'currency', 'source_url', 'retrieved_at'
        ]
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            for row in all_rows:
                # Filter row to only include header keys
                filtered_row = {k: row.get(k) for k in header}
                writer.writerow(filtered_row)

    # Summary by pricing type
    by_type = {}
    for r in all_rows:
        pt = r.get('pricing_type', 'unknown')
        by_type[pt] = by_type.get(pt, 0) + 1
        
    type_summary = ", ".join([f"{k}({v})" for k, v in by_type.items()])
    
    print(f"Merged {len(all_rows)} records from {len(entries)} files into {out_path}")
    print(f"  By pricing type: {type_summary}")
    if csv_path:
        print(f"Saved CSV to {csv_path}")

if __name__ == '__main__':
    main()
