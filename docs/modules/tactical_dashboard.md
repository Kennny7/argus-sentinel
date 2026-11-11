# ARGUS Sentinel - Tactical Dashboard Module Documentation

Next-generation Command Center frontend inspired by high-threat cartography and tactical reconnaissance consoles.

## Module Tree Structure

```text
services/tactical-dashboard/
├── Dockerfile
├── pyproject.toml
├── README.md
├── public/
│   └── index.html
└── src/
    └── main.py
```

## Workflow Diagram

```mermaid
flowchart TD
    User[Officer / Commander] --> Browser[Web Browser]
    Browser --> Server[Dashboard Web Server :3000]
    
    subgraph Views
        Map[Tactical Grid Map & Heatmap]
        CCTV[CCTV Video Recon Matrix & Reticles]
        Mesh[3D Facial Mesh Reconstructor]
        HITL[Human-In-The-Loop Audit Station]
        Agent[Autonomous AI Agent Console]
        Streams[Stream Pipeline Monitor]
    end
    
    Browser --> Views
    Views <-->|WebSocket & REST| Gateway[Gateway API :8000]
```

<details>
<summary>Click to Expand Technical Capabilities</summary>

### Features
1. **Interactive Cartography**: High-contrast dark basemap with pulsing threat markers, sector filtering, and inter-node vector arcs.
2. **CCTV Target HUD**: Video surveillance frame with tracking brackets, vertical biometric scan animations, verified dossier popups, and technical telemetry panels.
3. **Three.js 3D Facial Mesh**: Interactive 468-point cranial wireframe with rotation controls (pitch, yaw, roll) and landmark topology storage.
4. **Human-In-The-Loop Modal**: Split verification station for approving, rejecting, or escalating suspect detections with operator audit logging.
5. **Autonomous Agent Interface**: On-demand generation of investigation dossiers leveraging local neural engines.
</details>
