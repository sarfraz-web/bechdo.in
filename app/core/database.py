from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client = None
database = None


async def init_db():
    global client, database
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[settings.DATABASE_NAME]

    # Create indexes
    await create_indexes()


async def close_db():
    global client
    if client:
        client.close()


async def get_database():
    return database


async def create_indexes():
    """Create database indexes for better performance"""
    # User indexes
    await database.users.create_index("email", unique=True)
    await database.users.create_index("username", unique=True)

    # Product indexes
    await database.products.create_index("seller_id")
    await database.products.create_index("category")
    await database.products.create_index("created_at")
    await database.products.create_index([("title", "text"), ("description", "text")])

    # Order indexes
    await database.orders.create_index("buyer_id")
    await database.orders.create_index("seller_id")
    await database.orders.create_index("created_at")
