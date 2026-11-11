import json
from pathlib import Path
from typing import Dict, Any, List
import networkx as nx

class CrimeOntologyGraphEngine:
    def __init__(self, ontology_path: Path):
        self.ontology_path = ontology_path
        self.graph = nx.MultiDiGraph()
        self.raw_data: Dict[str, Any] = {}
        self.build_graph()

    def build_graph(self):
        if not self.ontology_path.exists():
            return
        with open(self.ontology_path, "r", encoding="utf-8") as f:
            self.raw_data = json.load(f)

        self.graph.clear()
        triples = self.raw_data.get("knowledge_triples", [])
        for t in triples:
            sub = t.get("subject")
            pred = t.get("predicate")
            obj = t.get("object")
            if sub and pred and obj:
                self.graph.add_edge(sub, obj, predicate=pred)

    def query_entity_connections(self, entity_id: str) -> Dict[str, Any]:
        self.build_graph()
        if entity_id not in self.graph:
            return {"entity": entity_id, "exists": False, "neighbors": []}

        neighbors = []
        # Outgoing edges
        for _, neighbor, data in self.graph.out_edges(entity_id, data=True):
            neighbors.append({
                "direction": "OUTGOING",
                "target": neighbor,
                "predicate": data.get("predicate", "RELATED_TO")
            })
        # Incoming edges
        for source, _, data in self.graph.in_edges(entity_id, data=True):
            neighbors.append({
                "direction": "INCOMING",
                "source": source,
                "predicate": data.get("predicate", "RELATED_TO")
            })

        return {
            "entity": entity_id,
            "exists": True,
            "connection_count": len(neighbors),
            "connections": neighbors
        }

    def get_full_graph_data(self) -> Dict[str, Any]:
        self.build_graph()
        return self.raw_data
