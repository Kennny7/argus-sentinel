import csv
import json
from pathlib import Path
from typing import List, Dict, Any

class BatchDatasetLoader:
    @staticmethod
    def load_csv(csv_path: Path) -> List[Dict[str, Any]]:
        records = []
        if not csv_path.exists():
            return records
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
        return records

    @staticmethod
    def load_json(json_path: Path) -> List[Dict[str, Any]]:
        if not json_path.exists():
            return []
        with open(json_path, mode="r", encoding="utf-8") as f:
            return json.load(f)
