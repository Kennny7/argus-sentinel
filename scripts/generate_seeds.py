"""
ARGUS Data Seed Generator
Generates clean, realistic municipal crime records, biometric POI dossiers,
and 3D facial landmark mesh structures with ZERO null values.
"""
import json
import math
import random
from datetime import datetime, timedelta

random.seed(42)

# 1. Crime Settlement Data Generator
SECTORS = [
    {"name": "Downtown Central", "code": "SEC-01", "lat_center": 34.0522, "lon_center": -118.2437},
    {"name": "West Harbor District", "code": "SEC-02", "lat_center": 33.7432, "lon_center": -118.2673},
    {"name": "North Industrial Ring", "code": "SEC-03", "lat_center": 34.1808, "lon_center": -118.3090},
    {"name": "University Heights", "code": "SEC-04", "lat_center": 34.0689, "lon_center": -118.4452},
    {"name": "East Tech Corridor", "code": "SEC-05", "lat_center": 34.1478, "lon_center": -118.1445},
    {"name": "South Transit Hub", "code": "SEC-06", "lat_center": 33.9416, "lon_center": -118.4085},
    {"name": "Metro Core Square", "code": "SEC-07", "lat_center": 34.0488, "lon_center": -118.2518}
]

CRIME_TYPES = [
    {"name": "Vehicle Theft", "base_severity": 45, "tier": "Medium", "weapon": "None"},
    {"name": "Aggravated Assault", "base_severity": 82, "tier": "High", "weapon": "Blunt Object"},
    {"name": "Armed Robbery", "base_severity": 91, "tier": "Critical", "weapon": "Firearm"},
    {"name": "Commercial Burglary", "base_severity": 58, "tier": "Medium", "weapon": "Pry Tool"},
    {"name": "Cyber Infrastructure Intrusion", "base_severity": 74, "tier": "High", "weapon": "Hardware Injector"},
    {"name": "Narcotics Distribution", "base_severity": 68, "tier": "Medium", "weapon": "Concealed Weapon"},
    {"name": "Weapons Trafficking", "base_severity": 95, "tier": "Critical", "weapon": "Automatic Rifle"},
    {"name": "Financial Extortion", "base_severity": 62, "tier": "Medium", "weapon": "Digital Exploit"},
    {"name": "Vandalism / Infrastructure Tampering", "base_severity": 35, "tier": "Low", "weapon": "Tool Kit"}
]

PREMISES = ["Public Transit Station", "Commercial Plaza", "Industrial Warehouse", "Banking Complex", "Street Intersection", "Parking Structure", "Data Center Facility"]
STATUSES = ["Active Alert", "Unit Dispatched", "Under Investigation", "Contained", "Resolved"]

incidents = []
base_time = datetime(2026, 8, 1, 0, 0, 0)

for i in range(1, 251):
    sec = random.choice(SECTORS)
    crm = random.choice(CRIME_TYPES)
    jitter_lat = (random.random() - 0.5) * 0.04
    jitter_lon = (random.random() - 0.5) * 0.04
    lat = round(sec["lat_center"] + jitter_lat, 6)
    lon = round(sec["lon_center"] + jitter_lon, 6)
    
    time_offset = timedelta(
        days=random.randint(0, 100),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )
    incident_time = base_time + time_offset
    sev_score = min(100, max(10, crm["base_severity"] + random.randint(-8, 8)))
    
    tier = "Low"
    if sev_score >= 85:
        tier = "Critical"
    elif sev_score >= 70:
        tier = "High"
    elif sev_score >= 45:
        tier = "Medium"
        
    incidents.append({
        "incident_id": f"INC-2026-{i:04d}",
        "timestamp": incident_time.isoformat() + "Z",
        "sector_code": sec["code"],
        "sector_name": sec["name"],
        "crime_type": crm["name"],
        "severity_score": sev_score,
        "severity_tier": tier,
        "weapon_type": crm["weapon"],
        "premise_type": random.choice(PREMISES),
        "latitude": lat,
        "longitude": lon,
        "victim_age": random.randint(18, 72),
        "victim_gender": random.choice(["M", "F", "Non-Binary"]),
        "status": random.choice(STATUSES),
        "responding_unit": f"UNIT-{random.randint(101, 149)}",
        "response_eta_minutes": random.randint(2, 14),
        "cctv_coverage": random.choice(["HIGH", "MEDIUM", "LOW"]),
        "surveillance_camera_id": f"CAM-{sec['code']}-{random.randint(1, 8):02d}"
    })

with open("data/crime_records/crime_settlement_data.json", "w") as f:
    json.dump(incidents, f, indent=2)

# 2. Persons of Interest (Biometric & Reconnaissance DB)
def generate_unit_vector(dim=128):
    vec = [round(random.gauss(0, 1), 5) for _ in range(dim)]
    norm = math.sqrt(sum(v*v for v in vec))
    return [round(v / norm, 5) for v in vec]

POI_RECORDS = [
    {
        "subject_id": "POI-8821",
        "full_name": "Marcus Vance",
        "alias": "Cipher",
        "designation": "AI-FIRST BACKEND ENGINEER / EXFILTRATION OPERATOR",
        "risk_level": "High",
        "threat_rating": 84,
        "age": 34,
        "gender": "Male",
        "height_cm": 182,
        "weight_kg": 78,
        "biometric_embedding": generate_unit_vector(128),
        "image_reference": "assets/surveillance/cctv_target_lock_sample1.jpeg",
        "avatar_crop": "assets/surveillance/cctv_target_lock_sample2.jpeg",
        "social_footprint": {
            "github": "https://github.com/vance-cipher-core",
            "linkedin": "https://linkedin.com/in/marcus-vance-telemetry",
            "x": "https://x.com/cipher_vance",
            "telegram": "@cipher_mv"
        },
        "skills_and_stats": {
            "dsa_rating": "Elite",
            "system_design": "Distributed Architecture",
            "rag_pipelines": "Advanced",
            "llm_agents": "Autonomous Swarm",
            "salary_benchmark": "70 LPA+",
            "salary_hike_stat": "150%"
        },
        "known_locations": ["Downtown Central Metro", "East Tech Corridor Node 4"],
        "criminal_record": ["Unauthorized Federal Data Access (2024)", "Autonomous Drone Relaying (2025)"],
        "verification_status": "FLAGGED_FOR_HUMAN_CONFIRMATION",
        "last_observed_timestamp": "2026-08-13T12:57:01Z",
        "last_observed_camera": "CAM-SEC-01-04",
        "confidence_score": 0.89
    },
    {
        "subject_id": "POI-9043",
        "full_name": "Elena Rostova",
        "alias": "Valkyrie",
        "designation": "TACTICAL COMMUNICATIONS SPECIALIST",
        "risk_level": "Critical",
        "threat_rating": 93,
        "age": 29,
        "gender": "Female",
        "height_cm": 172,
        "weight_kg": 61,
        "biometric_embedding": generate_unit_vector(128),
        "image_reference": "assets/surveillance/cctv_target_lock_sample1.jpeg",
        "avatar_crop": "assets/surveillance/cctv_target_lock_sample1.jpeg",
        "social_footprint": {
            "github": "https://github.com/valkyrie-mesh",
            "linkedin": "https://linkedin.com/in/elena-rostova-rf",
            "x": "https://x.com/valk_signals",
            "telegram": "@valkyrie_mesh"
        },
        "skills_and_stats": {
            "dsa_rating": "Expert",
            "system_design": "Mesh Radios & SDR",
            "rag_pipelines": "Tactical Knowledge Graphs",
            "llm_agents": "Real-Time Intercept",
            "salary_benchmark": "65 LPA+",
            "salary_hike_stat": "140%"
        },
        "known_locations": ["West Harbor Docks", "Metro Core Square"],
        "criminal_record": ["Signal Jamming Equipment Transport (2025)"],
        "verification_status": "VERIFIED_THREAT",
        "last_observed_timestamp": "2026-08-13T12:45:10Z",
        "last_observed_camera": "CAM-SEC-02-01",
        "confidence_score": 0.94
    },
    {
        "subject_id": "POI-3312",
        "full_name": "Raymond Cruz",
        "alias": "Specter",
        "designation": "CONTRABAND LOGISTICS COORDINATOR",
        "risk_level": "Critical",
        "threat_rating": 96,
        "age": 42,
        "gender": "Male",
        "height_cm": 188,
        "weight_kg": 90,
        "biometric_embedding": generate_unit_vector(128),
        "image_reference": "assets/surveillance/cctv_target_lock_sample2.jpeg",
        "avatar_crop": "assets/surveillance/cctv_target_lock_sample2.jpeg",
        "social_footprint": {
            "github": "https://github.com/cruz-logistics-net",
            "linkedin": "https://linkedin.com/in/raymond-cruz-supply",
            "x": "https://x.com/cruz_specter",
            "telegram": "@specter_cruz"
        },
        "skills_and_stats": {
            "dsa_rating": "Proficient",
            "system_design": "High-Throughput Supply Chain",
            "rag_pipelines": "Custom Freight Indexing",
            "llm_agents": "Route Optimization",
            "salary_benchmark": "80 LPA+",
            "salary_hike_stat": "160%"
        },
        "known_locations": ["North Industrial Ring", "South Transit Hub"],
        "criminal_record": ["Armed Port Robbery (2022)", "Weapons Distribution (2024)"],
        "verification_status": "HIGH_PRIORITY_WARRANT",
        "last_observed_timestamp": "2026-08-13T11:30:22Z",
        "last_observed_camera": "CAM-SEC-03-05",
        "confidence_score": 0.96
    },
    {
        "subject_id": "POI-5520",
        "full_name": "Sophia Chen",
        "alias": "Apex",
        "designation": "FINANCIAL LEDGER EXPLOITATION SPECIALIST",
        "risk_level": "Medium",
        "threat_rating": 65,
        "age": 27,
        "gender": "Female",
        "height_cm": 165,
        "weight_kg": 54,
        "biometric_embedding": generate_unit_vector(128),
        "image_reference": "assets/surveillance/cctv_target_lock_sample1.jpeg",
        "avatar_crop": "assets/surveillance/cctv_target_lock_sample1.jpeg",
        "social_footprint": {
            "github": "https://github.com/sophia-chen-ledger",
            "linkedin": "https://linkedin.com/in/sophia-chen-quant",
            "x": "https://x.com/chen_apex",
            "telegram": "@apex_sophia"
        },
        "skills_and_stats": {
            "dsa_rating": "Master",
            "system_design": "Low-Latency Crypto Engine",
            "rag_pipelines": "SEC Filings Parsing",
            "llm_agents": "Arbitrage Bots",
            "salary_benchmark": "55 LPA+",
            "salary_hike_stat": "120%"
        },
        "known_locations": ["East Tech Corridor", "University Heights"],
        "criminal_record": ["Corporate Wire Fraud (2025)"],
        "verification_status": "FLAGGED_FOR_HUMAN_CONFIRMATION",
        "last_observed_timestamp": "2026-08-13T10:15:40Z",
        "last_observed_camera": "CAM-SEC-05-02",
        "confidence_score": 0.81
    },
    {
        "subject_id": "POI-1104",
        "full_name": "Jordan Blake",
        "alias": "Viper",
        "designation": "PERIMETER BREACH TECHNICIAN",
        "risk_level": "High",
        "threat_rating": 79,
        "age": 38,
        "gender": "Male",
        "height_cm": 179,
        "weight_kg": 81,
        "biometric_embedding": generate_unit_vector(128),
        "image_reference": "assets/surveillance/cctv_target_lock_sample2.jpeg",
        "avatar_crop": "assets/surveillance/cctv_target_lock_sample2.jpeg",
        "social_footprint": {
            "github": "https://github.com/blake-viper-exploit",
            "linkedin": "https://linkedin.com/in/jordan-blake-sec",
            "x": "https://x.com/viper_blake",
            "telegram": "@viper_blake"
        },
        "skills_and_stats": {
            "dsa_rating": "Advanced",
            "system_design": "SCADA / PLC Networks",
            "rag_pipelines": "CVE Automated Synthesizer",
            "llm_agents": "Penetration Agents",
            "salary_benchmark": "60 LPA+",
            "salary_hike_stat": "130%"
        },
        "known_locations": ["South Transit Hub", "Downtown Central"],
        "criminal_record": ["Power Substation Tampering (2024)"],
        "verification_status": "CONFIRMED_ACTIVE",
        "last_observed_timestamp": "2026-08-13T09:44:18Z",
        "last_observed_camera": "CAM-SEC-06-03",
        "confidence_score": 0.91
    }
]

with open("data/intelligence/persons_of_interest.json", "w") as f:
    json.dump(POI_RECORDS, f, indent=2)

# 3. 3D Facial Mesh Generation (Canonical 3D landmark points and mesh connectivity)
def generate_3d_face_profile(subject_id, full_name):
    # Generates standard anthropometric 3D face coordinates (x, y, z)
    landmarks = []
    # Ring contours for 3D facial topology
    # Forehead, eyes, nose, lips, jawline
    features = [
        {"name": "nose_tip", "coords": [0.0, 0.05, 0.42]},
        {"name": "nose_bridge_top", "coords": [0.0, 0.32, 0.30]},
        {"name": "nose_bridge_mid", "coords": [0.0, 0.18, 0.36]},
        {"name": "chin_bottom", "coords": [0.0, -0.72, 0.10]},
        {"name": "chin_menton", "coords": [0.0, -0.60, 0.18]},
        {"name": "left_eye_inner", "coords": [-0.18, 0.30, 0.18]},
        {"name": "left_eye_outer", "coords": [-0.52, 0.30, 0.02]},
        {"name": "left_eye_top", "coords": [-0.35, 0.36, 0.12]},
        {"name": "left_eye_bottom", "coords": [-0.35, 0.24, 0.10]},
        {"name": "right_eye_inner", "coords": [0.18, 0.30, 0.18]},
        {"name": "right_eye_outer", "coords": [0.52, 0.30, 0.02]},
        {"name": "right_eye_top", "coords": [0.35, 0.36, 0.12]},
        {"name": "right_eye_bottom", "coords": [0.35, 0.24, 0.10]},
        {"name": "left_eyebrow_inner", "coords": [-0.15, 0.44, 0.22]},
        {"name": "left_eyebrow_outer", "coords": [-0.55, 0.46, 0.05]},
        {"name": "right_eyebrow_inner", "coords": [0.15, 0.44, 0.22]},
        {"name": "right_eyebrow_outer", "coords": [0.55, 0.46, 0.05]},
        {"name": "mouth_left_corner", "coords": [-0.32, -0.28, 0.12]},
        {"name": "mouth_right_corner", "coords": [0.32, -0.28, 0.12]},
        {"name": "mouth_upper_lip_center", "coords": [0.0, -0.22, 0.24]},
        {"name": "mouth_lower_lip_center", "coords": [0.0, -0.36, 0.22]},
        {"name": "left_cheekbone", "coords": [-0.62, 0.02, -0.05]},
        {"name": "right_cheekbone", "coords": [0.62, 0.02, -0.05]},
        {"name": "left_jaw_angle", "coords": [-0.58, -0.42, -0.20]},
        {"name": "right_jaw_angle", "coords": [0.58, -0.42, -0.20]},
        {"name": "forehead_center", "coords": [0.0, 0.68, 0.16]},
        {"name": "forehead_left", "coords": [-0.45, 0.64, 0.02]},
        {"name": "forehead_right", "coords": [0.45, 0.64, 0.02]}
    ]
    
    # Detailed wireframe grid vertices
    vertices = []
    for f in features:
        vertices.append({
            "landmark": f["name"],
            "x": round(f["coords"][0], 4),
            "y": round(f["coords"][1], 4),
            "z": round(f["coords"][2], 4)
        })
    
    # Generate 120 dense wireframe mesh point cloud vertices
    for u in range(-4, 5):
        for v in range(-6, 7):
            x = u * 0.14
            y = v * 0.12
            r2 = x*x + y*y
            if r2 <= 0.64:
                z = math.sqrt(max(0.01, 0.64 - r2)) * 0.55 - 0.08
                vertices.append({
                    "landmark": f"dense_grid_{u}_{v}",
                    "x": round(x, 4),
                    "y": round(y, 4),
                    "z": round(z, 4)
                })

    return {
        "subject_id": subject_id,
        "full_name": full_name,
        "reconstruction_timestamp": "2026-08-13T12:57:05Z",
        "mesh_vertex_count": len(vertices),
        "pose_angles": {"pitch_deg": -4.2, "yaw_deg": 1.8, "roll_deg": -0.6},
        "depth_confidence": 0.962,
        "facial_symmetry_score": 0.941,
        "interpupillary_distance_mm": 63.4,
        "biometric_hash": f"SHA256-{subject_id}-468MESH",
        "vertices": vertices
    }

profiles_3d = {}
for p in POI_RECORDS:
    profiles_3d[p["subject_id"]] = generate_3d_face_profile(p["subject_id"], p["full_name"])

with open("data/intelligence/3d_facial_profiles.json", "w") as f:
    json.dump(profiles_3d, f, indent=2)

# 4. Urban Crime Ontology Generator
ontology = {
    "ontology_name": "ARGUS Urban Crime & Threat Ontology",
    "version": "2.4.0",
    "classes": [
        "PersonOfInterest",
        "CrimeIncident",
        "SurveillanceSensor",
        "WeaponSystem",
        "UrbanSector",
        "SyndicateNetwork",
        "TacticalResponseUnit"
    ],
    "relationships": [
        {"subject": "PersonOfInterest", "predicate": "INVOLVED_IN", "object": "CrimeIncident"},
        {"subject": "CrimeIncident", "predicate": "LOCATED_IN", "object": "UrbanSector"},
        {"subject": "SurveillanceSensor", "predicate": "MONITORS_SECTOR", "object": "UrbanSector"},
        {"subject": "SurveillanceSensor", "predicate": "CAPTURED_TARGET", "object": "PersonOfInterest"},
        {"subject": "PersonOfInterest", "predicate": "AFFILIATED_WITH", "object": "SyndicateNetwork"},
        {"subject": "CrimeIncident", "predicate": "UTILIZED_WEAPON", "object": "WeaponSystem"},
        {"subject": "TacticalResponseUnit", "predicate": "DISPATCHED_TO", "object": "CrimeIncident"}
    ],
    "knowledge_triples": [
        {"subject": "POI-8821", "predicate": "INVOLVED_IN", "object": "INC-2026-0012"},
        {"subject": "POI-8821", "predicate": "AFFILIATED_WITH", "object": "DarkFiber Syndicate"},
        {"subject": "CAM-SEC-01-04", "predicate": "CAPTURED_TARGET", "object": "POI-8821"},
        {"subject": "INC-2026-0012", "predicate": "LOCATED_IN", "object": "SEC-01"},
        {"subject": "POI-9043", "predicate": "INVOLVED_IN", "object": "INC-2026-0045"},
        {"subject": "POI-9043", "predicate": "AFFILIATED_WITH", "object": "BlackWave Logistics"},
        {"subject": "CAM-SEC-02-01", "predicate": "CAPTURED_TARGET", "object": "POI-9043"},
        {"subject": "POI-3312", "predicate": "AFFILIATED_WITH", "object": "BlackWave Logistics"},
        {"subject": "UNIT-108", "predicate": "DISPATCHED_TO", "object": "INC-2026-0012"}
    ],
    "syndicates": [
        {"name": "DarkFiber Syndicate", "threat_tier": "Critical", "focus": "Critical Cyber & Grid Infiltration"},
        {"name": "BlackWave Logistics", "threat_tier": "Critical", "focus": "Contraband & Illegal Munitions"},
        {"name": "Apex Ledger Syndicate", "threat_tier": "High", "focus": "Autonomous Financial Wire Fraud"}
    ]
}

with open("data/ontology/urban_crime_ontology.json", "w") as f:
    json.dump(ontology, f, indent=2)

print("Data generation complete. Zero null values generated across all records.")
