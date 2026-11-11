import json
import math
from pathlib import Path
from typing import List, Dict, Any, Optional

class BiometricReconMatcher:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.records: List[Dict[str, Any]] = []
        self.load_database()

    def load_database(self):
        if self.db_path.exists():
            with open(self.db_path, "r", encoding="utf-8") as f:
                self.records = json.load(f)
        else:
            self.records = []

    def save_database(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.records, f, indent=2)

    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        if len(vec_a) != len(vec_b) or not vec_a:
            return 0.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def match_vector(self, probe_vector: List[float], min_threshold: float = 0.70) -> List[Dict[str, Any]]:
        self.load_database()
        results = []
        for rec in self.records:
            emb = rec.get("biometric_embedding", [])
            sim = self.cosine_similarity(probe_vector, emb)
            if sim >= min_threshold:
                match_entry = {
                    "subject_id": rec["subject_id"],
                    "full_name": rec["full_name"],
                    "alias": rec["alias"],
                    "designation": rec.get("designation", "UNKNOWN"),
                    "risk_level": rec.get("risk_level", "Medium"),
                    "threat_rating": rec.get("threat_rating", 50),
                    "similarity_score": round(sim, 4),
                    "confidence_score": round(sim, 4),
                    "social_footprint": rec.get("social_footprint", {}),
                    "skills_and_stats": rec.get("skills_and_stats", {}),
                    "criminal_record": rec.get("criminal_record", []),
                    "verification_status": rec.get("verification_status", "PENDING_VERIFICATION"),
                    "last_observed_camera": rec.get("last_observed_camera", "CAM-SEC-01-04"),
                    "image_reference": rec.get("image_reference", "")
                }
                results.append(match_entry)

        return sorted(results, key=lambda x: x["similarity_score"], reverse=True)

    def get_poi(self, subject_id: str) -> Optional[Dict[str, Any]]:
        self.load_database()
        for rec in self.records:
            if rec.get("subject_id") == subject_id:
                return rec
        return None
