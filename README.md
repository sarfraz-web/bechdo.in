
A complete backend API for a buying/selling marketplace built with FastAPI and MongoDB.

## Features

✅ **User Authentication & Authorization**
- JWT-based authentication
- User registration and login
- Protected routes
- User profiles with image upload

✅ **Product Management**
- CRUD operations for products
- Image upload (Cloudinary/S3)
- Product search and filtering
- Categories and conditions
- View tracking

✅ **Order Management**
- Create and manage orders
- Order status tracking
- Payment status management
- Buyer and seller order views

✅ **Database**
- MongoDB with async Motor driver
- Proper indexing for performance
- Data validation with Pydantic

✅ **File Upload**
- Support for Cloudinary and AWS S3
- Image validation and resizing
- Secure file handling

## Quick Start

### Prerequisites
- Python 3.11+
- MongoDB
- (Optional) Cloudinary or AWS S3 account for image uploads

### Installation

1. **Clone and setup**
```bash
git clone <repository>
cd marketplace-backend
pip install -r requirements.txt
```

2. **Environment setup**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start MongoDB**
```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or use your local MongoDB installation
```

4. **Run the application**
```bash
# Development
python -m app.main

# Or with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user info

### Users
- `GET /api/v1/users/profile` - Get user profile
- `PUT /api/v1/users/profile` - Update user profile
- `POST /api/v1/users/upload-avatar` - Upload profile image
- `GET /api/v1/users/{user_id}` - Get user by ID

### Products
- `POST /api/v1/products/` - Create product
- `GET /api/v1/products/` - Get products with filters
- `GET /api/v1/products/my-products` - Get current user's products
- `GET /api/v1/products/{product_id}` - Get product by ID
- `PUT /api/v1/products/{product_id}` - Update product
- `DELETE /api/v1/products/{product_id}` - Delete product
- `POST /api/v1/products/upload-images` - Upload product images

### Orders
- `POST /api/v1/orders/` - Create order
- `GET /api/v1/orders/` - Get user's orders (as buyer)
- `GET /api/v1/orders/sales` - Get user's sales (as seller)
- `GET /api/v1/orders/{order_id}` - Get order by ID
- `PUT /api/v1/orders/{order_id}` - Update order status

## Configuration

### Environment Variables

```env
# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=marketplace_db

# Security
SECRET_KEY=your-super-secret-jwt-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Cloudinary (Optional)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# AWS S3 (Optional)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_BUCKET_NAME=your_bucket_name
AWS_REGION=us-east-1
```

## Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  username: String,
  email: String,
  hashed_password: String,
  full_name: String,
  phone: String,
  address: String,
  profile_image: String,
  is_active: Boolean,
  is_verified: Boolean,
  created_at: Date,
  updated_at: Date
}
```

### Products Collection
```javascript
{
  _id: ObjectId,
  title: String,
  description: String,
  price: Number,
  category: String,
  condition: String,
  images: [String],
  seller_id: String,
  status: String,
  location: String,
  tags: [String],
  views: Number,
  created_at: Date,
  updated_at: Date
}
```

### Orders Collection
```javascript
{
  _id: ObjectId,
  product_id: String,
  buyer_id: String,
  seller_id: String,
  quantity: Number,
  total_price: Number,
  status: String,
  payment_status: String,
  shipping_address: String,
  buyer_notes: String,
  seller_notes: String,
  created_at: Date,
  updated_at: Date
}
```

## Docker Deployment

```bash
# Build image
docker build -t marketplace-api .

# Run with Docker Compose
docker-compose up -d
```

## Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## Production Considerations

1. **Security**
   - Change default SECRET_KEY
   - Use environment variables for all secrets
   - Configure CORS properly
   - Use HTTPS in production

2. **Database**
   - Use MongoDB Atlas or properly configured replica set
   - Configure proper backup strategy
   - Monitor database performance

3. **File Storage**
   - Configure CDN for image delivery
   - Set up proper image optimization
   - Implement file cleanup strategies

4. **Performance**
   - Use connection pooling
   - Implement caching (Redis)
   - Configure proper indexes
   - Monitor API performance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details  # bechdo.in
