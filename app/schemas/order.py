from typing import Optional
from pydantic import BaseModel, Field
from app.models.order import OrderStatus, PaymentStatus


class OrderCreate(BaseModel):
    product_id: str = Field(...)
    quantity: int = Field(..., ge=1)
    shipping_address: str = Field(...)
    buyer_notes: Optional[str] = None


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    seller_notes: Optional[str] = None


class OrderFilter(BaseModel):
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
