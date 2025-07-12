from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.product import ProductStatus, ProductCondition


class ProductCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    price: float = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=50)
    condition: ProductCondition = ProductCondition.GOOD
    images: List[str] = Field(default=[])
    location: Optional[str] = None
    tags: List[str] = Field(default=[])


class ProductUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    condition: Optional[ProductCondition] = None
    images: Optional[List[str]] = None
    location: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[ProductStatus] = None


class ProductFilter(BaseModel):
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    condition: Optional[ProductCondition] = None
    location: Optional[str] = None
    search: Optional[str] = None
