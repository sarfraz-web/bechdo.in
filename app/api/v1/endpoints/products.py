from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.product import ProductCreate, ProductUpdate, ProductFilter
from app.models.product import ProductResponse, ProductCondition
from app.services.product_service import product_service
from app.utils.image_upload import image_upload_service

router = APIRouter()


@router.post("/", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    current_user=Depends(get_current_user)
):
    """Create a new product"""
    product = await product_service.create_product(product_data, current_user.id)
    return await product_service.get_product_by_id(product.id)


@router.get("/", response_model=List[ProductResponse])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    condition: Optional[ProductCondition] = Query(None),
    location: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """Get products with filters"""
    filter_data = ProductFilter(
        category=category,
        min_price=min_price,
        max_price=max_price,
        condition=condition,
        location=location,
        search=search
    )

    products = await product_service.get_products(filter_data, skip, limit)
    return products


@router.get("/my-products", response_model=List[ProductResponse])
async def get_my_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user=Depends(get_current_user)
):
    """Get current user's products"""
    products = await product_service.get_user_products(current_user.id, skip, limit)
    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    """Get product by ID"""
    product = await product_service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Increment views
    await product_service.increment_views(product_id)

    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_data: ProductUpdate,
    current_user=Depends(get_current_user)
):
    """Update product (only by owner)"""
    product = await product_service.update_product(product_id, product_data, current_user.id)
    if not product:
        raise HTTPException(status_code=404,
                            detail="Product not found or not authorized")

    return product


@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    current_user=Depends(get_current_user)
):
    """Delete product (only by owner)"""
    success = await product_service.delete_product(product_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404,
                            detail="Product not found or not authorized")

    return {"message": "Product deleted successfully"}


@router.post("/upload-images")
async def upload_product_images(
    files: List[UploadFile] = File(...),
    current_user=Depends(get_current_user)
):
    """Upload product images"""
    if len(files) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 images allowed")

    try:
        image_urls = []
        for file in files:
            image_url = await image_upload_service.upload_image(file, "products")
            image_urls.append(image_url)

        return {"message": "Images uploaded successfully",
                "image_urls": image_urls}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}", response_model=List[ProductResponse])
async def get_user_products(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """Get products by user ID"""
    products = await product_service.get_user_products(user_id, skip, limit)
    return products
