# Architecture and implementation status

Phase 1: an HTTP client calls the FastAPI application. The allowlisted registry
resolves sentiment to a pinned quantized model. One ONNX session loads at startup
and serves CPU predictions. Health checks distinguish liveness and readiness.

| Component | Phase | Status |
| --- | --- | --- |
| FastAPI REST interface, registry, model adapter | 1 | Implemented |
| Independent model containers and router | 2 | Planned |
| Floci S3/SQS/DynamoDB adapters and async workers | 3 | Planned |
| Local Kubernetes Services, Deployments and HPA | 4 | Planned |
| Metrics Server, load generator and measurements | 4 | Planned |
| GitHub Actions, image publishing and deployment | 5 | Planned |
| Actual AWS infrastructure and monitoring | 5 | Separate authorized milestone |

EKS is excluded. Later cloud compute can use self-managed k3s on EC2.
Floci emulates supported AWS APIs; it does not run the inference model or replace
Docker/Kubernetes. Local integration success is distinct from actual AWS deployment.
HPA scales Pods; a single-node cluster still has finite CPU and RAM.
