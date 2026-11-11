import logging
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from .config import settings
    from .model_trainer import CrimeSeverityModelEngine
    from .hotspot_forecaster import SpatialHotspotForecaster
except ImportError:
    from config import settings
    from model_trainer import CrimeSeverityModelEngine
    from hotspot_forecaster import SpatialHotspotForecaster

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("argus-prediction-service")

app = FastAPI(
    title="ARGUS Crime Prediction & Hotspot Service",
    version="2.4.0",
    description="Microservice providing real-time crime severity classification, regression, and spatial hotspot forecasting."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = CrimeSeverityModelEngine(settings.DATA_PATH, settings.MODEL_DIR)
hotspot_engine = SpatialHotspotForecaster(settings.DATA_PATH)

@app.on_event("startup")
def startup_event():
    logger.info("Initializing ML models...")
    if not engine.load():
        logger.info("Training initial model from local municipal dataset...")
        engine.train()

class PredictionRequest(BaseModel):
    crime_type: str
    premise_type: str
    weapon_type: Optional[str] = "None"
    victim_age: Optional[int] = 30
    latitude: Optional[float] = 34.0522
    longitude: Optional[float] = -118.2437

@app.get("/health")
def health():
    return {
        "status": "HEALTHY",
        "service": "argus-crime-prediction",
        "model_loaded": engine.clf is not None,
        "metrics": engine.metrics
    }

@app.post("/predict/severity")
def predict_incident_severity(req: PredictionRequest):
    try:
        result = engine.predict(
            crime_type=req.crime_type,
            premise_type=req.premise_type,
            weapon_type=req.weapon_type or "None",
            victim_age=req.victim_age or 30,
            lat=req.latitude or 34.0522,
            lon=req.longitude or -118.2437
        )
        return result
    except Exception as exc:
        logger.error(f"Prediction failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/predict/batch")
def predict_batch(records: List[PredictionRequest]):
    results = []
    for r in records:
        pred = engine.predict(
            crime_type=r.crime_type,
            premise_type=r.premise_type,
            weapon_type=r.weapon_type or "None",
            victim_age=r.victim_age or 30,
            lat=r.latitude or 34.0522,
            lon=r.longitude or -118.2437
        )
        results.append(pred)
    return {"batch_count": len(results), "predictions": results}

@app.get("/predict/hotspots")
def get_spatial_hotspots():
    hotspots = hotspot_engine.compute_hotspots()
    return {"total_hotspots": len(hotspots), "hotspots": hotspots}

@app.post("/train")
def trigger_retraining():
    logger.info("Retraining model...")
    engine.train()
    return {"status": "SUCCESS", "metrics": engine.metrics}

@app.get("/metrics")
def get_model_metrics():
    return engine.metrics

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.crime-prediction-service.src.main:app", host=settings.PREDICTION_HOST, port=settings.PREDICTION_PORT, reload=True)
