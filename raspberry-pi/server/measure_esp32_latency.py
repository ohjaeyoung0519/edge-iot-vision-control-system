import csv
import json
import time
import urllib.request
from datetime import datetime

URL = "http://192.168.0.36/api/ping"
OUTPUT_FILE = "esp32_latency_rpi_to_esp32_100.csv"
NUM_REQUESTS = 100

results = []

for i in range(1, NUM_REQUESTS + 1):
    start = time.perf_counter()

    try:
        with urllib.request.urlopen(URL, timeout=3) as response:
            raw_data = response.read().decode("utf-8")

        elapsed_ms = (time.perf_counter() - start) * 1000
        data = json.loads(raw_data)

        result = {
            "index": i,
            "timestamp": datetime.now().isoformat(),
            "status": "ok",
            "latency_ms": round(elapsed_ms, 2),
            "esp32_free_heap": data.get("free_heap"),
            "esp32_rssi": data.get("rssi"),
            "esp32_uptime_ms": data.get("uptime_ms"),
            "error": ""
        }

        print(f"[{i:02d}] OK - latency: {result['latency_ms']} ms, "
              f"free_heap: {result['esp32_free_heap']}, RSSI: {result['esp32_rssi']} dBm")

    except Exception as error:
        elapsed_ms = (time.perf_counter() - start) * 1000

        result = {
            "index": i,
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "latency_ms": round(elapsed_ms, 2),
            "esp32_free_heap": "",
            "esp32_rssi": "",
            "esp32_uptime_ms": "",
            "error": str(error)
        }

        print(f"[{i:02d}] ERROR - {error}")

    results.append(result)
    time.sleep(0.5)

with open(OUTPUT_FILE, "w", newline="") as csvfile:
    fieldnames = [
        "index",
        "timestamp",
        "status",
        "latency_ms",
        "esp32_free_heap",
        "esp32_rssi",
        "esp32_uptime_ms",
        "error"
    ]

    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

latencies = [r["latency_ms"] for r in results if r["status"] == "ok"]

if latencies:
    print()
    print("=== Latency Summary ===")
    print(f"count: {len(latencies)}")
    print(f"min: {min(latencies):.2f} ms")
    print(f"max: {max(latencies):.2f} ms")
    print(f"avg: {sum(latencies) / len(latencies):.2f} ms")

print()
print(f"Saved result to {OUTPUT_FILE}")
