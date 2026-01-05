"""
Database connection and session management.
Uses SQLAlchemy for ORM and supports both SQLite (dev) and PostgreSQL (production).
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Database URL - defaults to SQLite for development, can be overridden with DATABASE_URL env var
DATABASE_URL = settings.database_url or f"sqlite:///./{settings.chroma_db_path}/fairdeal.db"

# For PostgreSQL, use: postgresql://user:password@localhost/dbname
# For SQLite (default): sqlite:///./path/to/db.db

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Set to True for SQL query logging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI to get database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Call this on application startup.
    Also handles migrations for existing databases.
    """
    # Create all tables (if they don't exist)
    Base.metadata.create_all(bind=engine)
    
    # Handle migrations for existing databases
    if "sqlite" in DATABASE_URL:
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(engine)
            
            # Check if contract_analyses table exists and has analysis_result_json column
            if "contract_analyses" in inspector.get_table_names():
                columns = [col["name"] for col in inspector.get_columns("contract_analyses")]
                if "analysis_result_json" not in columns:
                    # Add missing column
                    with engine.connect() as conn:
                        conn.execute(text("ALTER TABLE contract_analyses ADD COLUMN analysis_result_json TEXT"))
                        conn.commit()
        except Exception as e:
            # Migration failed, but don't crash - log and continue
            import logging
            logging.warning(f"Database migration check failed: {e}")

