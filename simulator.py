import time
import random
import requests

API = "http://web:5000/api/ingest"
HEALTH = "http://web:5000/health"
API_KEY = "WATER_LEAK_API_KEY_123"

NODES = ["node1", "node2", "node3", "node4"]

def wait_for_server():
    print("⏳ Waiting for Flask server...")
    while True:
        try:
            r = requests.get(HEALTH, timeout=2)
            if r.status_code == 200:
                print("✅ Flask server is ready.")
                return
        except Exception:
            pass
        time.sleep(2)

def post(node_id, flow):
    payload = {
        "node_id": node_id,
        "flow_lpm": flow,
        "pressure_kpa": 200 + random.random() * 10
    }
    r = requests.post(API, json=payload, headers={"X-API-KEY": API_KEY}, timeout=5)
    if r.status_code != 200:
        print("POST failed:", r.status_code, r.text)

def main():
    wait_for_server()
    base = 300.0
    while True:
        flows = [base, base - 5, base - 8, base - 10]

        if random.random() < 0.30:
            flows = [base, base - 5, base - 90, base - 95]

        flows = [max(0.0, f + random.uniform(-2, 2)) for f in flows]

        for nid, f in zip(NODES, flows):
            post(nid, f)

        print("📡 Sent:", dict(zip(NODES, flows)))
        time.sleep(10)

if __name__ == "__main__":
    main()
