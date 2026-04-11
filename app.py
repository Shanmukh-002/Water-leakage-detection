from flask import Flask, request, jsonify, render_template
from datetime import datetime
from config import Config
from models import db, Reading, LeakEvent
from leak_logic import compute_sections, is_fresh

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

nodes = sorted(Config.NODES, key=lambda x: x["km"])
node_ids = {n["id"] for n in nodes}

def authorized(req) -> bool:
    return req.headers.get("X-API-KEY", "") == Config.INGEST_API_KEY

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

@app.get("/")
def index():
    return render_template("index.html")

def latest_fresh_readings():
    """
    Latest per node, but only if fresh.
    Returns dict node_id -> Reading
    """
    latest = {}
    for n in nodes:
        r = (Reading.query
             .filter_by(node_id=n["id"])
             .order_by(Reading.ts.desc())
             .first())
        if r and is_fresh(r.ts, Config.FRESH_SECONDS):
            latest[n["id"]] = r
    return latest

def log_leak_events(section_results):
    """
    Store leak events only when status == leak.
    Deduplicate: same section within 10 minutes with similar delta (±5).
    """
    for item in section_results:
        if item["status"] != "leak":
            continue

        section = item["section"]
        delta_lpm = float(item["delta_lpm"])
        severity = item["severity"]
        message = item["message"]
        ts = item["ts"] or datetime.utcnow()

        recent = (LeakEvent.query
                  .filter_by(section=section)
                  .order_by(LeakEvent.ts.desc())
                  .first())

        if recent:
            age_s = (ts - recent.ts).total_seconds()
            if age_s < 600 and abs(recent.delta_lpm - delta_lpm) < 5:
                continue

        db.session.add(LeakEvent(
            section=section,
            delta_lpm=delta_lpm,
            severity=severity,
            message=message,
            ts=ts
        ))

    db.session.commit()

@app.post("/api/ingest")
def ingest():
    if not authorized(request):
        return jsonify({"error": "Unauthorized (bad X-API-KEY)"}), 401

    data = request.get_json(silent=True) or {}
    node_id = (data.get("node_id") or "").strip().lower()
    if node_id not in node_ids:
        return jsonify({"error": "invalid node_id"}), 400

    try:
        flow_lpm = float(data["flow_lpm"])
    except Exception:
        return jsonify({"error": "flow_lpm must be numeric"}), 400

    pressure = data.get("pressure_kpa", None)
    if pressure is not None:
        try:
            pressure = float(pressure)
        except Exception:
            return jsonify({"error": "pressure_kpa must be numeric"}), 400

    r = Reading(node_id=node_id, flow_lpm=flow_lpm, pressure_kpa=pressure, ts=datetime.utcnow())
    db.session.add(r)
    db.session.commit()

    # After ingest, compute + log leaks
    latest = latest_fresh_readings()
    sections = compute_sections(latest, nodes, Config.LEAK_THRESHOLD_LPM)
    log_leak_events(sections)

    return jsonify({"ok": True, "stored": {"node_id": node_id, "flow_lpm": flow_lpm, "ts": r.ts.isoformat()}})

@app.get("/api/status")
def status():
    latest = latest_fresh_readings()
    sections = compute_sections(latest, nodes, Config.LEAK_THRESHOLD_LPM)

    nodes_json = []
    for n in nodes:
        r = latest.get(n["id"])
        nodes_json.append({
            "node_id": n["id"],
            "name": n["name"],
            "km": n["km"],
            "flow_lpm": None if not r else r.flow_lpm,
            "pressure_kpa": None if not r else r.pressure_kpa,
            "ts": None if not r else r.ts.isoformat(),
            "fresh": bool(r),
        })

    # overall status (simple)
    leak_found = any(s["status"] == "leak" for s in sections)
    unknown_found = any(s["status"] == "unknown" for s in sections)
    overall = "LEAK DETECTED" if leak_found else ("DATA MISSING" if unknown_found else "NORMAL")

    return jsonify({
        "overall_status": overall,
        "threshold_lpm": Config.LEAK_THRESHOLD_LPM,
        "fresh_seconds": Config.FRESH_SECONDS,
        "nodes": nodes_json,
        "sections": sections
    })

@app.get("/api/events")
def events():
    limit = int(request.args.get("limit", "20"))
    limit = max(1, min(limit, 200))

    rows = (LeakEvent.query
            .order_by(LeakEvent.ts.desc())
            .limit(limit)
            .all())

    return jsonify([{
        "ts": r.ts.isoformat(),
        "section": r.section,
        "severity": r.severity,
        "delta_lpm": r.delta_lpm,
        "message": r.message
    } for r in rows])

@app.get("/api/chart-data")
def chart_data():
    # last N readings per node for charts
    N = 40
    flow_chart = {}

    for n in nodes:
        readings = (Reading.query
                    .filter_by(node_id=n["id"])
                    .order_by(Reading.ts.desc())
                    .limit(N)
                    .all())
        readings = list(reversed(readings))
        flow_chart[n["id"]] = {
            "time": [r.ts.strftime("%H:%M:%S") for r in readings],
            "flow": [r.flow_lpm for r in readings],
        }

    # leak bars based on latest fresh readings
    latest = latest_fresh_readings()
    sections = compute_sections(latest, nodes, Config.LEAK_THRESHOLD_LPM)

    leak_chart = [{
        "section": s["section"],
        "delta_lpm": 0 if s["delta_lpm"] is None else s["delta_lpm"],
        "status": s["status"],
        "severity": s["severity"]
    } for s in sections]

    return jsonify({
        "flow_chart": flow_chart,
        "leak_chart": leak_chart
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
