import json
from pathlib import Path
from typing import List, Dict, Any

class SpatialHotspotForecaster:
    def __init__(self, data_path: Path):
        self.data_path = data_path

    def compute_hotspots(self) -> List[Dict[str, Any]]:
        if not self.data_path.exists():
            return []

        with open(self.data_path, "r", encoding="utf-8") as f:
            incidents = json.load(f)

        sectors = {}
        for inc in incidents:
            sec = inc.get("sector_name", "General Grid")
            if sec not in sectors:
                sectors[sec] = {
                    "sector": sec,
                    "sector_code": inc.get("sector_code", "SEC-00"),
                    "lats": [],
                    "lons": [],
                    "severities": [],
                    "incidents_count": 0,
                    "critical_count": 0
                }
            sectors[sec]["lats"].append(inc.get("latitude", 34.0522))
            sectors[sec]["lons"].append(inc.get("longitude", -118.2437))
            sectors[sec]["severities"].append(inc.get("severity_score", 50))
            sectors[sec]["incidents_count"] += 1
            if inc.get("severity_tier") == "Critical":
                sectors[sec]["critical_count"] += 1

        hotspots = []
        for name, data in sectors.items():
            avg_lat = sum(data["lats"]) / len(data["lats"])
            avg_lon = sum(data["lons"]) / len(data["lons"])
            avg_sev = sum(data["severities"]) / len(data["severities"])
            
            # Risk rating computation: combined incident density and severity index
            risk_rating = round((avg_sev * 0.6) + min(40, (data["incidents_count"] * 0.8)), 1)
            threat_color = "#ff3366" if risk_rating >= 80 else "#ffaa00" if risk_rating >= 60 else "#00ff9d"

            hotspots.append({
                "cluster_id": f"HOTSPOT-{data['sector_code']}",
                "sector_name": name,
                "sector_code": data["sector_code"],
                "latitude": round(avg_lat, 6),
                "longitude": round(avg_lon, 6),
                "incident_density": data["incidents_count"],
                "critical_incidents": data["critical_count"],
                "mean_severity": round(avg_sev, 2),
                "composite_risk_rating": risk_rating,
                "threat_color": threat_color,
                "patrol_recommendation": "DEPLOY_CONTINUOUS_SWEEP" if risk_rating >= 80 else "INCREASE_FREQUENCY"
            })

        return sorted(hotspots, key=lambda x: x["composite_risk_rating"], reverse=True)
