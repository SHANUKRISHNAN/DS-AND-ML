# EcoTwin — Reinforcement Learning for Urban Carbon Dispersal

A digital twin of a city traffic grid where a reinforcement learning agent controls traffic
lights to minimize **both** commute wait times and localized CO2 buildup — not just one at
the expense of the other.

## Problem Statement

Standard traffic optimization algorithms minimize vehicle wait times exclusively, ignoring the
environmental impact of their decisions. This lets hazardous, localized smog and CO2 build up
at major intersections even when traffic is "flowing well" by conventional metrics. EcoTwin
treats congestion and pollution as a joint optimization problem.

## What's Built So Far (Week 1 + Week 2)

| | Backend | Frontend |
|---|---|---|
| **Week 1** | SUMO city grid + traffic demand generated and TraCI-controllable | React app rendering the grid as SVG |
| **Week 2** | Custom Gymnasium environment (`EcoTwinEnv`) with a calibrated multi-objective reward | Live WebSocket feed rendering moving vehicles in real time |

Both checkpoints have been **run and verified**, not just written — see "Verification Notes"
below for exactly what was tested and how.

## Architecture

```
┌─────────────────┐     TraCI      ┌──────────────────┐
│  SUMO simulation │◄──────────────►│  FastAPI backend │
│  (city_grid.*)   │                │    (server.py)   │
└─────────────────┘                └────────┬─────────┘
                                             │ WebSocket
                                             ▼
                                    ┌──────────────────┐
                                    │  React frontend   │
                                    │  (SVG live map)    │
                                    └──────────────────┘

┌─────────────────┐     TraCI      ┌──────────────────┐
│  SUMO simulation │◄──────────────►│  ecotwin_env.py  │
│  (same grid)      │                │  (Gymnasium env) │
└─────────────────┘                └──────────────────┘
                                             ▲
                                             │ (Week 3: PPO/DQN agent)
```

`server.py` and `ecotwin_env.py` are independent: the former drives the live dashboard, the
latter is what an RL agent will train against in Week 3. They don't import each other.

## Tech Stack

- **Simulation:** [SUMO](https://sumo.dlr.de/) (Simulation of Urban MObility) via TraCI
- **RL environment:** [Gymnasium](https://gymnasium.farama.org/) (maintained successor to OpenAI Gym)
- **Backend:** Python, FastAPI, WebSockets
- **Frontend:** React (Vite), plain SVG for rendering
- **Planned (Week 3):** Ray RLlib (PPO/DQN) for agent training

## Project Structure

```
ecotwin/
├── backend/
│   ├── requirements.txt
│   ├── generate_network.sh / .bat
│   ├── generate_routes.sh / .bat
│   ├── city_grid.sumocfg
│   ├── city_grid.net.xml       # generated, git-ignored
│   ├── city_grid.rou.xml       # generated, git-ignored
│   ├── server.py               # live dashboard backend
│   ├── ecotwin_env.py          # Gymnasium RL environment
│   ├── get_tls_ids.py          # helper: lists traffic light IDs
│   ├── smoke_test_env.py       # standalone env verification script
│   └── test_connection.py      # standalone WebSocket verification script
└── frontend/
    ├── package.json
    └── src/
        ├── App.jsx
        ├── main.jsx
        ├── components/
        │   ├── GridMap.jsx     # static grid (Week 1)
        │   └── LiveMap.jsx     # live vehicle rendering (Week 2)
        └── hooks/
            └── useSimulationSocket.js
```

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **SUMO** — install via `pip install eclipse-sumo` inside your backend venv (simplest), or the
  official installer from [sumo.dlr.de](https://sumo.dlr.de/docs/Downloads.php)

## Setup

### Backend

```bash
cd backend
python -m venv venv

# macOS/Linux
source venv/bin/activate
# Windows (cmd)
venv\Scripts\activate

pip install -r requirements.txt
```

Set `SUMO_HOME` — required so `traci`/`sumolib` and SUMO's own tools can find each other:

```bash
# macOS/Linux
export SUMO_HOME=/usr/share/sumo   # adjust if you installed elsewhere

# Windows (cmd) — if you used pip install eclipse-sumo inside this venv:
python -c "import sumo, os; print(os.path.dirname(sumo.__file__))"
set "SUMO_HOME=<paste the path printed above>"
```

Generate the SUMO network and demand files (these are build artifacts, not checked into git):

```bash
# macOS/Linux
bash generate_network.sh
bash generate_routes.sh

# Windows
generate_network.bat
generate_routes.bat
```

### Frontend

```bash
cd frontend
npm install
```

## Running It

Run these in **two separate terminals**, backend first:

**Terminal 1 — backend:**
```bash
cd backend
venv\Scripts\activate        # or: source venv/bin/activate
uvicorn server:app --reload --port 8000
```
Confirm it's healthy: open `http://127.0.0.1:8000/` in a browser — you should see
`{"status":"ok","message":"EcoTwin backend is running"}`.

**Terminal 2 — frontend:**
```bash
cd frontend
npm run dev
```
Open the printed URL (typically `http://localhost:5173`). You should see the city grid with
orange dots moving along the streets, sourced live from the running SUMO simulation.

**Optional — verify the pieces independently, without the browser:**
```bash
cd backend
python get_tls_ids.py          # lists the network's traffic light IDs
python smoke_test_env.py       # proves the Gym environment works standalone
python test_connection.py      # proves the WebSocket streams real data (backend must be running)
```

## Verification Notes

These checkpoints weren't just written — they were actually run and their output inspected:

- **Coordinates:** `traci.simulation.convertGeo()` returns unchanged raw coordinates on this
  network (it has no real geographic projection attached), so the frontend renders vehicles as
  plain SVG using local `(x, y)` coordinates directly rather than fake GPS coordinates.
- **Reward function calibration:** an initial flat `0.5 * wait + 0.5 * (co2/1000)` reward was
  tested by charting both components separately over a real 300-step run. CO2 (scale: tens of
  thousands) completely dominated wait time (scale: tens of seconds) — the agent would have
  learned to ignore congestion almost entirely. The reward now normalizes both terms to a 0–1
  range against calibrated reference ceilings before weighting. **These reference values were
  calibrated against this specific network's observed traffic** — recheck them if your demand
  pattern differs significantly (see the comments in `ecotwin_env.py`).

## Roadmap

- **Week 3:** Train the PPO/DQN agent (Ray RLlib) against `EcoTwinEnv`; add a live CO2 heatmap
  overlay to the frontend.
- **Week 4:** Wire the trained agent into `server.py` to control live traffic lights; polish the
  dashboard with metric charts (total CO2 emitted, average wait time).

## License

_Add your license here._
