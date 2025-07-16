"""
Mercari MCP Server - 实现Mercari商品搜索的MCP智能体工具
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
)

from .mercapi_client import MercapiClient

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建MCP服务器实例
server = Server("mercari-mcp")
mercapi_client = MercapiClient()


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """列出可用的工具"""
    return [
        Tool(
            name="search_mercari_items",
            description="搜索Mercari商品",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "category_id": {
                        "type": "string",
                        "description": "分类ID（可选）"
                    },
                    "brand_id": {
                        "type": "string",
                        "description": "品牌ID（可选）"
                    },
                    "price_min": {
                        "type": "integer",
                        "description": "最低价格（可选）"
                    },
                    "price_max": {
                        "type": "integer",
                        "description": "最高价格（可选）"
                    },
                    "condition": {
                        "type": "string",
                        "description": "商品状态（可选）：new, like_new, good, fair, poor"
                    },
                    "sort": {
                        "type": "string",
                        "description": "排序方式（可选）：created_time, price, popular",
                        "default": "created_time"
                    },
                    "order": {
                        "type": "string",
                        "description": "排序顺序（可选）：asc, desc",
                        "default": "desc"
                    },
                    "page": {
                        "type": "integer",
                        "description": "页码（可选）",
                        "default": 1
                    },
                    "limit": {
                        "type": "integer",
                        "description": "每页数量（可选）",
                        "default": 20
                    }
                },
                "required": ["keyword"]
            }
        ),
        Tool(
            name="get_mercari_item_detail",
            description="获取Mercari商品详情",
            inputSchema={
                "type": "object",
                "properties": {
                    "item_id": {
                        "type": "string",
                        "description": "商品ID"
                    }
                },
                "required": ["item_id"]
            }
        ),
        Tool(
            name="search_mercari_by_category",
            description="按分类搜索Mercari商品",
            inputSchema={
                "type": "object",
                "properties": {
                    "category_name": {
                        "type": "string",
                        "description": "分类名称（如：电子产品、服装、书籍等）"
                    },
                    "price_min": {
                        "type": "integer",
                        "description": "最低价格（可选）"
                    },
                    "price_max": {
                        "type": "integer",
                        "description": "最高价格（可选）"
                    },
                    "condition": {
                        "type": "string",
                        "description": "商品状态（可选）：new, like_new, good, fair, poor"
                    },
                    "sort": {
                        "type": "string",
                        "description": "排序方式（可选）：created_time, price, popular",
                        "default": "created_time"
                    },
                    "page": {
                        "type": "integer",
                        "description": "页码（可选）",
                        "default": 1
                    },
                    "limit": {
                        "type": "integer",
                        "description": "每页数量（可选）",
                        "default": 20
                    }
                },
                "required": ["category_name"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理工具调用"""
    
    if name == "search_mercari_items":
        try:
            # 提取搜索参数
            keyword = arguments.get("keyword")
            category_id = arguments.get("category_id")
            brand_id = arguments.get("brand_id")
            price_min = arguments.get("price_min")
            price_max = arguments.get("price_max")
            condition = arguments.get("condition")
            sort = arguments.get("sort", "created_time")
            order = arguments.get("order", "desc")
            page = arguments.get("page", 1)
            limit = arguments.get("limit", 20)
            
            # 执行搜索
            search_result = await mercapi_client.search_items(
                keyword=keyword,
                category_id=category_id,
                brand_id=brand_id,
                price_min=price_min,
                price_max=price_max,
                condition=condition,
                sort=sort,
                order=order,
                page=page,
                limit=limit
            )
            
            # 格式化结果
            result_text = f"🔍 搜索结果（关键词：{keyword}）\n"
            result_text += f"📊 总共找到 {search_result.total_count} 个商品\n"
            result_text += f"📄 当前第 {search_result.current_page} 页\n"
            result_text += f"➡️ {'有' if search_result.has_next else '没有'}下一页\n\n"
            
            if not search_result.items:
                result_text += "❌ 没有找到匹配的商品\n"
            else:
                for i, item in enumerate(search_result.items, 1):
                    result_text += f"🛍️ 商品 {i}:\n"
                    result_text += f"   📝 ID: {item.id}\n"
                    result_text += f"   🏷️ 名称: {item.name}\n"
                    result_text += f"   💰 价格: ¥{item.price:,}\n"
                    result_text += f"   📦 状态: {item.status}\n"
                    result_text += f"   👤 卖家: {item.seller_name}\n"
                    if item.seller_rating:
                        result_text += f"   ⭐ 卖家评分: {item.seller_rating}\n"
                    if item.brand_name:
                        result_text += f"   🏢 品牌: {item.brand_name}\n"
                    if item.category_name:
                        result_text += f"   📂 分类: {item.category_name}\n"
                    if item.url:
                        result_text += f"   🔗 链接: {item.url}\n"
                    result_text += f"   🖼️ 缩略图: {item.thumbnail}\n"
                    result_text += f"   📅 创建时间: {item.created_time}\n"
                    result_text += "\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return [TextContent(type="text", text=f"❌ 搜索失败: {str(e)}")]
    
    elif name == "get_mercari_item_detail":
        try:
            item_id = arguments.get("item_id")
            
            # 获取商品详情
            item = await mercapi_client.get_item_detail(item_id)
            
            # 格式化结果
            result_text = f"📋 商品详情:\n"
            result_text += f"📝 ID: {item.id}\n"
            result_text += f"🏷️ 名称: {item.name}\n"
            result_text += f"💰 价格: ¥{item.price:,}\n"
            result_text += f"📦 状态: {item.status}\n"
            result_text += f"👤 卖家: {item.seller_name}\n"
            if item.seller_rating:
                result_text += f"⭐ 卖家评分: {item.seller_rating}\n"
            if item.brand_name:
                result_text += f"🏢 品牌: {item.brand_name}\n"
            if item.category_name:
                result_text += f"📂 分类: {item.category_name}\n"
            if item.url:
                result_text += f"🔗 链接: {item.url}\n"
            result_text += f"🖼️ 缩略图: {item.thumbnail}\n"
            result_text += f"📅 创建时间: {item.created_time}\n"
            result_text += f"🔄 更新时间: {item.updated_time}\n"
            if item.description:
                result_text += f"📝 描述: {item.description}\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"获取商品详情失败: {e}")
            return [TextContent(type="text", text=f"❌ 获取商品详情失败: {str(e)}")]
    
    elif name == "search_mercari_by_category":
        try:
            # 提取搜索参数
            category_name = arguments.get("category_name")
            price_min = arguments.get("price_min")
            price_max = arguments.get("price_max")
            condition = arguments.get("condition")
            sort = arguments.get("sort", "created_time")
            page = arguments.get("page", 1)
            limit = arguments.get("limit", 20)
            
            # 使用分类名称作为关键词进行搜索
            search_result = await mercapi_client.search_items(
                keyword=category_name,
                price_min=price_min,
                price_max=price_max,
                condition=condition,
                sort=sort,
                page=page,
                limit=limit
            )
            
            # 格式化结果
            result_text = f"🔍 分类搜索结果（分类：{category_name}）\n"
            result_text += f"📊 总共找到 {search_result.total_count} 个商品\n"
            result_text += f"📄 当前第 {search_result.current_page} 页\n"
            result_text += f"➡️ {'有' if search_result.has_next else '没有'}下一页\n\n"
            
            if not search_result.items:
                result_text += "❌ 没有找到匹配的商品\n"
            else:
                for i, item in enumerate(search_result.items, 1):
                    result_text += f"🛍️ 商品 {i}:\n"
                    result_text += f"   📝 ID: {item.id}\n"
                    result_text += f"   🏷️ 名称: {item.name}\n"
                    result_text += f"   💰 价格: ¥{item.price:,}\n"
                    result_text += f"   📦 状态: {item.status}\n"
                    result_text += f"   👤 卖家: {item.seller_name}\n"
                    if item.seller_rating:
                        result_text += f"   ⭐ 卖家评分: {item.seller_rating}\n"
                    if item.brand_name:
                        result_text += f"   🏢 品牌: {item.brand_name}\n"
                    if item.category_name:
                        result_text += f"   📂 分类: {item.category_name}\n"
                    if item.url:
                        result_text += f"   🔗 链接: {item.url}\n"
                    result_text += f"   📅 创建时间: {item.created_time}\n"
                    result_text += "\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"分类搜索失败: {e}")
            return [TextContent(type="text", text=f"❌ 分类搜索失败: {str(e)}")]
    
    else:
        return [TextContent(type="text", text=f"❌ 未知工具: {name}")]


async def main():
    """主函数"""
    # 运行服务器
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mercari-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main()) 