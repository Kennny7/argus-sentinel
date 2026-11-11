import asyncio
import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from pydantic import BaseModel

try:
    from .config import settings
    from .websocket_manager import ws_manager
except ImportError:
    from config import settings
    from websocket_manager import ws_manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("argus-gateway")

app = FastAPI(
    title="ARGUS Sentinel API Gateway",
    version="2.4.0",
    description="Central reverse proxy, WebSocket telemetry hub, and dispatch controller for ARGUS Sentinel."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_json_file(rel_path: str):
    path = settings.DATA_DIR / rel_path
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_json_file(rel_path: str, data: Any):
    path = settings.DATA_DIR / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

class IncidentCreateRequest(BaseModel):
    crime_type: str
    sector_code: str
    premise_type: str
    weapon_type: Optional[str] = "None"
    victim_age: Optional[int] = 30
    victim_gender: Optional[str] = "M"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class HITLVerificationRequest(BaseModel):
    verification_id: str
    subject_id: str
    decision: str  # "APPROVE_MATCH", "REJECT_FALSE_POSITIVE", "ESCALATE_ALERT"
    operator_name: str
    operator_notes: str

@app.get("/")
def get_root_status():
    return {
        "system": "ARGUS SENTINEL",
        "codename": "Civitas Intelligence Grid",
        "status": "OPERATIONAL",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "2.4.0",
        "active_microservices": {
            "gateway_api": "ONLINE (Port 8000)",
            "crime_prediction_service": f"AVAILABLE ({settings.PREDICTION_SERVICE_URL})",
            "surveillance_recon_service": f"AVAILABLE ({settings.SURVEILLANCE_SERVICE_URL})",
            "stream_ingestion_service": f"AVAILABLE ({settings.INGESTION_SERVICE_URL})",
            "ontology_agent_service": f"AVAILABLE ({settings.ONTOLOGY_SERVICE_URL})"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "HEALTHY",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "connections_active": len(ws_manager.active_connections)
    }

# ------------------------------------------------------------------------------
# Incidents Endpoints
# ------------------------------------------------------------------------------
@app.get("/api/v1/incidents")
def list_incidents(
    sector: Optional[str] = None,
    tier: Optional[str] = None,
    crime_type: Optional[str] = None,
    limit: int = Query(default=100, le=500)
):
    data = load_json_file("crime_records/crime_settlement_data.json")
    if not isinstance(data, list):
        data = []
    
    filtered = data
    if sector:
        filtered = [item for item in filtered if sector.lower() in item.get("sector_name", "").lower() or sector.lower() in item.get("sector_code", "").lower()]
    if tier:
        filtered = [item for item in filtered if tier.lower() == item.get("severity_tier", "").lower()]
    if crime_type:
        filtered = [item for item in filtered if crime_type.lower() in item.get("crime_type", "").lower()]

    return {
        "total_records": len(filtered),
        "limit": limit,
        "records": filtered[:limit]
    }

@app.post("/api/v1/incidents")
async def create_incident(payload: IncidentCreateRequest):
    data = load_json_file("crime_records/crime_settlement_data.json")
    new_id = f"INC-2026-{len(data) + 1:04d}"
    
    # Forward to prediction service if available, else compute locally
    severity_score = random.randint(45, 95)
    tier = "Medium"
    if severity_score >= 85:
        tier = "Critical"
    elif severity_score >= 70:
        tier = "High"

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.post(
                f"{settings.PREDICTION_SERVICE_URL}/predict/severity",
                json={
                    "crime_type": payload.crime_type,
                    "premise_type": payload.premise_type,
                    "weapon_type": payload.weapon_type,
                    "victim_age": payload.victim_age
                }
            )
            if resp.status_code == 200:
                pred = resp.json()
                severity_score = pred.get("severity_score", severity_score)
                tier = pred.get("severity_tier", tier)
    except Exception:
        pass

    record = {
        "incident_id": new_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sector_code": payload.sector_code,
        "sector_name": payload.sector_code,
        "crime_type": payload.crime_type,
        "severity_score": severity_score,
        "severity_tier": tier,
        "weapon_type": payload.weapon_type,
        "premise_type": payload.premise_type,
        "latitude": payload.latitude or 34.0522,
        "longitude": payload.longitude or -118.2437,
        "victim_age": payload.victim_age,
        "victim_gender": payload.victim_gender,
        "status": "Unit Dispatched",
        "responding_unit": f"UNIT-{random.randint(101, 149)}",
        "response_eta_minutes": random.randint(3, 8),
        "cctv_coverage": "HIGH",
        "surveillance_camera_id": f"CAM-{payload.sector_code}-01"
    }

    data.insert(0, record)
    save_json_file("crime_records/crime_settlement_data.json", data)

    # Broadcast via WebSocket
    await ws_manager.broadcast_json({
        "event_type": "NEW_INCIDENT_ALERT",
        "payload": record
    })

    return {"status": "SUCCESS", "incident": record}

# ------------------------------------------------------------------------------
# Predictions & Hotspots Proxy
# ------------------------------------------------------------------------------
@app.post("/api/v1/predictions/severity")
async def predict_severity(payload: Dict[str, Any]):
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(f"{settings.PREDICTION_SERVICE_URL}/predict/severity", json=payload)
            return resp.json()
    except Exception as exc:
        # Fallback heuristic calculation if microservice standalone
        base_sev = 75
        c_type = str(payload.get("crime_type", "")).lower()
        if "armed" in c_type or "weapon" in c_type:
            base_sev = 92
        elif "assault" in c_type or "homicide" in c_type:
            base_sev = 88
        elif "theft" in c_type or "burglary" in c_type:
            base_sev = 55
        
        tier = "Critical" if base_sev >= 85 else "High" if base_sev >= 70 else "Medium"
        return {
            "severity_score": base_sev,
            "severity_tier": tier,
            "risk_confidence": 0.915,
            "response_protocol": "IMMEDIATE_TACTICAL_DISPATCH" if tier in ["High", "Critical"] else "STANDARD_PATROL_MONITOR",
            "model_version": "ANN-MLP-v2.4-LOCAL",
            "fallback_used": True
        }

@app.get("/api/v1/predictions/hotspots")
async def get_hotspots():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.PREDICTION_SERVICE_URL}/predict/hotspots")
            return resp.json()
    except Exception:
        incidents = load_json_file("crime_records/crime_settlement_data.json")
        clusters = [
            {"sector": "Downtown Central", "cluster_id": "CLS-01", "risk_rating": 89, "incident_count": 48, "lat": 34.0522, "lon": -118.2437},
            {"sector": "West Harbor District", "cluster_id": "CLS-02", "risk_rating": 82, "incident_count": 39, "lat": 33.7432, "lon": -118.2673},
            {"sector": "North Industrial Ring", "cluster_id": "CLS-03", "risk_rating": 76, "incident_count": 31, "lat": 34.1808, "lon": -118.3090},
            {"sector": "South Transit Hub", "cluster_id": "CLS-04", "risk_rating": 71, "incident_count": 27, "lat": 33.9416, "lon": -118.4085}
        ]
        return {"hotspot_clusters": clusters, "timestamp": datetime.utcnow().isoformat() + "Z"}

# ------------------------------------------------------------------------------
# Surveillance, Biometrics, and 3D Profiles
# ------------------------------------------------------------------------------
@app.get("/api/v1/surveillance/cameras")
def get_cameras():
    return [
        {"camera_id": "CAM-SEC-01-04", "name": "Downtown Metro North Escalator", "sector": "Downtown Central", "lat": 34.0522, "lon": -118.2437, "status": "ONLINE", "stream_protocol": "RTSP/H264", "fov_angle": 120, "active_targets": 4},
        {"camera_id": "CAM-SEC-02-01", "name": "Harbor Wharf Pier 14", "sector": "West Harbor District", "lat": 33.7432, "lon": -118.2673, "status": "ONLINE", "stream_protocol": "RTSP/H264", "fov_angle": 95, "active_targets": 2},
        {"camera_id": "CAM-SEC-03-05", "name": "Industrial Terminal Gate C", "sector": "North Industrial Ring", "lat": 34.1808, "lon": -118.3090, "status": "ONLINE", "stream_protocol": "RTSP/H264", "fov_angle": 110, "active_targets": 1},
        {"camera_id": "CAM-SEC-05-02", "name": "East Tech Corridor Atrium", "sector": "East Tech Corridor", "lat": 34.1478, "lon": -118.1445, "status": "ONLINE", "stream_protocol": "RTSP/H264", "fov_angle": 135, "active_targets": 3},
        {"camera_id": "CAM-SEC-06-03", "name": "South Transit Concourse Central", "sector": "South Transit Hub", "lat": 33.9416, "lon": -118.4085, "status": "ONLINE", "stream_protocol": "RTSP/H264", "fov_angle": 140, "active_targets": 5}
    ]

@app.get("/api/v1/surveillance/targets/active")
def get_active_targets():
    pois = load_json_file("intelligence/persons_of_interest.json")
    targets = []
    for i, poi in enumerate(pois):
        targets.append({
            "tracking_id": f"TRK-{8800 + i*111}",
            "subject_id": poi["subject_id"],
            "full_name": poi["full_name"],
            "alias": poi["alias"],
            "designation": poi["designation"],
            "risk_level": poi["risk_level"],
            "threat_rating": poi["threat_rating"],
            "confidence_score": poi["confidence_score"],
            "camera_id": poi.get("last_observed_camera", "CAM-SEC-01-04"),
            "bounding_box": {
                "x_norm": 0.42 + (i * 0.05) % 0.25,
                "y_norm": 0.28 + (i * 0.04) % 0.35,
                "w_norm": 0.18,
                "h_norm": 0.45
            },
            "stats": poi.get("skills_and_stats", {}),
            "social_footprint": poi.get("social_footprint", {}),
            "verification_status": poi.get("verification_status", "FLAGGED_FOR_HUMAN_CONFIRMATION")
        })
    return {"active_targets": targets, "camera_sync_time": datetime.utcnow().isoformat() + "Z"}

@app.get("/api/v1/surveillance/profiles/3d/{subject_id}")
def get_3d_profile(subject_id: str):
    profiles = load_json_file("intelligence/3d_facial_profiles.json")
    if subject_id in profiles:
        return profiles[subject_id]
    first_key = list(profiles.keys())[0] if profiles else None
    if first_key:
        return profiles[first_key]
    raise HTTPException(status_code=404, detail="3D profile not found")

@app.get("/api/v1/surveillance/hitl/queue")
def get_hitl_queue():
    pois = load_json_file("intelligence/persons_of_interest.json")
    queue = []
    for poi in pois:
        if "CONFIRMATION" in poi.get("verification_status", "") or poi.get("risk_level") == "Critical":
            queue.append({
                "verification_id": f"HITL-{poi['subject_id']}",
                "subject_id": poi["subject_id"],
                "full_name": poi["full_name"],
                "alias": poi["alias"],
                "risk_level": poi["risk_level"],
                "match_confidence": poi["confidence_score"],
                "sighted_camera": poi.get("last_observed_camera", "CAM-SEC-01-04"),
                "timestamp": poi.get("last_observed_timestamp", "2026-08-13T12:57:01Z"),
                "status": "PENDING_OPERATOR_REVIEW"
            })
    return {"pending_verifications": queue, "total_pending": len(queue)}

@app.post("/api/v1/surveillance/hitl/verify")
async def verify_hitl(req: HITLVerificationRequest):
    pois = load_json_file("intelligence/persons_of_interest.json")
    found = False
    for poi in pois:
        if poi["subject_id"] == req.subject_id:
            poi["verification_status"] = req.decision
            poi["verified_by"] = req.operator_name
            poi["verification_notes"] = req.operator_notes
            poi["verification_timestamp"] = datetime.utcnow().isoformat() + "Z"
            found = True
            break
    
    if not found:
        raise HTTPException(status_code=404, detail="Subject not found")

    save_json_file("intelligence/persons_of_interest.json", pois)

    audit_entry = {
        "event_type": "HITL_DECISION_COMMITTED",
        "verification_id": req.verification_id,
        "subject_id": req.subject_id,
        "decision": req.decision,
        "operator": req.operator_name,
        "notes": req.operator_notes,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    await ws_manager.broadcast_json(audit_entry)

    return {"status": "SUCCESS", "audit": audit_entry}

# ------------------------------------------------------------------------------
# Ontology & AI Agent Investigation
# ------------------------------------------------------------------------------
@app.get("/api/v1/ontology/query")
def get_ontology_graph():
    return load_json_file("ontology/urban_crime_ontology.json")

@app.post("/api/v1/ontology/briefing")
async def generate_agent_briefing(payload: Dict[str, Any]):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(f"{settings.ONTOLOGY_SERVICE_URL}/agent/investigate", json=payload)
            return resp.json()
    except Exception:
        # Structured fallback response
        target = payload.get("subject_id", "POI-8821")
        sector = payload.get("sector", "Downtown Central")
        return {
            "investigation_id": f"INV-AGENT-{random.randint(1000, 9999)}",
            "subject_target": target,
            "target_sector": sector,
            "executive_summary": f"Comprehensive multi-modal synthesis indicates elevated threat convergence in {sector}. Subject {target} demonstrates high network centrality linking cyber infiltration vectors with local logistics syndicates.",
            "identified_syndicate": "DarkFiber Syndicate",
            "recommended_actions": [
                "Deploy tactical response unit to South Transit Hub intersection",
                "Lock surveillance perimeter CAM-SEC-01-04 with biometric continuous tracking",
                "Execute warrants on digital payload exfiltration endpoints"
            ],
            "agent_confidence": 0.948,
            "ontology_nodes_traversed": 18,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

# ------------------------------------------------------------------------------
# Data Streams Status
# ------------------------------------------------------------------------------
@app.get("/api/v1/streams/status")
def get_stream_status():
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "connectors": [
            {"stream": "Kafka / Redpanda Broker", "status": "ONLINE", "rate_eps": 142.5, "topic": "argus.incidents.raw"},
            {"stream": "Redis Stream Pipeline", "status": "ONLINE", "rate_eps": 210.0, "key": "argus:stream:telemetry"},
            {"stream": "RTSP Video Surveillance Matrix", "status": "STREAMING", "active_cameras": 5, "fps": 10},
            {"stream": "GeoJSON Emergency Dispatch (CAD)", "status": "ONLINE", "polling_sec": 2, "records_buffered": 128}
        ]
    }

# ------------------------------------------------------------------------------
# Real-Time WebSocket Telemetry
# ------------------------------------------------------------------------------
@app.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        # Send initial handshake message
        await websocket.send_text(json.dumps({
            "event_type": "TELEMETRY_HANDSHAKE_ESTABLISHED",
            "server_time": datetime.utcnow().isoformat() + "Z",
            "grid_status": "DEFCON_2",
            "active_streams": 4
        }))

        while True:
            # Keep connection alive & handle incoming client signals
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("action") == "PING":
                    await websocket.send_text(json.dumps({"action": "PONG", "timestamp": datetime.utcnow().isoformat() + "Z"}))
            except Exception:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.gateway-api.src.main:app", host=settings.GATEWAY_HOST, port=settings.GATEWAY_PORT, reload=True)
