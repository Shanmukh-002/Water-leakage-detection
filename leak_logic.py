from datetime import datetime, timedelta

def is_fresh(ts, seconds: int) -> bool:
    return ts >= datetime.utcnow() - timedelta(seconds=seconds)

def compute_sections(latest_by_node, nodes_ordered, threshold_lpm: float):
    """
    For each consecutive pair:
      delta = flow(prev) - flow(next)
    status:
      - unknown: missing readings
      - leak: delta >= threshold
      - ok: delta < threshold
    """
    results = []
    for i in range(len(nodes_ordered) - 1):
        a = nodes_ordered[i]["id"]
        b = nodes_ordered[i + 1]["id"]
        ra = latest_by_node.get(a)
        rb = latest_by_node.get(b)

        section_id = f"{a}->{b}"

        if not ra or not rb:
            results.append({
                "section": section_id,
                "status": "unknown",
                "severity": "INFO",
                "delta_lpm": None,
                "message": "Missing readings for one or both nodes.",
                "ts": None
            })
            continue

        delta = float(ra.flow_lpm) - float(rb.flow_lpm)
        ts = max(ra.ts, rb.ts)

        if delta >= threshold_lpm:
            severity = "CRITICAL" if delta >= threshold_lpm * 2 else "WARNING"
            results.append({
                "section": section_id,
                "status": "leak",
                "severity": severity,
                "delta_lpm": round(delta, 2),
                "message": f"Leak suspected between {a} and {b} (drop {delta:.2f} L/min).",
                "ts": ts
            })
        else:
            results.append({
                "section": section_id,
                "status": "ok",
                "severity": "INFO",
                "delta_lpm": round(delta, 2),
                "message": f"Section {a}->{b} OK (drop {delta:.2f} L/min).",
                "ts": ts
            })

    return results
