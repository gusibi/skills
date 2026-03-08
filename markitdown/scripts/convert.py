#!/usr/bin/env python3
"""
MarkItDown Conversion Script

This script uses the `markitdown` library to convert various document formats
(PDF, Word, Excel, PowerPoint, Images, Audio, HTML, CSV, JSON, XML, ZIP) into Markdown.

Usage:
  python3 scripts/convert.py <input_file> [--output <output_file>]

If --output is not specified, it prints the markdown content to stdout.
"""

import sys
import subprocess
import importlib.util

# MarkItDown officially requires Python 3.10+
if sys.version_info < (3, 10):
    print("Error: MarkItDown requires Python 3.10 or higher.", file=sys.stderr)
    print(f"Current version is {sys.version.split()[0]}", file=sys.stderr)
    sys.exit(1)

def ensure_markitdown():
    """Ensure markitdown is installed, if not, install it using the Tsinghua mirror."""
    if importlib.util.find_spec("markitdown") is None:
        print("Installing markitdown (using Tsinghua mirror)...", file=sys.stderr)
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "markitdown", 
                "-i", "https://pypi.tuna.tsinghua.edu.cn/simple", "-q"
            ])
        except subprocess.CalledProcessError as e:
            print(f"Error installing markitdown: {e}", file=sys.stderr)
            sys.exit(1)

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    input_file = sys.argv[1]
    output_file = None

    if len(sys.argv) >= 4 and sys.argv[2] == "--output":
        output_file = sys.argv[3]

    ensure_markitdown()
    
    try:
        from markitdown import MarkItDown
    except ImportError as e:
        print(f"Failed to import markitdown: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Converting {input_file}...", file=sys.stderr)
    try:
        md = MarkItDown()
        result = md.convert(input_file)
        
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result.text_content)
            print(f"Successfully saved to {output_file}", file=sys.stderr)
        else:
            print(result.text_content)
            
    except Exception as e:
        print(f"Error converting file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
