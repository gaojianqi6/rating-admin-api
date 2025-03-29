## Rating Admin System API

### Start the Project
```Bash
# Enter the venv
source rating-venv/bin/activate

# Start app.main
uvicorn app.main:app --reload
```

### Local Environment Configuration
1. Create `.env` file, Add some credentials to the file
```env
# Databse url
ADMIN_DATABASE_URL="postgresql+psycopg2://username:password@localhost/rating"

# For JWT Token
ADMIN_JWT_SECRET=****

```

### Doc
FastAPI automatically includes interactive API documentation (Swagger UI) at /docs and ReDoc at /redoc. For example: `http://localhost:8000/docs` or `http://localhost:8000/redoc`.