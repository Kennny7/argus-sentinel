import random
from datetime import datetime
from typing import Dict, Any

class GeoJSONStreamParser:
    @staticmethod
    def parse_cad_dispatch(feature: Dict[str, Any]) -> Dict[str, Any]:
        """Converts raw GeoJSON CAD incident to standard ARGUS Incident Record"""
        props = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        coords = geometry.get("coordinates", [-118.2437, 34.0522])
        
        lon = float(coords[0]) if len(coords) > 0 else -118.2437
        lat = float(coords[1]) if len(coords) > 1 else 34.0522

        return {
            "incident_id": props.get("call_id", f"CAD-{random.randint(1000, 9999)}"),
            "timestamp": props.get("call_time", datetime.utcnow().isoformat() + "Z"),
            "sector_code": props.get("sector", "SEC-01"),
            "sector_name": props.get("district", "Downtown Central"),
            "crime_type": props.get("event_type", "Suspicious Activity"),
            "severity_score": props.get("priority_code", 50),
            "weapon_type": props.get("weapons_flag", "None"),
            "premise_type": props.get("premise_type", "Public Thoroughfare"),
            "latitude": lat,
            "longitude": lon,
            "status": "CAD Dispatched",
            "source": "GEOJSON_CAD_FEED"
        }
