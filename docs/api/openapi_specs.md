# ARGUS Sentinel - OpenAPI Specifications & REST Contract

Comprehensive reference of all RESTful and WebSocket API endpoints across the ARGUS Sentinel microservices ecosystem.

## 1. Gateway API Endpoints (Port 8000)

| Method | Endpoint | Description | Request Body | Response Payload |
|---|---|---|---|---|
| `GET` | `/` | Root system status | None | Operational status and active service URLs |
| `GET` | `/health` | Health & WebSocket count | None | Status, timestamp, active sessions |
| `GET` | `/api/v1/incidents` | List municipal incidents | Query params: `sector`, `tier`, `limit` | Incident records array |
| `POST` | `/api/v1/incidents` | Ingest new incident | Incident metadata JSON | Created incident record |
| `POST` | `/api/v1/predictions/severity` | Predict incident severity | Feature dictionary | Severity score & classification tier |
| `GET` | `/api/v1/predictions/hotspots` | Spatial risk hotspots | None | Geographic clusters and risk ratings |
| `GET` | `/api/v1/surveillance/cameras` | Surveillance camera directory | None | List of cameras, FOVs, locations |
| `GET` | `/api/v1/surveillance/targets/active` | Active optical targets | None | Bounding boxes, track IDs, traits |
| `GET` | `/api/v1/surveillance/profiles/3d/{id}`| 3D facial topology mesh | None | 468 vertices, pose angles, IPD |
| `GET` | `/api/v1/surveillance/hitl/queue` | Pending human review queue | None | Items requiring operator review |
| `POST` | `/api/v1/surveillance/hitl/verify` | Submit operator verification | Verification decision JSON | Audit trail confirmation |
| `GET` | `/api/v1/ontology/query` | Full ontology graph | None | Entities and knowledge triples |
| `POST` | `/api/v1/ontology/briefing` | Agent investigation report | Subject ID & Sector JSON | Synthesized intelligence dossier |
| `GET` | `/api/v1/streams/status` | Streaming pipelines status | None | Active connectors & throughput |
| `WS` | `/ws/telemetry` | Live incident & tracking stream| Bi-directional WebSocket | Real-time broadcast alerts |

---

## 2. Crime Prediction Endpoints (Port 8001)

| Method | Endpoint | Description | Request Body |
|---|---|---|---|
| `GET` | `/health` | Service health & loaded models | None |
| `POST` | `/predict/severity` | Predict severity score & tier | `{crime_type, premise_type, weapon_type, victim_age, latitude, longitude}` |
| `POST` | `/predict/batch` | High-throughput batch scoring | Array of incident feature objects |
| `GET` | `/predict/hotspots` | Sector-level risk clustering | None |
| `POST` | `/train` | Retrain models on dataset | None |
| `GET` | `/metrics` | Accuracy, F1, and RMSE | None |

---

## 3. Surveillance Reconnaissance Endpoints (Port 8002)

| Method | Endpoint | Description | Request Body |
|---|---|---|---|
| `GET` | `/health` | Service health & enrolled count | None |
| `POST` | `/recon/match/vector` | Cosine similarity search | `{probe_vector: float[128], threshold: float}` |
| `GET` | `/recon/subjects/{id}` | Subject intelligence dossier | None |
| `GET` | `/recon/profiles/3d/{id}`| 3D cranial landmark mesh | None |
| `POST` | `/recon/profiles/3d/reconstruct` | Synthesize 3D facial mesh | `{subject_id, full_name, pitch, yaw, roll}` |
| `GET` | `/recon/hitl/queue` | Human review queue items | None |
| `POST` | `/recon/hitl/verify` | Operator audit decision | `{verification_id, subject_id, decision, operator_name, operator_notes}` |

---

## 4. Stream Ingestion Endpoints (Port 8003)

| Method | Endpoint | Description | Request Body |
|---|---|---|---|
| `GET` | `/health` | Service health & supported formats | None |
| `POST` | `/ingest/event` | Ingest stream record | `{source_protocol: str, payload: dict}` |
| `GET` | `/ingest/status` | Pipeline metrics & status | None |

---

## 5. Ontology & Agent Endpoints (Port 8004)

| Method | Endpoint | Description | Request Body |
|---|---|---|---|
| `GET` | `/health` | Service health & graph node count | None |
| `GET` | `/graph/schema` | Full knowledge ontology | None |
| `GET` | `/graph/entity/{id}` | Neighbor connections for entity | None |
| `POST` | `/agent/investigate` | Autonomous LLM investigation | `{subject_id: str, sector: str}` |
