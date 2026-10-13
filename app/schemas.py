"""Public REST request and response schemas."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class InferenceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: str = Field(min_length=1, max_length=64, strict=True)
    input: str = Field(min_length=1, max_length=10000, strict=True)

    @field_validator("input")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Input must contain non-whitespace text")
        return value


class InferenceResponse(BaseModel):
    status: Literal["success"] = "success"
    model: str
    prediction: Literal["positive", "negative"]
    confidence: float = Field(ge=0, le=1)
    processing_time_ms: float = Field(ge=0)
    tokens_processed: int = Field(gt=0)
    truncated: bool


class ModelMetadata(BaseModel):
    id: str
    name: str
    task: str
    source: str
    revision: str
    runtime: str
    labels: list[str]
    ready: bool
    max_input_chars: int
    max_input_tokens: int
    confidence_description: str


class ErrorResponse(BaseModel):
    detail: str
