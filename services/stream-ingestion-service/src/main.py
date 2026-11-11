import logging
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from .config import settings
    from .connectors.kafka_connector import KafkaStreamConnector
    from .connectors.redis_connector import RedisStreamConnector
    from .connectors.geojson_stream import GeoJSONStreamParser
    from .connectors.batch_loader import BatchDatasetLoader
except ImportError:
    from config import settings
    from connectors.kafka_connector import KafkaStreamConnector
    from connectors.redis_connector import RedisStreamConnector
    from connectors.geojson_stream import GeoJSONStreamParser
    from connectors.batch_loader import BatchDatasetLoader

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("argus-ingestion-service")

app = FastAPI(
    title="ARGUS Multi-Source Stream Ingestion Service",
    version="2.4.0",
    description="Multi-protocol stream ingestion gateway supporting Kafka, Redis Streams, RTSP telemetry, and GeoJSON CAD events."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

kafka = KafkaStreamConnector(settings.KAFKA_BOOTSTRAP_SERVERS, settings.KAFKA_TOPIC_INCIDENTS)
redis_conn = RedisStreamConnector(settings.REDIS_URL)

@app.on_event("startup")
def startup():
    kafka.connect()

@app.get("/health")
def health():
    return {
        "status": "HEALTHY",
        "service": "argus-stream-ingestion",
        "kafka_connected": kafka.is_connected,
        "supported_protocols": ["Kafka", "Redis Streams", "GeoJSON CAD", "RTSP Simulation", "CSV Batch"]
    }

class StreamEventPayload(BaseModel):
    source_protocol: str  # "kafka", "redis", "cad_geojson", "cctv_rtsp"
    payload: Dict[str, Any]

@app.post("/ingest/event")
def ingest_event(event: StreamEventPayload):
    proto = event.source_protocol.lower()
    data = event.payload

    if "geojson" in proto:
        standardized = GeoJSONStreamParser.parse_cad_dispatch(data)
    else:
        standardized = data

    kafka.produce_event(standardized)
    redis_conn.publish_telemetry(standardized)

    return {
        "status": "ACCEPTED",
        "protocol": event.source_protocol,
        "standardized_record": standardized
    }

@app.get("/ingest/status")
def ingestion_status():
    return {
        "active_pipelines": [
            {"name": "Kafka / Redpanda Ingest", "status": "LISTENING", "topic": settings.KAFKA_TOPIC_INCIDENTS},
            {"name": "Redis Fast Ingest", "status": "LISTENING", "stream": "argus:stream:telemetry"},
            {"name": "GeoJSON CAD Poller", "status": "ACTIVE", "frequency": "2s"},
            {"name": "RTSP Surveillance Sentinel", "status": "STREAMING", "channels": 5}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.stream-ingestion-service.src.main:app", host=settings.INGESTION_HOST, port=settings.INGESTION_PORT, reload=True)
