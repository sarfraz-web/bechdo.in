from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from app.core.database import get_database
from app.models.order import Order, OrderInDB, OrderResponse
from app.schemas.order import OrderCreate, OrderUpdate, OrderFilter
from app.services.user_service import user_service
from app.services.product_service import product_service


class OrderService:
    def __init__(self):
        self.collection_name = "orders"
    
    async def create_order(self, order_data: OrderCreate, buyer_id: str) -> OrderInDB:
        """Create a new order"""
        db = await get_database()
        
        # Get product to validate and get seller info
        product = await product_service.get_product_by_id(order_data.product_id)
        if not product:
            raise ValueError("Product not found")
        
        if product.seller_id == buyer_id:
            raise ValueError("Cannot buy your own product")
        
        if product.status != "active":
            raise ValueError("Product is not available for purchase")
        
        # Calculate total price
        total_price = product.price * order_data.quantity
        
        # Create order
        order_dict = order_data.dict()
        order_dict["buyer_id"] = buyer_id
        order_dict["seller_id"] = product.seller_id
        order_dict["total_price"] = total_price
        
        order = OrderInDB(**order_dict)
        result = await db[self.collection_name].insert_one(order.dict(by_alias=True))
        order.id = str(result.inserted_id)
        
        return order
    
    async def get_order_by_id(self, order_id: str) -> Optional[OrderResponse]:
        """Get order by ID with populated information"""
        db = await get_database()
        order_dict = await db[self.collection_name].find_one({"_id": ObjectId(order_id)})
        
        if order_dict:
            order_dict["_id"] = str(order_dict["_id"])
            order = OrderResponse(**order_dict)
            
            # Populate related information
            await self._populate_order_info(order)
            
            return order
        return None
    
    async def get_user_orders(
        self,
        user_id: str,
        filter_data: OrderFilter,
        skip: int = 0,
        limit: int = 10,
        as_buyer: bool = True
    ) -> List[OrderResponse]:
        """Get orders for a user (as buyer or seller)"""
        db = await get_database()
        
        # Build filter query
        query = {"buyer_id" if as_buyer else "seller_id": user_id}
        
        if filter_data.status:
            query["status"] = filter_data.status
        
        if filter_data.payment_status:
            query["payment_status"] = filter_data.payment_status
        
        # Execute query
        cursor = db[self.collection_name].find(query).skip(skip).limit(limit).sort("created_at", -1)
        orders = []
        
        async for order_dict in cursor:
            order_dict["_id"] = str(order_dict["_id"])
            order = OrderResponse(**order_dict)
            
            # Populate related information
            await self._populate_order_info(order)
            
            orders.append(order)
        
        return orders
    
    async def update_order(self, order_id: str, order_data: OrderUpdate, user_id: str) -> Optional[OrderResponse]:
        """Update order (only by seller)"""
        db = await get_database()
        
        # Check if user is the seller
        existing_order = await db[self.collection_name].find_one({
            "_id": ObjectId(order_id),
            "seller_id": user_id
        })
        
        if not existing_order:
            return None
        
        update_data = order_data.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            await db[self.collection_name].update_one(
                {"_id": ObjectId(order_id)},
                {"$set": update_data}
            )
        
        return await self.get_order_by_id(order_id)
    
    async def _populate_order_info(self, order: OrderResponse):
        """Populate order with related information"""
        # Get product info
        product = await product_service.get_product_by_id(order.product_id)
        if product:
            order.product_info = {
                "id": product.id,
                "title": product.title,
                "price": product.price,
                "images": product.images
            }
        
        # Get buyer info
        buyer = await user_service.get_user_by_id(order.buyer_id)
        if buyer:
            order.buyer_info = {
                "id": buyer.id,
                "username": buyer.username,
                "full_name": buyer.full_name,
                "profile_image": buyer.profile_image
            }
        
        # Get seller info
        seller = await user_service.get_user_by_id(order.seller_id)
        if seller:
            order.seller_info = {
                "id": seller.id,
                "username": seller.username,
                "full_name": seller.full_name,
                "profile_image": seller.profile_image
            }


order_service = OrderService()
