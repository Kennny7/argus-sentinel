import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from .config import settings
    from .biometric_matcher import BiometricReconMatcher
    from .mesh_3d_engine import FacialMesh3DEngine
    from .hitl_engine import HITLEngine
except ImportError:
    from config import settings
    from biometric_matcher import BiometricReconMatcher
    from mesh_3d_engine import FacialMesh3DEngine
    from hitl_engine import HITLEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("argus-surveillance-service")

app = FastAPI(
    title="ARGUS Surveillance Recon & 3D Profiling Service",
    version="2.4.0",
    description="CCTV stream target acquisition, vector biometric matching, 3D facial mesh reconstruction, and HITL verification engine."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

matcher = BiometricReconMatcher(settings.POI_DB_PATH)
mesh_engine = FacialMesh3DEngine(settings.PROFILES_3D_PATH)
hitl = HITLEngine(settings.POI_DB_PATH)

class VectorMatchRequest(BaseModel):
    probe_vector: List[float]
    threshold: Optional[float] = 0.70

class Reconstruct3DRequest(BaseModel):
    subject_id: str
    full_name: str
    pitch: Optional[float] = 0.0
    yaw: Optional[float] = 0.0
    roll: Optional[float] = 0.0

class HITLActionRequest(BaseModel):
    verification_id: str
    subject_id: str
    decision: str  # "APPROVE_MATCH", "REJECT_FALSE_POSITIVE", "ESCALATE_ALERT"
    operator_name: str
    operator_notes: str

@app.get("/health")
def health():
    return {
        "status": "HEALTHY",
        "service": "argus-surveillance-recon",
        "enrolled_subjects": len(matcher.records),
        "profiles_3d_count": len(mesh_engine.profiles_3d)
    }

@app.post("/recon/match/vector")
def match_face_vector(req: VectorMatchRequest):
    matches = matcher.match_vector(req.probe_vector, min_threshold=req.threshold or 0.70)
    return {"matches_found": len(matches), "results": matches}

@app.get("/recon/subjects/{subject_id}")
def get_subject_profile(subject_id: str):
    poi = matcher.get_poi(subject_id)
    if not poi:
        raise HTTPException(status_code=404, detail="Subject not found")
    return poi

@app.get("/recon/profiles/3d/{subject_id}")
def get_3d_profile(subject_id: str):
    return mesh_engine.get_profile(subject_id)

@app.post("/recon/profiles/3d/reconstruct")
def reconstruct_3d(req: Reconstruct3DRequest):
    profile = mesh_engine.reconstruct_3d_profile(
        subject_id=req.subject_id,
        full_name=req.full_name,
        pitch=req.pitch or 0.0,
        yaw=req.yaw or 0.0,
        roll=req.roll or 0.0
    )
    return {"status": "SUCCESS", "profile": profile}

@app.get("/recon/hitl/queue")
def list_hitl_queue():
    items = hitl.get_pending_queue()
    return {"pending_count": len(items), "queue": items}

@app.post("/recon/hitl/verify")
def submit_hitl_verification(req: HITLActionRequest):
    audit = hitl.record_decision(
        verification_id=req.verification_id,
        subject_id=req.subject_id,
        decision=req.decision,
        operator_name=req.operator_name,
        operator_notes=req.operator_notes
    )
    return {"status": "DECISION_COMMITTED", "audit": audit}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.surveillance-recon-service.src.main:app", host=settings.SURVEILLANCE_HOST, port=settings.SURVEILLANCE_PORT, reload=True)
