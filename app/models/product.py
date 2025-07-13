from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum


class ProductStatus(str, Enum):
    ACTIVE = "active"
    SOLD = "sold"
    DRAFT = "draft"
    INACTIVE = "inactive"


class ProductCondition(str, Enum):
    NEW = "new"
    LIKE_NEW = "like_new"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class Product(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    price: float = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=50)
    condition: ProductCondition = ProductCondition.GOOD
    images: List[str] = Field(default=[])
    seller_id: str = Field(...)
    seller_info: Optional[dict] = None  # Will be populated when fetching
    status: ProductStatus = ProductStatus.ACTIVE
    location: Optional[str] = None
    tags: List[str] = Field(default=[])
    views: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        use_enum_values = True


class ProductInDB(Product):
    """Product model for database operations"""
    pass


class ProductResponse(Product):
    """Product response with seller information"""
    seller_info: Optional[dict] = None
