"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Paths
    project_root: Path = Path(__file__).resolve().parents[2]
    data_dir: Path = project_root / "DS-RPC-01" / "data"
    chroma_dir: Path = project_root / "chroma_db"
    collection_name: str = "finsolve_docs"

    # Auth
    jwt_secret: str = "change-me-in-production-use-strong-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480

    # Groq LLM
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # LangSmith
    langsmith_api_key: str = ""
    langsmith_project: str = "finsolve-chatbot"

    # Embeddings (local, no API key required)
    embedding_model: str = "all-MiniLM-L6-v2"

    # RAG
    chunk_size: int = 1000
    chunk_overlap: int = 150
    top_k: int = 4

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_url: str = "http://localhost:8000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
