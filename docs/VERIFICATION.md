# Phase 1 verification record

Verification was performed in the assistant execution environment on Linux using
Python 3.12.14, not on the user's machine. Dependency versions are pinned in
requirements.txt and requirements-dev.txt.

- Downloaded all three assets from the immutable registry revision.
- Verified total asset size: 68,293,328 bytes.
- prepare_model.py --verify passed with actual positive and negative predictions.
- Full final suite: 32 passed in 0.67 seconds; no tests skipped.
- Four integration tests ran the actual ONNX model: positive, negative, truncation
  and CPU-provider/native-timeout recovery.
- API fault tests verified safe 500/503/504 errors, 429 capacity rejection and
  validation; no production inference backend was substituted.
- pip check: no broken requirements found.
- Started a real Uvicorn server on 127.0.0.1:8877, then ran smoke_test.py over HTTP.
- Live checks passed for health, metadata, real predictions, unknown model and
  missing/blank/oversized input.
- Captured structured server logs and confirmed demo input text was absent.
- Model preparation and live server startup worked with cached offline assets.

Observed live example outputs from this environment:
positive confidence 0.9998831748962402 and processing time 6.590 ms;
negative confidence 0.9998059868812561 and processing time 6.996 ms.
These are individual smoke-test observations, not performance benchmarks or
expected timing guarantees. The formal load-results CSV remains empty.

Windows/macOS commands are documented, but those platforms were not run here.
Actual model RAM usage was not reliably measured. Docker, Kubernetes, AWS,
Floci, load experiments and CI/CD have not been implemented or tested yet.
