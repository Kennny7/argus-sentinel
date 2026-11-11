import json
import logging
from pathlib import Path
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error
import joblib

logger = logging.getLogger("argus-model-trainer")

class CrimeSeverityModelEngine:
    def __init__(self, data_path: Path, artifacts_dir: Path):
        self.data_path = data_path
        self.artifacts_dir = artifacts_dir
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        self.clf = None
        self.reg = None
        self.encoder = None
        self.scaler = None
        self.metrics = {}

    def extract_features(self, record: dict):
        crime = str(record.get("crime_type", "Unknown"))
        premise = str(record.get("premise_type", "Unknown"))
        weapon = str(record.get("weapon_type", "None"))
        victim_age = float(record.get("victim_age", 30))
        lat = float(record.get("latitude", 34.0522))
        lon = float(record.get("longitude", -118.2437))
        return [crime, premise, weapon], [victim_age, lat, lon]

    def train(self):
        if not self.data_path.exists():
            logger.warning(f"Data file not found at {self.data_path}. Using synthetic initialization.")
            return

        with open(self.data_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        cat_list = []
        num_list = []
        y_score = []
        y_tier = []

        for r in records:
            cat, num = self.extract_features(r)
            cat_list.append(cat)
            num_list.append(num)
            y_score.append(float(r.get("severity_score", 50)))
            y_tier.append(str(r.get("severity_tier", "Medium")))

        self.encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        cat_encoded = self.encoder.fit_transform(cat_list)

        self.scaler = StandardScaler()
        num_scaled = self.scaler.fit_transform(num_list)

        X = np.hstack([cat_encoded, num_scaled])
        y_reg = np.array(y_score)
        y_clf = np.array(y_tier)

        X_train, X_test, y_reg_train, y_reg_test, y_clf_train, y_clf_test = train_test_split(
            X, y_reg, y_clf, test_size=0.2, random_state=42
        )

        self.clf = GradientBoostingClassifier(n_estimators=60, max_depth=4, random_state=42)
        self.clf.fit(X_train, y_clf_train)

        self.reg = RandomForestRegressor(n_estimators=50, random_state=42)
        self.reg.fit(X_train, y_reg_train)

        y_pred_clf = self.clf.predict(X_test)
        y_pred_reg = self.reg.predict(X_test)

        acc = accuracy_score(y_clf_test, y_pred_clf)
        f1 = f1_score(y_clf_test, y_pred_clf, average="weighted")
        mse = mean_squared_error(y_reg_test, y_pred_reg)

        self.metrics = {
            "classification_accuracy": round(float(acc), 4),
            "classification_f1_score": round(float(f1), 4),
            "score_rmse": round(float(np.sqrt(mse)), 4),
            "samples_trained": len(records),
            "feature_dimension": int(X.shape[1]),
            "algorithm": "GradientBoosting + RandomForest Ensembles"
        }

        # Save artifacts
        joblib.dump(self.clf, self.artifacts_dir / "severity_classifier.joblib")
        joblib.dump(self.reg, self.artifacts_dir / "severity_regressor.joblib")
        joblib.dump(self.encoder, self.artifacts_dir / "onehot_encoder.joblib")
        joblib.dump(self.scaler, self.artifacts_dir / "standard_scaler.joblib")
        with open(self.artifacts_dir / "metrics.json", "w") as f:
            json.dump(self.metrics, f, indent=2)

        logger.info(f"Model training successful. Metrics: {self.metrics}")

    def load(self):
        try:
            self.clf = joblib.load(self.artifacts_dir / "severity_classifier.joblib")
            self.reg = joblib.load(self.artifacts_dir / "severity_regressor.joblib")
            self.encoder = joblib.load(self.artifacts_dir / "onehot_encoder.joblib")
            self.scaler = joblib.load(self.artifacts_dir / "standard_scaler.joblib")
            with open(self.artifacts_dir / "metrics.json", "r") as f:
                self.metrics = json.load(f)
            return True
        except Exception:
            return False

    def predict(self, crime_type: str, premise_type: str, weapon_type: str = "None", victim_age: int = 30, lat: float = 34.0522, lon: float = -118.2437):
        if not self.clf or not self.encoder:
            # Automatic train if missing
            self.train()

        cat = [[str(crime_type), str(premise_type), str(weapon_type)]]
        num = [[float(victim_age), float(lat), float(lon)]]

        cat_encoded = self.encoder.transform(cat)
        num_scaled = self.scaler.transform(num)
        X = np.hstack([cat_encoded, num_scaled])

        score = float(self.reg.predict(X)[0])
        tier = str(self.clf.predict(X)[0])
        probabilities = self.clf.predict_proba(X)[0]
        classes = self.clf.classes_.tolist()

        class_confidence = {cls: round(float(prob), 4) for cls, prob in zip(classes, probabilities)}
        max_conf = max(probabilities)

        return {
            "predicted_severity_score": round(max(10.0, min(100.0, score)), 2),
            "severity_tier": tier,
            "confidence": round(float(max_conf), 4),
            "class_distribution": class_confidence,
            "response_protocol": "IMMEDIATE_TACTICAL_DEPLOYMENT" if tier in ["High", "Critical"] else "DISPATCH_PATROL_MONITOR"
        }
