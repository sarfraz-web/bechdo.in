from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.order import OrderCreate, OrderUpdate, OrderFilter
from app.models.order import OrderResponse, OrderStatus, PaymentStatus
from app.services.order_service import order_service

router = APIRouter()


@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user = Depends(get_current_user)
):
    """Create a new order"""
    try:
        order = await order_service.create_order(order_data, current_user.id)
        return await order_service.get_order_by_id(order.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[OrderResponse])
async def get_my_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[OrderStatus] = Query(None),
    payment_status: Optional[PaymentStatus] = Query(None),
    current_user = Depends(get_current_user)
):
    """Get current user's orders (as buyer)"""
    filter_data = OrderFilter(status=status, payment_status=payment_status)
    orders = await order_service.get_user_orders(
        current_user.id, filter_data, skip, limit, as_buyer=True
    )
    return orders


@router.get("/sales", response_model=List[OrderResponse])
async def get_my_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[OrderStatus] = Query(None),
    payment_status: Optional[PaymentStatus] = Query(None),
    current_user = Depends(get_current_user)
):
    """Get current user's sales (as seller)"""
    filter_data = OrderFilter(status=status, payment_status=payment_status)
    orders = await order_service.get_user_orders(
        current_user.id, filter_data, skip, limit, as_buyer=False
    )
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user = Depends(get_current_user)
):
    """Get order by ID"""
    order = await order_service.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if user is involved in this order
    if order.buyer_id != current_user.id and order.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    return order


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: str,
    order_data: OrderUpdate,
    current_user = Depends(get_current_user)
):
    """Update order status (only by seller)"""
    order = await order_service.update_order(order_id, order_data, current_user.id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found or not authorized")
    
    return order
