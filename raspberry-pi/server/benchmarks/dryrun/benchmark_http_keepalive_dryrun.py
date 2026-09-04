import csv
import statistics
import time
from datetime import datetime
from pathlib import Path

import requests


URL = "http://192.168.0.21/api/benchmark"
NUM_REQUESTS = 30
INTERVAL_SEC = 0.2
TIMEOUT_SEC = 3
RUN_ID = 1

OUTPUT_DIR = Path("data/raw/http_keepalive")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "http_keepalive_dryrun_30_nosleep_confirmed.csv"


session = requests.Session()
session.headers.update({
    "Connection": "keep-alive"
})


rows = []
successful_rtts = []


print("=" * 42)
print("HTTP Keep-Alive Benchmark Dry Run")
print("=" * 42)
print(f"Target     : {URL}")
print(f"Requests   : {NUM_REQUESTS}")
print(f"Interval   : {INTERVAL_SEC} sec")
print(f"Output     : {OUTPUT_FILE}")
print("=" * 42)
print()


for seq in range(1, NUM_REQUESTS + 1):

    command_id = f"http-keepalive-dryrun-{RUN_ID}-{seq}"

    start = time.perf_counter()

    try:
        response = session.get(
            URL,
            params={"id": command_id},
            timeout=TIMEOUT_SEC
        )

        response.raise_for_status()
        data = response.json()

        end = time.perf_counter()
        rtt_ms = (end - start) * 1000

        returned_id = str(data.get("command_id", ""))

        if returned_id != command_id:
            raise ValueError(
                f"command_id mismatch: sent={command_id}, received={returned_id}"
            )

        esp_processing_us = data.get("esp_processing_us")
        free_heap = data.get("free_heap")
        min_free_heap = data.get("min_free_heap")
        max_alloc_heap = data.get("max_alloc_heap")
        rssi_dbm = data.get("rssi_dbm")

        successful_rtts.append(rtt_ms)

        rows.append({
            "timestamp": datetime.now().isoformat(),
            "protocol": "http_keepalive",
            "run_id": RUN_ID,
            "seq": seq,
            "command_id": command_id,
            "status": "success",
            "rtt_ms": f"{rtt_ms:.3f}",
            "esp_processing_us": esp_processing_us,
            "esp_free_heap": free_heap,
            "esp_min_free_heap": min_free_heap,
            "esp_max_alloc_heap": max_alloc_heap,
            "rssi_dbm": rssi_dbm,
            "qos": "",
            "error": ""
        })

        print(
            f"[{seq:02d}] RTT={rtt_ms:8.3f} ms | "
            f"ESP={esp_processing_us} us | "
            f"Heap={free_heap} | "
            f"RSSI={rssi_dbm} dBm | success"
        )

    except Exception as e:

        end = time.perf_counter()
        elapsed_ms = (end - start) * 1000

        rows.append({
            "timestamp": datetime.now().isoformat(),
            "protocol": "http_keepalive",
            "run_id": RUN_ID,
            "seq": seq,
            "command_id": command_id,
            "status": "error",
            "rtt_ms": "",
            "esp_processing_us": "",
            "esp_free_heap": "",
            "esp_min_free_heap": "",
            "esp_max_alloc_heap": "",
            "rssi_dbm": "",
            "qos": "",
            "error": str(e)
        })

        print(
            f"[{seq:02d}] ERROR after {elapsed_ms:.3f} ms | {e}"
        )

    time.sleep(INTERVAL_SEC)


session.close()


fieldnames = [
    "timestamp",
    "protocol",
    "run_id",
    "seq",
    "command_id",
    "status",
    "rtt_ms",
    "esp_processing_us",
    "esp_free_heap",
    "esp_min_free_heap",
    "esp_max_alloc_heap",
    "rssi_dbm",
    "qos",
    "error"
]


with OUTPUT_FILE.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


print()
print("=" * 42)
print("HTTP Keep-Alive Dry Run Summary")
print("=" * 42)

print(f"Success : {len(successful_rtts)}/{NUM_REQUESTS}")

if successful_rtts:
    print(f"Min RTT : {min(successful_rtts):.3f} ms")
    print(f"Max RTT : {max(successful_rtts):.3f} ms")
    print(f"Mean RTT: {statistics.mean(successful_rtts):.3f} ms")
    print(f"Median  : {statistics.median(successful_rtts):.3f} ms")

print()
print(f"Saved Raw Data: {OUTPUT_FILE}")
