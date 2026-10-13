"""Only this registry can map client model IDs to model assets."""
from dataclasses import dataclass
from types import MappingProxyType

from app.config import Settings
from app.schemas import ModelMetadata


@dataclass(frozen=True)
class ModelSpec:
    id: str
    name: str
    source: str
    revision: str
    weights: str


SENTIMENT = ModelSpec(
    id="sentiment",
    name="DistilBERT SST-2 sentiment (quantized ONNX)",
    source="Xenova/distilbert-base-uncased-finetuned-sst-2-english",
    revision="0b6928efcb76139cae2c6881d49cda67fe119f42",
    weights="onnx/model_quantized.onnx",
)
REGISTRY = MappingProxyType({SENTIMENT.id: SENTIMENT})


def metadata(spec: ModelSpec, settings: Settings, ready: bool) -> ModelMetadata:
    return ModelMetadata(
        id=spec.id, name=spec.name, task="sentiment-analysis",
        source=spec.source, revision=spec.revision, runtime="ONNX Runtime CPU",
        labels=["negative", "positive"], ready=ready,
        max_input_chars=settings.max_input_chars,
        max_input_tokens=settings.max_input_tokens,
        confidence_description=(
            "Softmax score for the predicted class. Not a calibrated probability "
            "of correctness. This binary model has no neutral class."
        ),
    )
