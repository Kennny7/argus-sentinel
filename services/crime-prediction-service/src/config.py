import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    PREDICTION_PORT: int = int(os.getenv("PREDICTION_PORT", "8001"))
    PREDICTION_HOST: str = "0.0.0.0"
    DATA_PATH: Path = Path(__file__).resolve().parents[3] / "data" / "crime_records" / "crime_settlement_data.json"
    MODEL_DIR: Path = Path(__file__).resolve().parent / "artifacts"

settings = Settings()
