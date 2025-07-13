from typing import Optional
from bson import ObjectId
from app.core.database import get_database
from app.core.security import get_password_hash, verify_password
from app.models.user import User, UserInDB
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self):
        self.collection_name = "users"

    async def create_user(self, user_data: UserCreate) -> UserInDB:
        """Create a new user"""
        db = await get_database()

        # Check if user exists
        existing_user = await db[self.collection_name].find_one({
            "$or": [
                {"email": user_data.email},
                {"username": user_data.username}
            ]
        })

        if existing_user:
            raise ValueError("User with this email or username already exists")

        # Create user
        user_dict = user_data.dict()
        user_dict["hashed_password"] = get_password_hash(user_data.password)
        del user_dict["password"]

        user = UserInDB(**user_dict)
        result = await db[self.collection_name].insert_one(user.dict(by_alias=True))
        user.id = str(result.inserted_id)

        return user

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email"""
        db = await get_database()
        user_dict = await db[self.collection_name].find_one({"email": email})

        if user_dict:
            user_dict["_id"] = str(user_dict["_id"])
            return UserInDB(**user_dict)
        return None

    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID"""
        db = await get_database()
        user_dict = await db[self.collection_name].find_one({"_id": ObjectId(user_id)})

        if user_dict:
            user_dict["_id"] = str(user_dict["_id"])
            return UserInDB(**user_dict)
        return None

    async def authenticate_user(self, email: str,
                                password: str) -> Optional[UserInDB]:
        """Authenticate user with email and password"""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def update_user(self, user_id: str,
                          user_data: UserUpdate) -> Optional[UserInDB]:
        """Update user information"""
        db = await get_database()

        update_data = user_data.dict(exclude_unset=True)
        if update_data:
            await db[self.collection_name].update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )

        return await self.get_user_by_id(user_id)


user_service = UserService()
