# Authentication & Database Setup

## Overview

This application now uses a production-ready database system with JWT authentication. All mock data has been removed and replaced with real database storage.

## Database Setup

### Development (SQLite)

By default, the app uses SQLite for development. The database file will be created at:
```
./chroma_db/fairdeal.db
```

### Production (PostgreSQL)

For production, update your `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/fairdeal
```

## Installation

1. Install backend dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```env
JWT_SECRET_KEY=your-secret-key-min-32-characters-long
DATABASE_URL=sqlite:///./chroma_db/fairdeal.db  # or PostgreSQL URL
```

3. Initialize the database:
```bash
# The database will be automatically created on first API startup
python -m uvicorn app.main:app --reload
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user info

### Profile
- `GET /api/profile/stats` - Get user statistics
- `GET /api/profile/analyses` - Get user's analysis history

## Frontend Configuration

Update `frontend/src/services/api.ts` with your backend URL:
```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
```

Or set in `.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

## Database Models

### User
- `id`: UUID primary key
- `email`: Unique email address
- `hashed_password`: Bcrypt hashed password
- `name`: User's full name
- `created_at`: Account creation timestamp
- `is_active`: Account status

### ContractAnalysis
- `id`: UUID primary key
- `user_id`: Foreign key to users
- `contract_filename`: Original filename
- `fairness_score`: Analysis score (0-100)
- `contract_type`, `industry`, `role`, `location`: Contract metadata
- `salary`, `notice_period_days`: Numeric fields
- `created_at`: Analysis timestamp

## Security

- Passwords are hashed using bcrypt
- JWT tokens expire after 7 days (configurable)
- All API endpoints require authentication except register/login
- CORS is configured for frontend origins

## Migration to Production

1. Set up PostgreSQL database
2. Update `DATABASE_URL` in `.env`
3. Set strong `JWT_SECRET_KEY` (min 32 characters)
4. Update CORS origins in `backend/app/main.py`
5. Run database migrations (if using Alembic)

