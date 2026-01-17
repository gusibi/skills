#!/usr/bin/env python3
"""
图片上传脚本 - 通过本地代理上传图片到 R2

用法：
    python upload_image.py /path/to/image.png [--port 38123]
    
返回：
    成功时输出上传后的 URL
    失败时返回非零退出码
"""

import argparse
import json
import sys

import requests


def upload_image(file_path: str, port: int = 38123) -> str:
    """
    上传图片到 R2
    
    Args:
        file_path: 图片文件路径
        port: 本地代理服务端口
        
    Returns:
        上传后的图片 URL
    """
    url = f"http://127.0.0.1:{port}/upload"
    
    try:
        with open(file_path, "rb") as f:
            filename = file_path.split("/")[-1]
            files = {"file": (filename, f)}
            
            print(f"正在上传: {filename}")
            resp = requests.post(url, files=files, timeout=60)
            
        if resp.status_code == 200:
            # 尝试解析 JSON 响应获取 URL
            try:
                data = resp.json()
                if isinstance(data, dict):
                    # 尝试不同的可能的 URL 字段名
                    image_url = data.get("url") or data.get("URL") or data.get("image_url") or data.get("link")
                    if image_url:
                        print(f"上传成功!")
                        print(f"URL: {image_url}")
                        return image_url
            except json.JSONDecodeError:
                pass
            
            # 如果无法解析 JSON，直接输出响应文本
            print(f"上传成功!")
            print(f"响应: {resp.text}")
            return resp.text.strip()
        else:
            print(f"上传失败，状态码: {resp.status_code}", file=sys.stderr)
            print(f"响应: {resp.text}", file=sys.stderr)
            sys.exit(1)
            
    except requests.exceptions.ConnectionError:
        print(f"错误: 无法连接到代理服务 (端口 {port})", file=sys.stderr)
        print("请确保代理服务正在运行", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"错误: 文件不存在: {file_path}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("错误: 上传超时", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="通过本地代理上传图片到 R2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python upload_image.py cover.png
    python upload_image.py /path/to/image.jpg --port 8080
        """
    )
    
    parser.add_argument(
        "file",
        help="要上传的图片文件路径"
    )
    
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=38123,
        help="代理服务端口（默认: 38123）"
    )
    
    args = parser.parse_args()
    
    upload_image(args.file, args.port)


if __name__ == "__main__":
    main()