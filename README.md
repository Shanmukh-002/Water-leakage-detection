
# 💧 Water Leak Detection System

A real-time water leak detection system built using **Flask**, **SQLite**, and **Docker**, designed to monitor pipeline flow data and automatically identify potential leaks between nodes.

This project simulates real-world pipeline monitoring by analyzing flow rate differences across multiple nodes and visualizing results through a live dashboard.

---

## 🚀 Features

* 📡 Real-time data ingestion via REST API
* 📊 Flow comparison between pipeline nodes
* 🚨 Automatic leak detection using threshold logic
* ⚠️ Severity classification (`WARNING`, `CRITICAL`)
* 🗃️ Persistent storage using SQLite
* 📈 Interactive dashboard with live updates
* 🤖 Built-in simulator to generate sample data

---

## 🧠 How It Works

1. Each pipeline node sends flow readings (`flow_lpm`)

2. The system compares flow between consecutive nodes

3. It calculates:

   ```
   Δ = flow(previous node) - flow(next node)
   ```

4. If Δ exceeds a configured threshold → 🚨 Leak detected

5. Leak events are stored and visualized on the dashboard

The core logic is implemented in the leak computation module .

---

## 🏗️ Tech Stack

* **Backend:** Flask 
* **Database:** SQLite (via SQLAlchemy) 
* **Containerization:** Docker & Docker Compose 
* **Simulation:** Python-based data generator 

---

## ⚙️ Installation & Setup

### 🐳 Option 1: Run with Docker (Recommended)

```bash
docker compose up --build
```

Access the app:

* Dashboard → [http://localhost:5001/](http://localhost:5001/)
* Health Check → [http://localhost:5001/health](http://localhost:5001/health)

Stop the app:

```bash
docker compose down
```

Reset database:

```bash
docker compose down -v
```

---

### 🖥️ Option 2: Run Locally

#### Prerequisites

* Python 3.11+

#### Steps

```bash
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
# .venv\Scripts\activate    # Windows

pip install -r requirements.txt
python app.py
```

Open:

```
http://127.0.0.1:5000/
```

---

## 📡 API Endpoints

| Endpoint          | Method | Description           |
| ----------------- | ------ | --------------------- |
| `/health`         | GET    | Service status        |
| `/`               | GET    | Dashboard UI          |
| `/api/ingest`     | POST   | Submit flow data      |
| `/api/status`     | GET    | Current system status |
| `/api/events`     | GET    | Leak history          |
| `/api/chart-data` | GET    | Data for graphs       |

---

### 📥 Example: Send Data

```bash
curl -X POST http://localhost:5001/api/ingest \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: WATER_LEAK_API_KEY_123" \
  -d '{"node_id":"node1","flow_lpm":300,"pressure_kpa":205}'
```

---

## 🤖 Simulator

The simulator automatically generates data and sends it to the API.

Behavior:

* Normal Mode → small flow drops
* Leak Mode → large drop between nodes (~30% probability)

Runs automatically with Docker.

---

## ⚙️ Configuration

All system settings are defined in :

* `NODES` → pipeline nodes and distances
* `LEAK_THRESHOLD_LPM` → detection threshold
* `FRESH_SECONDS` → data freshness window
* `DATABASE_URI` → SQLite storage

---

## 📂 Project Structure

```
.
├── app.py              # Flask application & API routes
├── config.py           # Configuration settings
├── leak_logic.py       # Leak detection logic
├── models.py           # Database models
├── simulator.py        # Data generator
├── docker-compose.yml  # Docker setup
├── requirements.txt    # Dependencies
```

---

## 🧪 Troubleshooting

**No data on dashboard**

* Ensure simulator is running
* Check `/health` endpoint

**Unauthorized error**

* Verify API key in request headers

**Reset everything**

```bash
docker compose down -v
```

---