import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=env_path)

PORT = int(os.getenv("DASHBOARD_PORT", "3000"))
PUBLIC_DIR = Path(__file__).resolve().parent.parent / "public"

app = FastAPI(title="ARGUS Tactical Command Center Dashboard", version="2.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(PUBLIC_DIR)), name="static")

# Mount assets directory for surveillance images and branding
ASSETS_DIR = Path(__file__).resolve().parents[3] / "assets"
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

@app.get("/health")
def health():
    return {"status": "HEALTHY", "ui": "argus-tactical-dashboard", "port": PORT}

@app.get("/")
def serve_index():
    index_file = PUBLIC_DIR / "index.html"
    return FileResponse(str(index_file))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.tactical-dashboard.src.main:app", host="0.0.0.0", port=PORT, reload=True)
