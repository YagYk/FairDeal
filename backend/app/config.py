"""
Configuration management for ContractCompare.
Loads environment variables and provides typed configuration.
"""
from typing import Literal
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LLM Configuration
    google_api_key: str = ""
    llm_provider: Literal["gemini"] = "gemini"
    embedding_provider: Literal["gemini"] = "gemini"
    
    # Model Selection
    llm_model: str = "gemini-1.5-flash"  # Verified stable model for free tier
    embedding_model: str = "models/text-embedding-004"
    
    # ChromaDB Configuration
    chroma_db_path: str = "./chroma_db"
    chroma_collection_name: str = "contracts"
    
    # Data Paths (relative to backend directory)
    raw_contracts_path: str = "./data/raw_contracts"
    processed_contracts_path: str = "./data/processed"
    
    def get_raw_contracts_path(self) -> Path:
        """Get absolute path to raw contracts directory."""
        # Look in project root (parent of backend directory)
        project_root = Path(__file__).parent.parent.parent  # backend/app -> backend -> project_root
        return (project_root / self.raw_contracts_path.lstrip("./")).resolve()
    
    def get_processed_contracts_path(self) -> Path:
        """Get absolute path to processed contracts directory."""
        # Look in project root (parent of backend directory)
        project_root = Path(__file__).parent.parent.parent  # backend/app -> backend -> project_root
        return (project_root / self.processed_contracts_path.lstrip("./")).resolve()
    
    def get_chroma_db_path(self) -> Path:
        """Get absolute path to ChromaDB directory."""
        # Look in backend directory (ChromaDB is backend-specific)
        backend_dir = Path(__file__).parent.parent  # backend/app -> backend
        return (backend_dir / self.chroma_db_path).resolve()
    
    # Chunking Configuration
    max_chunk_size_tokens: int = 800
    chunk_overlap_tokens: int = 100
    
    # Database Configuration
    database_url: str = ""
    
    # JWT Configuration
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days
    
    class Config:
        # Find .env file in project root (parent of backend directory)
        env_file = str(Path(__file__).parent.parent.parent / ".env")
        case_sensitive = False


# Global settings instance
settings = Settings()

