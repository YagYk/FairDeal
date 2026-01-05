# Database Setup Guide

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**
   Create a `.env` file in the project root:
   ```env
   JWT_SECRET_KEY=your-secret-key-minimum-32-characters-long-for-production
   DATABASE_URL=sqlite:///./chroma_db/fairdeal.db
   ```

3. **Start the Backend**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```
   
   The database will be automatically created on first startup.

## Database Models

### User Table
- Stores user authentication and profile information
- Fields: id, email, hashed_password, name, created_at, is_active

### ContractAnalysis Table
- Stores analysis history for each user
- Fields: id, user_id, contract_filename, fairness_score, metadata fields, created_at

## Production Setup (PostgreSQL)

1. **Install PostgreSQL** and create a database:
   ```sql
   CREATE DATABASE fairdeal;
   ```

2. **Update `.env`**:
   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/fairdeal
   ```

3. **Start the backend** - tables will be created automatically.

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user  
- `GET /api/auth/me` - Get current user (requires auth)

### Profile
- `GET /api/profile/stats` - Get user statistics (requires auth)
- `GET /api/profile/analyses` - Get analysis history (requires auth)

## Frontend Configuration

Set the API base URL in `frontend/.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

Or update `frontend/src/services/api.ts` directly.

