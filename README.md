# AI Model Serving Platform with Dynamic Scaling

Phase 1 is implemented: a FastAPI REST API with real CPU sentiment inference,
validation, health checks, model metadata and automated tests. No EKS is used.

Start with [docs/PHASE_1.md](docs/PHASE_1.md). It contains complete PowerShell and
Bash install/run/test commands, expected responses, acceptance checks and recovery.

## Quick start on Windows PowerShell

Open the extracted ai-model-serving-platform folder in your terminal:

    py -3.12 -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
    .\.venv\Scripts\python.exe scripts/prepare_model.py --verify
    .\.venv\Scripts\python.exe -m pytest tests/ -v
    .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1

In a second terminal:

    .\.venv\Scripts\python.exe scripts/smoke_test.py

Open http://127.0.0.1:8000/docs to try the API. The guide also includes Bash commands.
Copy .env.example to .env only when you want to configure settings.

## Implemented endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | /health/live | Process liveness |
| GET | /health/ready | Model readiness after real warm-up |
| GET | /api/models | Allowlisted model metadata |
| GET | /api/models/{model_id} | Model details or 404 |
| POST | /api/inference | Real label, score and measured timing |
| GET | /docs | Swagger UI |
| GET | /openapi.json | Generated API schema |

## Five phase roadmap

| Phase | Scope | Current status |
| --- | --- | --- |
| 1 | Environment, REST API, one real model and tests | Implemented and tested here; verify on your machine |
| 2 | Docker, independent model services and routing | Pending |
| 3 | Floci/AWS storage, metadata, queue and workers | Pending |
| 4 | Local Kubernetes, HPA, observability and load experiments | Pending |
| 5 | CI/CD, AWS deployment testing and final demo | Pending |

[docs/PHASES.md](docs/PHASES.md) explains each gate. AWS integrations remain part of
the full project, but they are not required to test the Phase 1 API. The cloud
compute approach is self-managed Kubernetes/k3s on EC2, with no EKS. Local
emulation and real cloud deployment have separate verification milestones.

## Project files

| Path | Responsibility |
| --- | --- |
| app/main.py | REST endpoints, lifespan loading, health and safe failures |
| app/config.py | Validated environment settings |
| app/schemas.py | Request/response schemas |
| app/model_registry.py | Allowlisted ID, immutable upstream revision and metadata |
| app/inference.py | Download/load quantized ONNX model and CPU predictions |
| app/observability.py | Structured logs without full input text |
| tests/ | 32 lifecycle, validation, failure and real-model checks |
| scripts/prepare_model.py | Download pinned assets and verify real predictions |
| scripts/smoke_test.py | Live HTTP acceptance checks |
| docs/PHASE_1.md | Setup and troubleshooting |
| models/README.md | Model provenance and limitations |
| docs/VERIFICATION.md | Actual verification performed for this release |

Dockerfile, Kubernetes YAML, load-test scripts, cleanup scripts and CI are still
clearly marked placeholders. They are not runnable infrastructure or passing CI. The CI placeholder is named
ci.yml.example so GitHub does not try to run it.
Do not run the future Docker/Kubernetes steps yet.

## Model and constraints

The model is DistilBERT fine-tuned for English binary SST-2 sentiment, using
Xenova's quantized ONNX export. Three required files total 68,293,328 bytes; weights
are downloaded on first preparation/startup rather than bundled in the archive.
No paid inference API, GPU or PyTorch installation is required.

The immutable revision is recorded in model_registry.py. The model loads once
per process and runs a warm-up before readiness. Failed loading returns 503 for
readiness/inference while retaining liveness. Restart after fixing the cause.

Default input limit is 2000 characters, with truncation to 256 tokens disclosed in
the response. Confidence is a softmax class score, not calibrated correctness.
Two inference slots are allowed; additional active requests get 429. A 15-second
native inference deadline returns 504. Logs omit full input and private exception
messages. The API is a local lab service; authentication is not implemented.

Stop Uvicorn with Ctrl+C. Keep .env and downloaded assets out of Git.
Performance experiments, Kubernetes scaling and cloud deployment are not yet tested.
