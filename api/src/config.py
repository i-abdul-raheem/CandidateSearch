import os
from dataclasses import dataclass
from pathlib import Path


API_ROOT = Path(__file__).resolve().parents[1]


def _csv(name: str, default: str = "") -> tuple[str, ...]:
    return tuple(value.strip() for value in os.getenv(name, default).split(",") if value.strip())


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Candidate Search API")
    app_version: str = "0.2.0"
    environment: str = os.getenv("ENVIRONMENT", "development")
    data_dir: Path = Path(os.getenv("DATA_DIR", API_ROOT / "data")).resolve()
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-large")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen3:4b")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    max_upload_bytes: int = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
    api_key: str | None = os.getenv("API_KEY") or None
    cors_origins: tuple[str, ...] = _csv("CORS_ORIGINS")

    @property
    def resume_dir(self) -> Path:
        return self.data_dir / "pdf"

    @property
    def upload_dir(self) -> Path:
        return self.resume_dir / "uploads"


settings = Settings()
