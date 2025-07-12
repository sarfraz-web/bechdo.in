// MongoDB initialization script
db = db.getSiblingDB('marketplace_db');

// Create collections
db.createCollection('users');
db.createCollection('products');
db.createCollection('orders');

// Create indexes
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "username": 1 }, { unique: true });

db.products.createIndex({ "seller_id": 1 });
db.products.createIndex({ "category": 1 });
db.products.createIndex({ "created_at": -1 });
db.products.createIndex({ "title": "text", "description": "text" });

db.orders.createIndex({ "buyer_id": 1 });
db.orders.createIndex({ "seller_id": 1 });
db.orders.createIndex({ "created_at": -1 });

print('Database initialized successfully');
