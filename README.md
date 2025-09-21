# RateEverything Admin API 🌟

## Overview
RateEverything is a unified rating and review platform that brings together diverse media types under one roof. Whether you're rating movies, music, TV shows, books, podcasts, or even physical locations like restaurants and stores, RateEverything provides a seamless experience for users to share their opinions and discover new content.

## 🌟 Features
- Comprehensive rating system for multiple media types
- Single user profile for all rating activities
- Cross-media recommendations
- Interactive API documentation
- Secure authentication with JWT
- PostgreSQL database integration

## 🛠️ Technology Stack
- **Backend Framework**: FastAPI (Python)
- **Database ORM**: SQLModel & SQLAlchemy
- **Database**: PostgreSQL
- **API Documentation**: Swagger UI & ReDoc
- **Authentication**: JWT (JSON Web Tokens)

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- PostgreSQL database
- Virtual environment (recommended)

### Installation

1. Clone the repository
```bash
git clone [repository-url]
cd rating-admin-api
```

2. Create and activate a virtual environment
```bash
python -m venv rating-venv
source rating-venv/bin/activate  # On Windows, use: rating-venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables
Create a `.env` file in the root directory with the following content:
```env
# Database Configuration
ADMIN_DATABASE_URL="postgresql+psycopg://username:password@localhost/rating"

# JWT Configuration
ADMIN_JWT_SECRET="your-secret-key-here"
```

### Running the Application

1. Ensure your virtual environment is activated
```bash
source rating-venv/bin/activate  # On Windows, use: rating-venv\Scripts\activate
```

2. Start the server
```bash
uvicorn app.main:app --reload
```

3. Access the API documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📝 API Documentation
The project includes comprehensive API documentation that you can access through:
- Swagger UI: Interactive documentation with testing capabilities
- ReDoc: Alternative documentation interface with a clean, responsive design

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
