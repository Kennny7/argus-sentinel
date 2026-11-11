import sys
from pathlib import Path
import pytest

root_dir = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root_dir / "services" / "crime-prediction-service" / "src"))

from model_trainer import CrimeSeverityModelEngine
from hotspot_forecaster import SpatialHotspotForecaster

def test_model_training_and_prediction(tmp_path):
    data_path = root_dir / "data" / "crime_records" / "crime_settlement_data.json"
    engine = CrimeSeverityModelEngine(data_path, tmp_path)
    engine.train()
    
    assert engine.clf is not None
    assert engine.reg is not None
    assert "classification_accuracy" in engine.metrics
    
    pred = engine.predict("Armed Robbery", "Commercial Plaza", "Firearm", 35)
    assert 10 <= pred["predicted_severity_score"] <= 100
    assert pred["severity_tier"] in ["Low", "Medium", "High", "Critical"]
    assert 0.0 <= pred["confidence"] <= 1.0

def test_hotspot_computation():
    data_path = root_dir / "data" / "crime_records" / "crime_settlement_data.json"
    forecaster = SpatialHotspotForecaster(data_path)
    hotspots = forecaster.compute_hotspots()
    
    assert len(hotspots) > 0
    first = hotspots[0]
    assert "sector_name" in first
    assert "composite_risk_rating" in first
    assert first["composite_risk_rating"] >= 0
