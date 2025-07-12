from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from app.core.database import get_database
from app.models.product import Product, ProductInDB, ProductResponse
from app.schemas.product import ProductCreate, ProductUpdate, ProductFilter
from app.services.user_service import user_service


class ProductService:
    def __init__(self):
        self.collection_name = "products"
    
    async def create_product(self, product_data: ProductCreate, seller_id: str) -> ProductInDB:
        """Create a new product"""
        db = await get_database()
        
        product_dict = product_data.dict()
        product_dict["seller_id"] = seller_id
        
        product = ProductInDB(**product_dict)
        result = await db[self.collection_name].insert_one(product.dict(by_alias=True))
        product.id = str(result.inserted_id)
        
        return product
    
    async def get_product_by_id(self, product_id: str) -> Optional[ProductResponse]:
        """Get product by ID with seller information"""
        db = await get_database()
        product_dict = await db[self.collection_name].find_one({"_id": ObjectId(product_id)})
        
        if product_dict:
            product_dict["_id"] = str(product_dict["_id"])
            product = ProductResponse(**product_dict)
            
            # Get seller info
            seller = await user_service.get_user_by_id(product.seller_id)
            if seller:
                product.seller_info = {
                    "id": seller.id,
                    "username": seller.username,
                    "full_name": seller.full_name,
                    "profile_image": seller.profile_image
                }
            
            return product
        return None
    
    async def get_products(
        self,
        filter_data: ProductFilter,
        skip: int = 0,
        limit: int = 10
    ) -> List[ProductResponse]:
        """Get products with filters"""
        db = await get_database()
        
        # Build filter query
        query = {"status": "active"}
        
        if filter_data.category:
            query["category"] = filter_data.category
        
        if filter_data.min_price is not None or filter_data.max_price is not None:
            price_filter = {}
            if filter_data.min_price is not None:
                price_filter["$gte"] = filter_data.min_price
            if filter_data.max_price is not None:
                price_filter["$lte"] = filter_data.max_price
            query["price"] = price_filter
        
        if filter_data.condition:
            query["condition"] = filter_data.condition
        
        if filter_data.location:
            query["location"] = {"$pattern": filter_data.location, "$options": "i"}
        
        if filter_data.search:
            query["$text"] = {"$search": filter_data.search}
        
        # Execute query
        cursor = db[self.collection_name].find(query).skip(skip).limit(limit).sort("created_at", -1)
        products = []
        
        async for product_dict in cursor:
            product_dict["_id"] = str(product_dict["_id"])
            product = ProductResponse(**product_dict)
            
            # Get seller info
            seller = await user_service.get_user_by_id(product.seller_id)
            if seller:
                product.seller_info = {
                    "id": seller.id,
                    "username": seller.username,
                    "full_name": seller.full_name,
                    "profile_image": seller.profile_image
                }
            
            products.append(product)
        
        return products
    
    async def get_user_products(self, user_id: str, skip: int = 0, limit: int = 10) -> List[ProductResponse]:
        """Get products by user"""
        db = await get_database()
        
        cursor = db[self.collection_name].find({"seller_id": user_id}).skip(skip).limit(limit).sort("created_at", -1)
        products = []
        
        async for product_dict in cursor:
            product_dict["_id"] = str(product_dict["_id"])
            product = ProductResponse(**product_dict)
            products.append(product)
        
        return products
    
    async def update_product(self, product_id: str, product_data: ProductUpdate, user_id: str) -> Optional[ProductResponse]:
        """Update product (only by owner)"""
        db = await get_database()
        
        # Check if user owns the product
        existing_product = await db[self.collection_name].find_one({
            "_id": ObjectId(product_id),
            "seller_id": user_id
        })
        
        if not existing_product:
            return None
        
        update_data = product_data.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            await db[self.collection_name].update_one(
                {"_id": ObjectId(product_id)},
                {"$set": update_data}
            )
        
        return await self.get_product_by_id(product_id)
    
    async def delete_product(self, product_id: str, user_id: str) -> bool:
        """Delete product (only by owner)"""
        db = await get_database()
        
        result = await db[self.collection_name].delete_one({
            "_id": ObjectId(product_id),
            "seller_id": user_id
        })
        
        return result.deleted_count > 0
    
    async def increment_views(self, product_id: str):
        """Increment product views"""
        db = await get_database()
        await db[self.collection_name].update_one(
            {"_id": ObjectId(product_id)},
            {"$inc": {"views": 1}}
        )


product_service = ProductService()