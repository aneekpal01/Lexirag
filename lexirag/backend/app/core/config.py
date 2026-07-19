from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Postgres
    database_url: str = "postgresql://lexirag:lexirag@localhost:5432/lexirag"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "lexirag_documents"

    # LLM providers (set the one you're using)
    gemini_api_key: str = ""
    openai_api_key: str = ""
    llm_provider: str = "gemini"  # "gemini" | "openai"
    llm_model: str = "gemini-2.5-flash"

    # Embeddings
    embedding_model: str = "BAAI/bge-m3"
    embedding_dim: int = 1024

    # Chunking
    chunk_size: int = 800
    chunk_overlap: int = 150

    # Retrieval
    top_k_retrieve: int = 20
    top_k_final: int = 6

    # Auth
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24

    # Uploads
    upload_dir: str = "./uploads"
    max_upload_mb: int = 100


settings = Settings()
