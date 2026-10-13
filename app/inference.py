"""Real pretrained CPU inference; no Transformers/PyTorch installation required."""
import json
import threading
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import onnxruntime as ort
from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer

from app.config import Settings
from app.model_registry import ModelSpec


class InferenceTimeout(Exception):
    """The native ONNX run exceeded its deadline."""


@dataclass(frozen=True)
class Prediction:
    label: str
    confidence: float
    tokens_processed: int
    truncated: bool


def download_assets(spec: ModelSpec, settings: Settings) -> dict[str, Path]:
    """Fetch only three files from an immutable allowlisted revision."""
    return {
        filename: Path(hf_hub_download(
            repo_id=spec.source, filename=filename, revision=spec.revision,
            cache_dir=str(settings.model_cache_dir),
            local_files_only=settings.model_local_files_only,
        ))
        for filename in ("config.json", "tokenizer.json", spec.weights)
    }


class SentimentModel:
    def __init__(self, spec: ModelSpec, settings: Settings):
        self.spec = spec
        self.settings = settings
        self._session: ort.InferenceSession | None = None
        self._tokenizer: Tokenizer | None = None
        self._labels: dict[int, str] = {}

    @property
    def ready(self) -> bool:
        return self._session is not None and self._tokenizer is not None

    def load(self) -> None:
        assets = download_assets(self.spec, self.settings)
        config = json.loads(assets["config.json"].read_text(encoding="utf-8"))
        labels = {int(k): v.lower() for k, v in config["id2label"].items()}
        if labels != {0: "negative", 1: "positive"}:
            raise ValueError("Unexpected labels for allowlisted sentiment model")
        tokenizer = Tokenizer.from_file(str(assets["tokenizer.json"]))
        tokenizer.enable_truncation(max_length=self.settings.max_input_tokens)
        options = ort.SessionOptions()
        options.intra_op_num_threads = self.settings.inference_threads
        options.inter_op_num_threads = 1
        options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        session = ort.InferenceSession(
            str(assets[self.spec.weights]), sess_options=options,
            providers=["CPUExecutionProvider"],
        )
        if {x.name for x in session.get_inputs()} != {"input_ids", "attention_mask"}:
            raise ValueError("Unexpected ONNX input contract")
        self._session, self._tokenizer, self._labels = session, tokenizer, labels
        # Readiness requires a real warm-up prediction, not merely a downloaded file.
        try:
            self.predict("A good film.")
        except Exception:
            self.close()
            raise

    def predict(self, text: str) -> Prediction:
        session, tokenizer = self._session, self._tokenizer
        if session is None or tokenizer is None:
            raise RuntimeError("Model is not loaded")
        encoding = tokenizer.encode(text)
        feed = {
            "input_ids": np.array([encoding.ids], dtype=np.int64),
            "attention_mask": np.array([encoding.attention_mask], dtype=np.int64),
        }
        run_options = ort.RunOptions()
        expired = threading.Event()

        def terminate() -> None:
            expired.set()
            run_options.terminate = True

        timer = threading.Timer(self.settings.inference_timeout_seconds, terminate)
        timer.daemon = True
        timer.start()
        try:
            logits = session.run(["logits"], feed, run_options=run_options)[0][0]
        except Exception as exc:
            if expired.is_set():
                raise InferenceTimeout("Inference deadline exceeded") from exc
            raise
        finally:
            timer.cancel()
        if expired.is_set():
            raise InferenceTimeout("Inference deadline exceeded")
        if logits.shape != (2,) or not np.isfinite(logits).all():
            raise ValueError("Invalid model logits")
        probabilities = np.exp(logits - np.max(logits))
        probabilities /= probabilities.sum()
        index = int(np.argmax(probabilities))
        return Prediction(
            label=self._labels[index], confidence=float(probabilities[index]),
            tokens_processed=len(encoding.ids), truncated=bool(encoding.overflowing),
        )

    def close(self) -> None:
        self._session = None
        self._tokenizer = None
        self._labels = {}
