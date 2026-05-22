from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    upload_dir: str = "uploaded_files"
    model_path: str = "models/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
    chroma_persist_dir: str = "data/chroma_db"
    cors_origins: list[str] = ["http://localhost:5173"]
    max_file_size_mb: int = 50
    n_ctx: int = 2048
    n_threads: int = 4

    model_config = {"env_file": ".env"}


settings = Settings()
