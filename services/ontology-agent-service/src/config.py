import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    ONTOLOGY_PORT: int = int(os.getenv("ONTOLOGY_PORT", "8004"))
    ONTOLOGY_HOST: str = "0.0.0.0"
    
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "google/gemma-4-E4B-it-qat-q4_0-gguf:Q4_0")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "http://10.210.8.63:8080/v1")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "not-needed")
    LLM_ENABLE_THINKING: bool = os.getenv("LLM_ENABLE_THINKING", "true").lower() == "true"
    
    ONTOLOGY_DATA_PATH: Path = Path(__file__).resolve().parents[3] / "data" / "ontology" / "urban_crime_ontology.json"

settings = Settings()
