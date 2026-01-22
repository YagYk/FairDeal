from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from ..config import settings
from ..logging_config import get_logger
from ..models.schemas import AnalyzeResponse


log = get_logger("service.cache")


class CacheService:
    """
    File-based caching for contract analysis results.
    """

    def __init__(self) -> None:
        self.cache_dir = settings.processed_dir / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, file_hash: str) -> Optional[AnalyzeResponse]:
        """
        Retrieve cached analysis for a given file hash.
        """
        cache_path = self.cache_dir / f"{file_hash}.json"
        if not cache_path.exists():
            return None
        
        try:
            data = json.loads(cache_path.read_text())
            return AnalyzeResponse(**data)
        except Exception as exc:
            log.error(f"Failed to read cache for {file_hash}: {exc}")
            return None

    def set(self, file_hash: str, response: AnalyzeResponse) -> None:
        """
        Store analysis in cache.
        """
        cache_path = self.cache_dir / f"{file_hash}.json"
        try:
            cache_path.write_text(response.model_dump_json(indent=2))
        except Exception as exc:
            log.error(f"Failed to write cache for {file_hash}: {exc}")
