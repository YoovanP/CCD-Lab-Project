# Later integration work

AWS-compatible storage, metadata, queueing and workers are planned in Phase 3.
Independent model services are planned in Phase 2; CI/cloud deployment in Phase 5.
These components are not implemented in the Phase 1 archive.
Prometheus/Grafana remain optional additions to basic measured observability.
No EKS is used. Actual EC2/k3s provisioning requires a separate cost review and
authorization; local emulator tests cannot prove actual cloud deployment.
