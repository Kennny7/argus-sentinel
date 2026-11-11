import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    INGESTION_PORT: int = int(os.getenv("INGESTION_PORT", "8003"))
    INGESTION_HOST: str = "0.0.0.0"
    
    GATEWAY_URL: str = os.getenv("GATEWAY_SERVICE_URL", "http://localhost:8000")
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_TOPIC_INCIDENTS: str = os.getenv("KAFKA_TOPIC_INCIDENTS", "argus.incidents.raw")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

settings = Settings()
