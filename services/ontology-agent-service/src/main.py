import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from .config import settings
    from .graph_engine import CrimeOntologyGraphEngine
    from .agent_reasoner import AutonomousCrimeAgent
except ImportError:
    from config import settings
    from graph_engine import CrimeOntologyGraphEngine
    from agent_reasoner import AutonomousCrimeAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("argus-ontology-service")

app = FastAPI(
    title="ARGUS Crime Ontology & Agentic Reasoning Service",
    version="2.4.0",
    description="Knowledge graph traversal and autonomous LLM-driven crime investigation agent."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph_engine = CrimeOntologyGraphEngine(settings.ONTOLOGY_DATA_PATH)
agent = AutonomousCrimeAgent(graph_engine)

class InvestigationRequest(BaseModel):
    subject_id: str
    sector: Optional[str] = "Downtown Central"

@app.get("/health")
def health():
    return {
        "status": "HEALTHY",
        "service": "argus-ontology-agent",
        "nodes_loaded": len(graph_engine.graph.nodes),
        "edges_loaded": len(graph_engine.graph.edges),
        "llm_target": settings.LLM_BASE_URL
    }

@app.get("/graph/schema")
def get_graph_schema():
    return graph_engine.get_full_graph_data()

@app.get("/graph/entity/{entity_id}")
def get_entity_connections(entity_id: str):
    return graph_engine.query_entity_connections(entity_id)

@app.post("/agent/investigate")
async def run_investigation(req: InvestigationRequest):
    briefing = await agent.investigate_target(req.subject_id, req.sector or "Downtown Central")
    return briefing

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.ontology-agent-service.src.main:app", host=settings.ONTOLOGY_HOST, port=settings.ONTOLOGY_PORT, reload=True)
