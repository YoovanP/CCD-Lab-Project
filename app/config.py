"""Validated local settings. Model sources are fixed in the allowlisted registry."""
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env", env_file_encoding="utf-8", extra="ignore"
    )
    model_cache_dir: Path = PROJECT_ROOT / "models" / "cache"
    model_local_files_only: bool = False
    max_input_chars: int = Field(default=2000, ge=1, le=10000)
    max_input_tokens: int = Field(default=256, ge=8, le=512)
    inference_threads: int = Field(default=1, ge=1, le=8)
    max_concurrent_inferences: int = Field(default=2, ge=1, le=16)
    inference_timeout_seconds: float = Field(default=15, gt=0, le=120)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    @field_validator("model_cache_dir")
    @classmethod
    def resolve_cache_dir(cls, value: Path) -> Path:
        return value if value.is_absolute() else PROJECT_ROOT / value
