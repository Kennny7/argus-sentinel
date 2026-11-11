# ARGUS Sentinel - Containerized Docker Deployment Guide

## 1. Prerequisites

- Docker Engine version 24.0 or higher
- Docker Compose version 2.20 or higher
- At least 4 CPU cores and 8GB RAM

## 2. Compose Cluster Architecture

The root `docker-compose.yml` deploys the entire ecosystem:

```text
Cluster Services:
- argus-redis           (Redis 7.2 Alpine)              Port 6379
- argus-redpanda        (Redpanda Kafka Broker)         Port 9092
- argus-gateway         (Gateway API)                   Port 8000
- argus-prediction      (Crime Prediction Engine)       Port 8001
- argus-surveillance    (Surveillance & 3D Profiling)   Port 8002
- argus-ingestion       (Multi-Source Ingestion)        Port 8003
- argus-ontology        (Ontology & Agentic Engine)     Port 8004
- argus-dashboard       (Tactical Command Center)       Port 3000
```

## 3. Deployment Commands

### Build and Launch All Services
```bash
docker-compose up --build -d
```

### Check Container Status
```bash
docker-compose ps
```

### Inspect Container Logs
```bash
# View combined logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f gateway-api
docker-compose logs -f surveillance-recon
docker-compose logs -f crime-prediction
```

### Stop Cluster
```bash
docker-compose down
```

### Stop Cluster and Wipe Volumes
```bash
docker-compose down -v
```

<details>
<summary>Click to Expand Production Hardening Recommendations</summary>

### 1. Reverse Proxy & SSL Termination
For production municipal environments, place an Nginx or Traefik reverse proxy in front of `argus-gateway` (:8000) and `argus-dashboard` (:3000) with TLS 1.3 certificates.

### 2. Private Subnet Isolation
Place internal microservices (`crime-prediction`, `surveillance-recon`, `stream-ingestion`, `ontology-agent`, `redpanda`, `redis`) on an isolated Docker bridge network (`argus-internal-net`), exposing only the Gateway (:8000) and Dashboard (:3000) to the host interface.

### 3. Resource Constraints
Add CPU and memory limits to `docker-compose.yml` for predictable scaling:
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2048M
```
</details>
