from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Order(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    product_id: str = Field(...)
    buyer_id: str = Field(...)
    seller_id: str = Field(...)
    quantity: int = Field(..., ge=1)
    total_price: float = Field(..., gt=0)
    status: OrderStatus = OrderStatus.PENDING
    payment_status: PaymentStatus = PaymentStatus.PENDING
    shipping_address: str = Field(...)
    buyer_notes: Optional[str] = None
    seller_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Populated fields
    product_info: Optional[dict] = None
    buyer_info: Optional[dict] = None
    seller_info: Optional[dict] = None

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        use_enum_values = True


class OrderInDB(Order):
    """Order model for database operations"""
    pass


class OrderResponse(Order):
    """Order response with populated information"""
    product_info: Optional[dict] = None
    buyer_info: Optional[dict] = None
    seller_info: Optional[dict] = None


# File: app/schemas/user.py


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    profile_image: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    profile_image: Optional[str] = None
    is_active: bool
    is_verified: bool


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
