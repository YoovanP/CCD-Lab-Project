# Load testing
Implementation begins in Phase 4, after Kubernetes inference works.
We will use k6 and record concurrency, duration, payload, model revision and hardware.
Run warm-up, a one-replica baseline, sustained high load, then recovery/scale-in.
Record throughput, mean/p95 latency, error rate, CPU/memory and ready replicas.
Repeat each scenario three times if practical. See docs/PHASES.md.
For the scaling experiment, run the load generator inside the cluster against the
Service DNS name. A kubectl port-forward to a Service selects a Pod and does not
provide a representative load-balancing test across replicas.
