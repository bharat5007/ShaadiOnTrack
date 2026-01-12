# Wedding Core Microservice

A FastAPI-based microservice for managing wedding planning, vendors, budgets, and services.

## 🚀 Features

- **Wedding Management**: Create and manage wedding events
- **Budget Tracking**: Track budget categories and expenses
- **Vendor Management**: Manage vendors and their services
- **Service Categories**: Organize services by categories
- **Authentication**: Integration with Auth-service for JWT authentication
- **RESTful API**: Full CRUD operations for all entities
- **Auto Documentation**: Interactive API docs with Swagger UI

## 📋 Prerequisites

- Python 3.9 or higher
- PostgreSQL 12 or higher
- Virtual environment (venv)

## 🔧 Quick Setup

### Option 1: Automated Setup (macOS/Linux)

```bash
# Make setup script executable
chmod +x setup.sh run.sh

# Run setup
./setup.sh

# Start the service
./run.sh
```

### Option 2: Manual Setup

#### 1. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Setup Database

```bash
# Create PostgreSQL database
psql -U postgres -c "CREATE DATABASE wedding_db;"
```

#### 4. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env file with your configuration
nano .env  # or use your preferred editor
```

Update these values in `.env`:
```env
DATABASE_URL=postgresql://your_user:your_password@localhost:5432/wedding_db
DB_USER=your_user
DB_PASSWORD=your_password
JWT_SECRET_KEY=your-secret-key-here
AUTH_SERVICE_URL=http://localhost:8001
```

#### 5. Run the Application

```bash
# Using Python
python run.py

# Or using uvicorn directly
uvicorn app.main:app --reload --port 8000
```

## 📖 API Documentation

Once the service is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🗄️ Database Schema

The service manages the following entities:

### Wedding Core
- Main wedding event information
- Budget tracking (total and spent)
- User associations

### Budget Categories
- Budget allocation by category
- Actual costs vs planned
- Remaining budget tracking

### Service Categories
- Types of services available
- Metadata for customization

### Vendors
- Vendor contact information
- Service category associations
- Multi-contact support

### Vendor Media
- Media files associated with vendors
- Type and metadata tracking

### Budget-Vendor Mapping
- Links budgets to vendors
- Track vendor assignments per wedding

## 🔑 Authentication

This service integrates with an external Auth-service for authentication.

### How it works:

1. User authenticates with Auth-service
2. Auth-service returns JWT token
3. Include token in requests to Wedding-core:
   ```
   Authorization: Bearer <your-jwt-token>
   ```

### Endpoints require authentication:

All endpoints except:
- `GET /` (root)
- `GET /health` (health check)
- `GET /docs` (API documentation)

### Example Request:

```bash
curl -X GET "http://localhost:8000/api/v1/weddings" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 🧪 Testing

### Manual Testing

Use the Swagger UI at http://localhost:8000/docs to test all endpoints interactively.

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Create a service category (requires auth)
curl -X POST "http://localhost:8000/api/v1/service-categories/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Photography", "meta": "Professional photography services"}'

# Get all service categories
curl -X GET "http://localhost:8000/api/v1/service-categories/" \
  -H "Authorization: Bearer <token>"
```

## 📁 Project Structure

```
wedding-core/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # CRUD operations
│   ├── crud_base.py         # Base CRUD class
│   ├── auth.py              # Authentication logic
│   ├── routers/             # API route handlers
│   │   ├── __init__.py
│   │   ├── weddings.py
│   │   ├── budget_categories.py
│   │   ├── service_categories.py
│   │   ├── vendors.py
│   │   └── vendor_media.py
│   └── service_managers/    # Business logic
│       ├── __init__.py
│       └── service_categories_manager.py
├── .env                     # Environment variables (not in git)
├── .env.example             # Environment template
├── .gitignore              # Git ignore rules
├── requirements.txt         # Python dependencies
├── setup.sh                # Setup script
├── run.sh                  # Run script
├── run.py                  # Python run script
└── README.md               # This file
```

## 🔄 Common Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Install new package
pip install <package-name>
pip freeze > requirements.txt

# Run with auto-reload (development)
uvicorn app.main:app --reload

# Run with specific port
uvicorn app.main:app --port 8080

# Check Python dependencies
pip list

# Deactivate virtual environment
deactivate
```

## 🐛 Troubleshooting

### Database Connection Error

```bash
# Check if PostgreSQL is running
pg_isready

# Restart PostgreSQL
# macOS:
brew services restart postgresql

# Linux:
sudo systemctl restart postgresql
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Virtual Environment Issues

```bash
# Remove and recreate virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Import Errors

```bash
# Make sure you're in the virtual environment
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## 📚 API Endpoints

### Weddings

- `POST /api/v1/weddings/` - Create wedding
- `GET /api/v1/weddings/` - List user's weddings
- `GET /api/v1/weddings/{id}` - Get wedding details
- `PUT /api/v1/weddings/{id}` - Update wedding
- `DELETE /api/v1/weddings/{id}` - Delete wedding

### Budget Categories

- `POST /api/v1/budget-categories/` - Create budget category
- `GET /api/v1/budget-categories/wedding/{id}` - List by wedding
- `GET /api/v1/budget-categories/{id}` - Get category details
- `PUT /api/v1/budget-categories/{id}` - Update category
- `DELETE /api/v1/budget-categories/{id}` - Delete category

### Service Categories

- `POST /api/v1/service-categories/` - Create service category
- `GET /api/v1/service-categories/` - List all categories
- `GET /api/v1/service-categories/{id}` - Get category details
- `PUT /api/v1/service-categories/{id}` - Update category
- `DELETE /api/v1/service-categories/{id}` - Delete category

### Vendors

- `POST /api/v1/vendors/` - Create vendor
- `GET /api/v1/vendors/` - List vendors (with filters)
- `GET /api/v1/vendors/{id}` - Get vendor details
- `PUT /api/v1/vendors/{id}` - Update vendor
- `DELETE /api/v1/vendors/{id}` - Delete vendor

### Vendor Media

- `POST /api/v1/vendor-media/` - Add vendor media
- `GET /api/v1/vendor-media/vendor/{id}` - List by vendor
- `GET /api/v1/vendor-media/{id}` - Get media details
- `PUT /api/v1/vendor-media/{id}` - Update media
- `DELETE /api/v1/vendor-media/{id}` - Delete media

## 🔐 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://...` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `DB_NAME` | Database name | `wedding_db` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `postgres` |
| `SERVICE_NAME` | Service name | `wedding-core` |
| `SERVICE_PORT` | Service port | `8000` |
| `DEBUG` | Debug mode | `True` |
| `AUTH_SERVICE_URL` | Auth service URL | `http://localhost:8001` |
| `JWT_SECRET_KEY` | JWT secret key | Required |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 📧 Support

For issues and questions, please open an issue in the repository.

---

**Happy Wedding Planning! 💒**