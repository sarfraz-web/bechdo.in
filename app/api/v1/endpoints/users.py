from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.user import UserUpdate, UserResponse
from app.services.user_service import user_service
from app.utils.image_upload import image_upload_service

router = APIRouter()


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user=Depends(get_current_user)):
    """Get user profile"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone,
        address=current_user.address,
        profile_image=current_user.profile_image,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified
    )


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_data: UserUpdate,
    current_user=Depends(get_current_user)
):
    """Update user profile"""
    updated_user = await user_service.update_user(current_user.id, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=updated_user.id,
        username=updated_user.username,
        email=updated_user.email,
        full_name=updated_user.full_name,
        phone=updated_user.phone,
        address=updated_user.address,
        profile_image=updated_user.profile_image,
        is_active=updated_user.is_active,
        is_verified=updated_user.is_verified
    )


@router.post("/upload-avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    """Upload user avatar"""
    try:
        # Upload image
        image_url = await image_upload_service.upload_image(file, "avatars")

        # Update user profile with new image
        user_update = UserUpdate(profile_image=image_url)
        await user_service.update_user(current_user.id, user_update)

        return {"message": "Avatar uploaded successfully",
                "image_url": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: str):
    """Get user by ID (public information only)"""
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        address=user.address,
        profile_image=user.profile_image,
        is_active=user.is_active,
        is_verified=user.is_verified
    )
