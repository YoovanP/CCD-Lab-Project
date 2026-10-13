# Five phase roadmap and acceptance gates

User-confirmed constraint: no EKS. The PDF's AWS integration goals are retained;
compute can use local Kubernetes and later self-managed k3s on EC2.
Build incrementally. A test passing here does not substitute for verification
on the developer's machine. Advance only when the current gate passes.

## Phase 1 — API and one real CPU model

Implemented now. Use docs/PHASE_1.md for exact PowerShell/Bash commands.
Install requirements-dev.txt, run prepare_model.py --verify, run all 32 tests,
start Uvicorn, run smoke_test.py and submit predictions in /docs.
Gate: real positive/negative predictions; valid measured response; health,
metadata and error tests pass. Record OS, shell, CPU/RAM and Python version.
Recovery: check interpreter/venv, model download/cache and startup logs.

## Phase 2 — Docker, independent model services and routing

Package the working API/model with non-root Docker execution, reproducible
model assets and documented startup behavior. Add a second verified CPU model
in a separate container/service and a routing entry point that allowlists models.
The detailed container layout will be added during implementation.

Planned container checks (Bash or PowerShell):

    docker build --no-cache -t ai-model-serving:dev .
    docker run --rm --name ai-model-serving -p 8000:8000 ai-model-serving:dev

Run smoke_test.py from another terminal. Verify both model services independently
and through the router, including unknown IDs and one unavailable backend.
Gate: clean builds work without undocumented host caches; real inference reaches
the correct independent service; safe backend failures and health checks work.
Recovery: inspect build logs, model assets, filesystem permissions, ports and RAM.

## Phase 3 — AWS-compatible integrations and asynchronous inference

Add configuration/adapters for S3 artifacts, DynamoDB metadata/job state, and SQS
jobs using Floci for local testing. Verify current supported operations before
implementation. Use synthetic data and local dummy credentials with an explicit
emulator endpoint. Add worker containers and genuine submit/status endpoints.

Gate: store/retrieve an artifact; persist/query metadata; submit a job, process it,
persist output and retrieve status. Test duplicate delivery, worker restart,
failure, retry and acknowledgment after durable result storage.
No process-local job dictionary can stand in for shared durable job state.
Exact CLI and integration-test commands will be supplied with the implementation.
Recovery: inspect supported operations, endpoint override, region, container
networking, worker logs and persisted status. Emulator tests do not prove AWS deployment.

## Phase 4 — Kubernetes, HPA and measurements

Choose kind, k3d or minikube from installed tools and document exact image import.
Implement Namespace, Deployments, Services, probes and resource requests/limits.
Verify Metrics Server before enabling CPU-based autoscaling/v2 HPA.

Planned checks (Bash or PowerShell):

    kubectl get deployments,pods,svc,hpa -n ai-serving
    kubectl rollout status deployment/ai-model-serving -n ai-serving
    kubectl top nodes
    kubectl top pods -n ai-serving
    kubectl describe hpa ai-model-serving -n ai-serving
    kubectl get hpa -n ai-serving --watch

Gate: Service routing works across ready replicas, probes/resources are correct,
metrics are numeric, sustained inference load produces scale-out, and recovery
produces scale-in. Record workload/environment, throughput, mean/p95 latency,
errors, CPU/memory, ready replicas and scaling delays. Repeat runs when practical.
Run multi-replica load inside the cluster against Service DNS; a Service
port-forward selects a Pod and is appropriate for smoke checks only.
Recovery: inspect image availability, selectors/probes, Metrics Server, CPU
requests, HPA events and finite node capacity. More Pods do not add node CPU.
Implement cleanup scoped to the project's namespace and verify it.

## Phase 5 — CI/CD, cloud integration and reproducible demo

Automate tests, image builds, ECR publishing and manifest validation using GitHub
Actions. Introduce deployment automation only for a configured reachable target.
Hosted CI cannot automatically access a developer's private local cluster.
Implement cloud monitoring appropriate to the approved AWS deployment.

Before provisioning EC2/k3s, establish explicit authorization and verify
account-specific costs and limits. No EKS resources are used.
Gate: a real Actions run passes; tagged images publish/pull; authorized deployment
serves real predictions; AWS storage/queue/metadata integrations pass against
actual AWS if cloud completion is claimed; monitoring works; cleanup is verified.
Provide a 5–8 minute demo with measured results and documented limitations.
Recovery: inspect workflow permissions, registry auth, target connectivity,
manifest validation, cloud integration logs and remaining billable resources.

## Requirement reconciliation

The original Word brief supplied the API contract and local testing discipline.
The subsequent PDF adds independent model services, storage, metadata, async
processing and deployment automation as full-project goals. Those requirements
are staged above. The user's explicit no-EKS instruction resolves the conflicting
compute target. Cloud deployment is a separate later gate, not claimed from Floci.
