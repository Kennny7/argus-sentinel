import sys
from pathlib import Path
import pytest

root_dir = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root_dir / "services" / "surveillance-recon-service" / "src"))

from biometric_matcher import BiometricReconMatcher
from mesh_3d_engine import FacialMesh3DEngine
from hitl_engine import HITLEngine

def test_biometric_matching():
    db_path = root_dir / "data" / "intelligence" / "persons_of_interest.json"
    matcher = BiometricReconMatcher(db_path)
    assert len(matcher.records) > 0
    
    probe = matcher.records[0]["biometric_embedding"]
    matches = matcher.match_vector(probe, min_threshold=0.8)
    assert len(matches) > 0
    assert matches[0]["subject_id"] == matcher.records[0]["subject_id"]
    assert matches[0]["similarity_score"] >= 0.99

def test_3d_mesh_reconstruction(tmp_path):
    storage_path = tmp_path / "test_3d_profiles.json"
    engine = FacialMesh3DEngine(storage_path)
    profile = engine.reconstruct_3d_profile("POI-TEST-01", "Test Subject", pitch=2.5, yaw=-1.0)
    
    assert profile["subject_id"] == "POI-TEST-01"
    assert profile["mesh_vertex_count"] > 20
    assert "vertices" in profile
    assert profile["depth_confidence"] > 0.9

def test_hitl_lifecycle(tmp_path):
    # Copy sample DB to tmp to avoid mutating test data
    import shutil
    db_path = root_dir / "data" / "intelligence" / "persons_of_interest.json"
    temp_db = tmp_path / "poi.json"
    shutil.copy(db_path, temp_db)
    
    hitl = HITLEngine(temp_db)
    queue = hitl.get_pending_queue()
    assert len(queue) >= 0
    
    audit = hitl.record_decision(
        verification_id="HITL-TEST-01",
        subject_id="POI-8821",
        decision="APPROVE_MATCH",
        operator_name="Officer_Test",
        operator_notes="Confirmed via manual visual inspection."
    )
    assert audit["decision"] == "APPROVE_MATCH"
    assert audit["operator_name"] == "Officer_Test"
