# Development environment
Fill this out on the computer used to run the project before Phase 1.

| Field | Value |
| --- | --- |
| OS and version | Not recorded |
| Shell | PowerShell or Bash; confirm before implementation |
| Python | Target 3.12; actual version not recorded |
| CPU and available cores | Not recorded |
| Total RAM and RAM allocated to Docker | Not recorded |
| Available disk | Not recorded |
| Docker version | Not recorded |
| Kubernetes distribution and version | Not selected |
| kubectl version and active context | Not recorded |
| Model source, license and revision | To verify in Phase 1 |

PowerShell environment checks:
```powershell
py -3.12 --version
git --version
docker version
kubectl version --client
```
Bash environment checks:
```bash
python3.12 --version
git --version
docker version
kubectl version --client
```
Docker and Kubernetes checks become required before Phases 2 and 4 respectively.
Record actual output rather than assuming these tools are installed.
