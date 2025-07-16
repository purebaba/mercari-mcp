#!/usr/bin/env python3
"""
Mercari MCP SSE服务器启动脚本
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# 添加源码路径到Python路径
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from mercari_mcp.sse_server import main


def setup_logging(log_level: str = "INFO"):
    """设置日志"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr)
        ]
    )


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Mercari MCP SSE服务器")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="日志级别"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="服务器主机地址"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="服务器端口"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="Mercari MCP SSE Server 0.1.0"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    setup_logging(args.log_level)
    
    # 设置环境变量
    os.environ["MCP_HOST"] = args.host
    os.environ["MCP_PORT"] = str(args.port)
    
    try:
        # 运行SSE服务器
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 SSE服务器已停止", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"❌ SSE服务器启动失败: {e}", file=sys.stderr)
        sys.exit(1) 