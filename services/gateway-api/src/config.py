import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    GATEWAY_PORT: int = int(os.getenv("GATEWAY_PORT", "8000"))
    GATEWAY_HOST: str = os.getenv("GATEWAY_HOST", "0.0.0.0")
    
    PREDICTION_SERVICE_URL: str = os.getenv("PREDICTION_SERVICE_URL", "http://localhost:8001")
    SURVEILLANCE_SERVICE_URL: str = os.getenv("SURVEILLANCE_SERVICE_URL", "http://localhost:8002")
    INGESTION_SERVICE_URL: str = os.getenv("INGESTION_SERVICE_URL", "http://localhost:8003")
    ONTOLOGY_SERVICE_URL: str = os.getenv("ONTOLOGY_SERVICE_URL", "http://localhost:8004")
    
    DATA_DIR: Path = Path(__file__).resolve().parents[3] / "data"

settings = Settings()
