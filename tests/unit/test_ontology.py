import sys
from pathlib import Path
import pytest

root_dir = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root_dir / "services" / "ontology-agent-service" / "src"))

from graph_engine import CrimeOntologyGraphEngine

def test_ontology_graph_traversal():
    ontology_path = root_dir / "data" / "ontology" / "urban_crime_ontology.json"
    engine = CrimeOntologyGraphEngine(ontology_path)
    
    assert len(engine.graph.nodes) > 0
    assert len(engine.graph.edges) > 0
    
    result = engine.query_entity_connections("POI-8821")
    assert result["exists"] is True
    assert result["connection_count"] > 0
    
    # Check non-existent node
    absent = engine.query_entity_connections("POI-NON-EXISTENT")
    assert absent["exists"] is False
