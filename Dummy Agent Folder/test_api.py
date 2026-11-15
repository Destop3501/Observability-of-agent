"""Quick test script for the API endpoints."""
import requests

BASE = "http://localhost:5000"

def test_health():
    r = requests.get(f"{BASE}/api/health")
    print("HEALTH:", r.json())

def test_keys():
    r = requests.get(f"{BASE}/api/keys")
    print("KEYS:", r.json())

def test_order(fault="none"):
    payload = {
        "customer_id": "CUST-1001",
        "items": ["Laptop", "Mouse", "Keyboard"],
        "amount": 1299.99,
        "fault": fault,
    }
    r = requests.post(f"{BASE}/api/process-order", json=payload)
    data = r.json()
    print(f"\n=== Fault: {fault} ===")
    print(f"Success: {data.get('success')}")
    print(f"Error type: {data.get('error_type', 'none')}")
    for step in data.get("steps", []):
        status = step["status"]
        icon = {"success": "✅", "failed": "❌", "running": "…", "interrupted": "⚠️"}.get(status, "?")
        print(f"  {icon} Step {step['step']}: {step['name']} → {status}")
        if step.get("error"):
            print(f"     Error: {step['error']}")

if __name__ == "__main__":
    test_health()
    test_keys()
    for fault in ["none", "inventory", "payment", "invoice", "interrupt", "delivery"]:
        test_order(fault)
