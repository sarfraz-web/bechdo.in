from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class User(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    username: str = Field(..., min_length=3, max_length=20)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    hashed_password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    profile_image: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class UserInDB(User):
    """User model for database operations"""
    pass


class UserPublic(BaseModel):
    """Public user information (without sensitive data)"""
    id: str
    username: str
    full_name: Optional[str] = None
    profile_image: Optional[str] = None
    created_at: datetime

    class Config:
        populate_by_name = True
