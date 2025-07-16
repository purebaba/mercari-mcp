"""
Mercapi客户端包装器 - 使用mercapi库进行Mercari API调用
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from mercapi import Mercapi
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MercariItem(BaseModel):
    """Mercari商品数据模型"""
    id: str = Field(..., description="商品ID")
    name: str = Field(..., description="商品名称")
    price: int = Field(..., description="商品价格")
    status: str = Field(..., description="商品状态")
    thumbnail: str = Field(default="", description="商品缩略图URL")
    seller_name: str = Field(default="", description="卖家名称")
    seller_id: str = Field(default="", description="卖家ID")
    seller_rating: Optional[float] = Field(None, description="卖家评分")
    brand_name: Optional[str] = Field(None, description="品牌名称")
    category_name: Optional[str] = Field(None, description="分类名称")
    category_id: Optional[int] = Field(None, description="分类ID")
    description: Optional[str] = Field(None, description="商品描述")
    created_time: Optional[str] = Field(None, description="创建时间")
    updated_time: Optional[str] = Field(None, description="更新时间")
    url: Optional[str] = Field(None, description="商品链接")
    condition: Optional[str] = Field(None, description="商品状况")


class MercariSearchResult(BaseModel):
    """Mercari搜索结果模型"""
    total_count: int = Field(..., description="总结果数量")
    items: List[MercariItem] = Field(..., description="商品列表")
    has_next: bool = Field(..., description="是否有下一页")
    current_page: int = Field(..., description="当前页码")


class MercapiClient:
    """Mercapi客户端包装器"""
    
    def __init__(self):
        self.mercapi = Mercapi()
    
    async def _parse_search_result_item(self, item_data) -> MercariItem:
        """解析搜索结果中的商品数据"""
        try:
            # 获取缩略图URL
            thumbnail = ""
            if hasattr(item_data, 'thumbnails') and item_data.thumbnails:
                thumbnail = item_data.thumbnails[0]
            
            # 获取卖家信息
            seller_name = ""
            seller_rating = None
            seller_id = getattr(item_data, 'seller_id', '')
            
            # 对于SearchResultItem，seller是一个方法，需要调用
            if hasattr(item_data, 'seller'):
                try:
                    seller_obj = await item_data.seller()
                    if seller_obj:
                        seller_name = getattr(seller_obj, 'name', '')
                        # 计算评分
                        ratings = getattr(seller_obj, 'ratings', None)
                        if ratings:
                            good = getattr(ratings, 'good', 0)
                            normal = getattr(ratings, 'normal', 0)
                            bad = getattr(ratings, 'bad', 0)
                            total = good + normal + bad
                            if total > 0:
                                seller_rating = (good * 5 + normal * 3 + bad * 1) / total
                except Exception as e:
                    logger.warning(f"获取卖家信息失败: {e}")
            
            # 获取分类信息
            category_id = getattr(item_data, 'category_id', None)
            category_name = None  # SearchResultItem没有直接的分类名称
            
            # 获取状况信息
            condition_id = getattr(item_data, 'item_condition_id', None)
            condition = self._get_condition_text(condition_id)
            
            # 构建商品URL
            item_url = f"https://jp.mercari.com/item/{item_data.id_}"
            
            # 格式化时间
            created_time = str(item_data.created) if hasattr(item_data, 'created') else None
            updated_time = str(item_data.updated) if hasattr(item_data, 'updated') else None
            
            return MercariItem(
                id=item_data.id_,
                name=item_data.name,
                price=item_data.price,
                status=item_data.status,
                thumbnail=thumbnail,
                seller_name=seller_name,
                seller_id=seller_id,
                seller_rating=seller_rating,
                brand_name=None,  # SearchResultItem没有品牌信息
                category_name=category_name,
                category_id=category_id,
                description=None,  # SearchResultItem没有描述
                created_time=created_time,
                updated_time=updated_time,
                url=item_url,
                condition=condition
            )
        except Exception as e:
            logger.error(f"解析搜索结果商品数据失败: {e}")
            raise

    def _parse_item_data_to_dict(self, item_data) -> dict:
        """解析商品详情数据为字典（用于Item对象）"""
        try:
            # 获取缩略图URL
            thumbnail = ""
            if hasattr(item_data, 'thumbnails') and item_data.thumbnails:
                thumbnail = item_data.thumbnails[0]
            
            # 获取卖家信息
            seller_name = ""
            seller_rating = None
            seller_id = ""
            if hasattr(item_data, 'seller') and item_data.seller:
                seller_name = getattr(item_data.seller, 'name', '')
                seller_id = str(getattr(item_data.seller, 'id_', ''))
                # 计算卖家评分
                ratings = getattr(item_data.seller, 'ratings', None)
                if ratings:
                    good = getattr(ratings, 'good', 0)
                    normal = getattr(ratings, 'normal', 0)
                    bad = getattr(ratings, 'bad', 0)
                    total = good + normal + bad
                    if total > 0:
                        seller_rating = (good * 5 + normal * 3 + bad * 1) / total
                
            # 获取分类信息
            category_name = None
            category_id = None
            if hasattr(item_data, 'item_category') and item_data.item_category:
                category_name = getattr(item_data.item_category, 'name', None)
                category_id = getattr(item_data.item_category, 'id_', None)
            
            # 获取状况信息
            condition = None
            if hasattr(item_data, 'item_condition') and item_data.item_condition:
                condition = getattr(item_data.item_condition, 'name', None)
            
            # 获取品牌信息（如果有的话）
            brand_name = None
            if hasattr(item_data, 'brand') and item_data.brand:
                brand_name = getattr(item_data.brand, 'name', None)
            
            # 构建商品URL
            item_url = f"https://jp.mercari.com/item/{item_data.id_}"
            
            # 格式化时间
            created_time = str(item_data.created) if hasattr(item_data, 'created') else None
            updated_time = str(item_data.updated) if hasattr(item_data, 'updated') else None
            
            # 获取描述
            description = getattr(item_data, 'description', None)
            
            return {
                'id': item_data.id_,
                'name': item_data.name,
                'price': item_data.price,
                'status': item_data.status,
                'thumbnail': thumbnail,
                'seller_name': seller_name,
                'seller_id': seller_id,
                'seller_rating': seller_rating,
                'brand_name': brand_name,
                'category_name': category_name,
                'category_id': category_id,
                'description': description,
                'created_time': created_time,
                'updated_time': updated_time,
                'url': item_url,
                'condition': condition
            }
        except Exception as e:
            logger.error(f"解析商品数据失败: {e}")
            raise
    
    def _parse_item_data(self, item_data) -> MercariItem:
        """解析商品数据"""
        return MercariItem(**self._parse_item_data_to_dict(item_data))
    
    def _get_condition_text(self, condition_id: Optional[int]) -> Optional[str]:
        """根据条件ID获取条件文本"""
        if condition_id is None:
            return None
        
        condition_map = {
            1: "新品、未使用",
            2: "未使用に近い",
            3: "目立った傷や汚れなし",
            4: "やや傷や汚れあり",
            5: "傷や汚れあり",
            6: "全体的に状態が悪い"
        }
        return condition_map.get(condition_id, f"状態ID: {condition_id}")
    
    async def search_items(
        self,
        keyword: str,
        category_id: Optional[str] = None,
        brand_id: Optional[str] = None,
        price_min: Optional[int] = None,
        price_max: Optional[int] = None,
        condition: Optional[str] = None,
        sort: str = "created_time",
        order: str = "desc",
        page: int = 1,
        limit: int = 20
    ) -> MercariSearchResult:
        """搜索Mercari商品"""
        
        try:
            logger.info(f"搜索商品: keyword={keyword}, page={page}, limit={limit}")
            
            # 使用mercapi进行搜索
            search_result = await self.mercapi.search(keyword)
            
            # 解析响应数据
            items = []
            for item_data in search_result.items:
                try:
                    item = await self._parse_search_result_item(item_data)
                    items.append(item)
                except Exception as e:
                    logger.warning(f"解析商品数据失败: {e}, 跳过此商品")
                    continue
            
            # 应用过滤条件
            if price_min is not None:
                items = [item for item in items if item.price >= price_min]
            if price_max is not None:
                items = [item for item in items if item.price <= price_max]
            if category_id is not None:
                items = [item for item in items if item.category_id == int(category_id)]
            
            # 应用分页
            start_index = (page - 1) * limit
            end_index = start_index + limit
            paged_items = items[start_index:end_index]
            
            return MercariSearchResult(
                total_count=search_result.meta.num_found,
                items=paged_items,
                has_next=len(items) > end_index,
                current_page=page
            )
            
        except Exception as e:
            logger.error(f"搜索错误: {e}")
            raise Exception(f"搜索失败: {str(e)}")
    
    async def get_item_detail(self, item_id: str) -> MercariItem:
        """获取商品详情"""
        try:
            logger.info(f"获取商品详情: item_id={item_id}")
            
            # 使用mercapi获取商品详情
            item_data = await self.mercapi.item(item_id)
            
            if item_data is None:
                raise Exception(f"商品 {item_id} 不存在或无法访问")
            
            # 解析所有信息（包括详细描述）
            return self._parse_item_data(item_data)
            
        except Exception as e:
            logger.error(f"获取商品详情错误: {e}")
            raise Exception(f"获取商品详情失败: {str(e)}")
    
    def _format_price(self, price: int) -> str:
        """格式化价格"""
        return f"¥{price:,}"
    
    def _get_safe_attr(self, obj, attr: str, default: Any = None) -> Any:
        """安全获取对象属性"""
        try:
            return getattr(obj, attr, default)
        except:
            return default 