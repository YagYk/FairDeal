from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "FairDeal"
    debug: bool = True

    # Paths
    base_dir: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = base_dir / "data"
    # Primary market dataset (single file). README expects this path.
    market_data_path: Path = data_dir / "market_data.json"
    market_data_dir: Path = data_dir / "market_data"
    market_intel_dir: Path = data_dir / "market_intelligence"
    contracts_raw_dir: Path = data_dir / "raw_contracts"
    processed_dir: Path = data_dir / "processed"
    chroma_dir: Path = data_dir / "chroma"

    # RAG / embeddings
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    chroma_collection_name: str = "fairdeal_contracts"

    # LLM (Gemini or other) - optional
    llm_api_key: str | None = None
    llm_model: str = "gemini-1.5-pro"
    llm_timeout_seconds: int = 30
    llm_max_retries: int = 3

    class Config:
        env_prefix = "FAIRDEAL_"
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

