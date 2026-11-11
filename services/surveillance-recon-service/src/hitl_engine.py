import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

class HITLEngine:
    def __init__(self, poi_db_path: Path):
        self.poi_db_path = poi_db_path
        self.audit_log: List[Dict[str, Any]] = []

    def get_pending_queue(self) -> List[Dict[str, Any]]:
        if not self.poi_db_path.exists():
            return []
        with open(self.poi_db_path, "r", encoding="utf-8") as f:
            pois = json.load(f)

        queue = []
        for p in pois:
            status = p.get("verification_status", "")
            if "CONFIRMATION" in status or p.get("risk_level") == "Critical":
                queue.append({
                    "verification_id": f"HITL-{p['subject_id']}",
                    "subject_id": p["subject_id"],
                    "full_name": p["full_name"],
                    "alias": p["alias"],
                    "designation": p.get("designation", "POI"),
                    "threat_rating": p.get("threat_rating", 70),
                    "risk_level": p.get("risk_level", "High"),
                    "confidence_score": p.get("confidence_score", 0.85),
                    "image_reference": p.get("image_reference", ""),
                    "sighted_camera": p.get("last_observed_camera", "CAM-SEC-01-04"),
                    "timestamp": p.get("last_observed_timestamp", "2026-08-13T12:57:01Z"),
                    "status": "PENDING_OPERATOR_REVIEW"
                })
        return queue

    def record_decision(self, verification_id: str, subject_id: str, decision: str, operator_name: str, operator_notes: str) -> Dict[str, Any]:
        with open(self.poi_db_path, "r", encoding="utf-8") as f:
            pois = json.load(f)

        found = False
        for p in pois:
            if p["subject_id"] == subject_id:
                p["verification_status"] = decision
                p["verified_by"] = operator_name
                p["verification_notes"] = operator_notes
                p["verification_timestamp"] = datetime.utcnow().isoformat() + "Z"
                found = True
                break

        if found:
            with open(self.poi_db_path, "w", encoding="utf-8") as f:
                json.dump(pois, f, indent=2)

        audit_entry = {
            "verification_id": verification_id,
            "subject_id": subject_id,
            "decision": decision,
            "operator_name": operator_name,
            "operator_notes": operator_notes,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        self.audit_log.append(audit_entry)
        return audit_entry
