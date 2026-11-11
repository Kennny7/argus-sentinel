# ARGUS Sentinel - Newbie Quickstart Guide

A comprehensive, zero-assumption tutorial designed for newcomers, operators, and junior engineers to install, configure, and operate the ARGUS Sentinel platform on their local machine.

## Table of Contents
1. What is ARGUS Sentinel?
2. System Requirements
3. Step 1: Install Software Prerequisites
4. Step 2: Clone and Configure Environment
5. Step 3: Run the Entire System with Docker (Easiest)
6. Step 4: Run Microservices Individually with uv
7. Step 5: How to Use the Tactical Command Center
8. Common Troubleshooting and FAQ

---

## 1. What is ARGUS Sentinel?

ARGUS Sentinel is an autonomous reconnaissance and predictive intelligence platform designed for municipal crime monitoring. It takes information from police dispatches, street cameras, and sensor networks to:
- Predict how severe a reported crime is before officers arrive on the scene.
- Locate crime hotspots on an interactive tactical map.
- Detect suspects on surveillance feeds, match them against an intelligence database without null values, and reconstruct 3D facial wireframe profiles.
- Keep a human in the loop (HITL) so an operator always has the final say on biometric matches.
- Run autonomous AI investigation reports using locally hosted language models with zero paid cloud services.

---

## 2. System Requirements

- **Operating System**: Windows 10/11, macOS, or Linux (Ubuntu 20.04+ recommended).
- **Processor**: 4 physical CPU cores or more.
- **Memory (RAM)**: 8 GB minimum (16 GB recommended for running multiple containers).
- **Storage**: At least 5 GB of free disk space.
- **Browser**: Google Chrome, Mozilla Firefox, Microsoft Edge, or Brave.

---

## 3. Step 1: Install Software Prerequisites

You only need three free tools to run everything:

### A. Install Python (Version 3.10 or higher)
1. Visit the official Python download page: `https://www.python.org/downloads/`
2. Download the installer for your OS.
3. During installation on Windows, make sure to check the box: **"Add Python to PATH"**.

### B. Install uv (Ultra-Fast Python Package Manager)
On Windows PowerShell:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

On Linux or macOS:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify that uv is installed by running:
```bash
uv --version
```

### C. Install Docker Desktop (Optional but recommended)
1. Download Docker Desktop from `https://www.docker.com/products/docker-desktop/`
2. Follow the standard installation wizard.
3. Start Docker Desktop and ensure the engine status shows "running".

---

## 4. Step 2: Clone and Configure Environment

Open your terminal or PowerShell and navigate to the project root:

```bash
cd Azure-RealTime-Crime-Predictive-Analytics-System
```

Copy the example configuration to create your active `.env` file:

```bash
# On Windows PowerShell
Copy-Item .env.example .env

# On Linux or macOS
cp .env.example .env
```

The system is pre-configured with default local addresses and realistic intelligence datasets.

---

## 5. Step 3: Run the Entire System with Docker (Easiest Method)

If you have Docker Desktop running, you can start all 6 microservices and message brokers with a single command:

```bash
docker-compose up --build
```

Wait until you see the log messages stabilize. Once running, open your web browser and navigate to:

- **Tactical Command Center Dashboard**: `http://localhost:3000`
- **Central API Gateway Swagger UI**: `http://localhost:8000/docs`
- **Crime Prediction Swagger UI**: `http://localhost:8001/docs`
- **Surveillance Recon Swagger UI**: `http://localhost:8002/docs`
- **Stream Ingestion Swagger UI**: `http://localhost:8003/docs`
- **Ontology Agent Swagger UI**: `http://localhost:8004/docs`

To stop the system at any time, press `CTRL + C` in your terminal, or run:
```bash
docker-compose down
```

---

## 6. Step 4: Run Microservices Individually with uv

If you want to run services without Docker, or want to modify the code in real-time:

### Terminal 1: Crime Prediction Service
```bash
cd services/crime-prediction-service
uv venv
uv pip install -r pyproject.toml
python -m uvicorn src.main:app --port 8001 --reload
```

### Terminal 2: Surveillance Reconnaissance Service
```bash
cd services/surveillance-recon-service
uv venv
uv pip install -r pyproject.toml
python -m uvicorn src.main:app --port 8002 --reload
```

### Terminal 3: Stream Ingestion Service
```bash
cd services/stream-ingestion-service
uv venv
uv pip install -r pyproject.toml
python -m uvicorn src.main:app --port 8003 --reload
```

### Terminal 4: Ontology & Agent Service
```bash
cd services/ontology-agent-service
uv venv
uv pip install -r pyproject.toml
python -m uvicorn src.main:app --port 8004 --reload
```

### Terminal 5: Central Gateway API
```bash
cd services/gateway-api
uv venv
uv pip install -r pyproject.toml
python -m uvicorn src.main:app --port 8000 --reload
```

### Terminal 6: Tactical Dashboard
```bash
cd services/tactical-dashboard
uv venv
uv pip install -r pyproject.toml
python -m uvicorn src.main:app --port 3000 --reload
```

Now open `http://localhost:3000` in your web browser.

---

## 7. Step 5: How to Use the Tactical Command Center

<details>
<summary>Click to Expand User Interface Instructions</summary>

### 1. Tactical Grid Map
- View all municipal sectors and real-time incident pins.
- Critical incidents glow red, High incidents are amber, and Medium/Low are cyan/green.
- Click any card in the right sidebar to pan and zoom directly to the incident location.
- Use the **Test Ingestion Simulator** at the bottom of the sidebar to inject custom incident reports and watch them appear live on the map.

### 2. CCTV Recon Matrix
- Replicates live street surveillance feeds.
- The green tracking reticle follows moving subjects, and a scanning line analyzes biometric traits.
- The linked profile card shows verified records, technical traits, and social media handles.
- Click **[VERIFY]** to open the Human-in-the-Loop review dialog.

### 3. 3D Facial Mesh Recon
- Select any enrolled suspect from the dropdown.
- Adjust pitch, yaw, and roll sliders to rotate the 3D cranial landmark wireframe in real-time.
- Click **[SAVE 3D PROFILE TO DATABASE]** to persist the calculated topology.

### 4. HITL Verification Queue
- Shows detections awaiting human operator review.
- Review suspect photo crop, match confidence, and camera timestamp.
- Click **[AUDIT & VERIFY]** to accept, reject, or escalate the identification with audit notes.

### 5. AI Agent Investigation
- Select a suspect and sector.
- Click **[EXECUTE AUTONOMOUS INVESTIGATION]**. The agent traverses the knowledge graph and queries your local LLM to generate an actionable intelligence report.
</details>

---

## 8. Common Troubleshooting and FAQ

- **Port Conflict (e.g. Port 8000 or 3000 already in use)**:
  Change the port in your `.env` file (e.g. `GATEWAY_PORT=8080`) or stop the application using that port.
- **Docker Build Error**:
  Ensure Docker Desktop is fully started before running `docker-compose up`.
- **Local LLM Connection Timeout**:
  If your local LLM host (`10.210.8.63:8080`) is offline, the agent automatically switches to local deterministic intelligence synthesis so your workflow is never interrupted.
