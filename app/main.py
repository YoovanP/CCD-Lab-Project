"""FastAPI REST application with real model lifecycle and safe failures."""
import asyncio
import logging
import threading
from contextlib import asynccontextmanager
from time import perf_counter
from typing import Callable

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import Settings
from app.inference import InferenceTimeout, SentimentModel
from app.model_registry import REGISTRY, ModelSpec, metadata
from app.observability import configure_logging, event
from app.schemas import ErrorResponse, InferenceRequest, InferenceResponse, ModelMetadata


def create_app(
    settings: Settings | None = None,
    model_factory: Callable[[ModelSpec, Settings], SentimentModel] = SentimentModel,
) -> FastAPI:
    settings = settings or Settings()
    configure_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        for model_id, spec in REGISTRY.items():
            try:
                model = model_factory(spec, settings)
                await asyncio.to_thread(model.load)
                application.state.models[model_id] = model
                event("model_ready", model=model_id, revision=spec.revision)
            except Exception as exc:
                # Keep liveness available while readiness fails. Do not fake inference.
                event("model_load_failed", logging.ERROR, model=model_id,
                      error_type=type(exc).__name__)
        try:
            yield
        finally:
            for model in application.state.models.values():
                model.close()
            application.state.models.clear()

    application = FastAPI(
        title="AI Model Serving Platform", version="0.1.0", lifespan=lifespan,
        description="Phase 1 CPU sentiment REST API. AWS integrations are deferred.",
    )
    application.state.models = {}
    application.state.settings = settings
    application.state.slots = threading.BoundedSemaphore(settings.max_concurrent_inferences)

    @application.exception_handler(RequestValidationError)
    async def validation_error(_request: Request, exc: RequestValidationError):
        # FastAPI's default errors echo input. Exclude input and validator context.
        errors = [
            {"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]}
            for e in exc.errors()
        ]
        return JSONResponse(status_code=422, content={"detail": errors})

    @application.get("/health/live", tags=["health"])
    def live():
        return {"status": "alive"}

    @application.get("/health/ready", tags=["health"],
                     responses={503: {"model": ErrorResponse}})
    def ready():
        if not all(
            model_id in application.state.models and application.state.models[model_id].ready
            for model_id in REGISTRY
        ):
            raise HTTPException(503, "Model is not ready")
        return {"status": "ready"}

    @application.get("/api/models", response_model=list[ModelMetadata], tags=["models"])
    def models():
        return [
            metadata(spec, settings, bool(application.state.models.get(model_id)
                     and application.state.models[model_id].ready))
            for model_id, spec in REGISTRY.items()
        ]

    @application.get("/api/models/{model_id}", response_model=ModelMetadata,
                     tags=["models"], responses={404: {"model": ErrorResponse}})
    def model_details(model_id: str):
        if model_id not in REGISTRY:
            raise HTTPException(404, "Unknown model")
        model = application.state.models.get(model_id)
        return metadata(REGISTRY[model_id], settings, bool(model and model.ready))

    @application.post("/api/inference", response_model=InferenceResponse,
                      tags=["inference"],
                      responses={code: {"model": ErrorResponse}
                                 for code in (404, 429, 500, 503, 504)})
    def inference(body: InferenceRequest):
        started = perf_counter()
        code = 500
        acquired = False
        try:
            if len(body.input) > settings.max_input_chars:
                raise HTTPException(422, f"Input exceeds {settings.max_input_chars} characters")
            if body.model not in REGISTRY:
                raise HTTPException(404, "Unknown model")
            model = application.state.models.get(body.model)
            if model is None or not model.ready:
                raise HTTPException(503, "Model is not ready")
            acquired = application.state.slots.acquire(blocking=False)
            if not acquired:
                raise HTTPException(429, "Inference capacity reached; retry later",
                                    headers={"Retry-After": "1"})
            result = model.predict(body.input)
            response = InferenceResponse(
                model=body.model, prediction=result.label, confidence=result.confidence,
                processing_time_ms=round((perf_counter() - started) * 1000, 3),
                tokens_processed=result.tokens_processed, truncated=result.truncated,
            )
            code = 200
            return response
        except HTTPException as exc:
            code = exc.status_code
            raise
        except InferenceTimeout:
            code = 504
            raise HTTPException(504, "Inference timed out") from None
        except Exception as exc:
            event("inference_failed", logging.ERROR, error_type=type(exc).__name__)
            raise HTTPException(500, "Inference failed") from None
        finally:
            if acquired:
                application.state.slots.release()
            # Only log model IDs that belong to the allowlist.
            event("inference", model=body.model if body.model in REGISTRY else "unknown",
                  status_code=code, processing_time_ms=round((perf_counter() - started) * 1000, 3))

    return application


app = create_app()
