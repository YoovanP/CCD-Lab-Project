# Phase 1 REST API contract

Implemented by FastAPI. OpenAPI schema: /openapi.json. Swagger UI: /docs.

| Method | Path | Success | Errors |
| --- | --- | --- | --- |
| GET | /health/live | 200, status alive | Process must be running |
| GET | /health/ready | 200, status ready | 503 if model unavailable |
| GET | /api/models | 200, array of model metadata | — |
| GET | /api/models/{model_id} | 200, model details | 404 unknown model |
| POST | /api/inference | 200, real prediction | 404, 422, 429, 500, 503, 504 |

Inference request:

    {"model":"sentiment","input":"I love this product."}

Response fields: status (success), model, prediction (positive/negative),
confidence (actual softmax score), processing_time_ms (tokenization and prediction
processing duration, excluding HTTP network time), tokens_processed, truncated.
No fixed score or latency is promised.

Only the model ID sentiment is allowlisted. Source/revision cannot be supplied
by a client. Text must be a non-blank string, at most 2000 characters by default.
Extra request keys are rejected. Text beyond 256 tokens is truncated and disclosed
with truncated=true. Both limits are configured in .env and listed in metadata.

Errors use a detail string, or a detail array for schema validation (422).
Input text and private exception details are excluded from error responses.
429 includes Retry-After: 1. The native inference deadline uses 504.
Unknown model IDs return 404 without loading or downloading arbitrary models.
Model load failures leave liveness working but readiness/inference return 503.

/api/jobs and /metrics are not implemented. They will be added only alongside
real queue/state and monitoring implementations.
