import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    SURVEILLANCE_PORT: int = int(os.getenv("SURVEILLANCE_PORT", "8002"))
    SURVEILLANCE_HOST: str = "0.0.0.0"
    
    CONFIDENCE_THRESHOLD: float = float(os.getenv("RECON_CONFIDENCE_THRESHOLD", "0.75"))
    AUTO_VERIFY_THRESHOLD: float = float(os.getenv("HITL_AUTO_VERIFY_THRESHOLD", "0.92"))
    
    POI_DB_PATH: Path = Path(__file__).resolve().parents[3] / "data" / "intelligence" / "persons_of_interest.json"
    PROFILES_3D_PATH: Path = Path(__file__).resolve().parents[3] / "data" / "intelligence" / "3d_facial_profiles.json"

settings = Settings()
