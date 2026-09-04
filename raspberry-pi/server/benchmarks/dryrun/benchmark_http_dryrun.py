import csv
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path


# =========================
# Experiment Configuration
# =========================

ESP32_IP = "192.168.0.21"
BENCHMARK_URL = f"http://{ESP32_IP}/api/benchmark"

NUM_REQUESTS = 30
REQUEST_INTERVAL_SEC = 0.2
TIMEOUT_SEC = 3

RUN_ID = 1
PROTOCOL = "HTTP_DRYRUN"


# =========================
# Output Configuration
# =========================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "http"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = OUTPUT_DIR / "http_dryrun_30_nosleep_confirmed.csv"


# =========================
# Measurement
# =========================

results = []

print()
print("========================================")
print("HTTP Benchmark Dry Run")
print("========================================")
print(f"Target       : {BENCHMARK_URL}")
print(f"Requests     : {NUM_REQUESTS}")
print(f"Interval     : {REQUEST_INTERVAL_SEC} sec")
print(f"Output       : {OUTPUT_FILE}")
print("========================================")
print()


for seq in range(1, NUM_REQUESTS + 1):

    command_id = f"http-dryrun-{RUN_ID}-{seq}"

    query = urllib.parse.urlencode(
        {
            "id": command_id
        }
    )

    request_url = f"{BENCHMARK_URL}?{query}"

    start = time.perf_counter()

    try:

        with urllib.request.urlopen(
            request_url,
            timeout=TIMEOUT_SEC
        ) as response:

            raw_data = response.read().decode("utf-8")

        end = time.perf_counter()

        rtt_ms = (end - start) * 1000

        data = json.loads(raw_data)

        returned_command_id = data.get(
            "command_id",
            ""
        )

        # 보낸 command_id와 받은 command_id가
        # 일치하는지 확인
        if returned_command_id != command_id:
            status = "id_mismatch"
            error = (
                f"sent={command_id}, "
                f"received={returned_command_id}"
            )
        else:
            status = "success"
            error = ""

        result = {
            "timestamp": datetime.now().isoformat(),
            "protocol": PROTOCOL,
            "run_id": RUN_ID,
            "seq": seq,
            "command_id": command_id,
            "status": status,
            "rtt_ms": round(rtt_ms, 3),
            "esp_processing_us": data.get(
                "esp_processing_us",
                ""
            ),
            "esp_free_heap": data.get(
                "free_heap",
                ""
            ),
            "esp_min_free_heap": data.get(
                "min_free_heap",
                ""
            ),
            "esp_max_alloc_heap": data.get(
                "max_alloc_heap",
                ""
            ),
            "rssi_dbm": data.get(
                "rssi_dbm",
                ""
            ),
            "error": error,
        }

        print(
            f"[{seq:02d}] "
            f"RTT={result['rtt_ms']:8.3f} ms | "
            f"ESP={result['esp_processing_us']} us | "
            f"Heap={result['esp_free_heap']} | "
            f"RSSI={result['rssi_dbm']} dBm | "
            f"{status}"
        )

    except Exception as exc:

        end = time.perf_counter()

        rtt_ms = (end - start) * 1000

        result = {
            "timestamp": datetime.now().isoformat(),
            "protocol": PROTOCOL,
            "run_id": RUN_ID,
            "seq": seq,
            "command_id": command_id,
            "status": "error",
            "rtt_ms": round(rtt_ms, 3),
            "esp_processing_us": "",
            "esp_free_heap": "",
            "esp_min_free_heap": "",
            "esp_max_alloc_heap": "",
            "rssi_dbm": "",
            "error": str(exc),
        }

        print(
            f"[{seq:02d}] ERROR | "
            f"{exc}"
        )

    results.append(result)

    time.sleep(
        REQUEST_INTERVAL_SEC
    )


# =========================
# Save Raw CSV
# =========================

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
    "error",
]

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as csvfile:

    writer = csv.DictWriter(
        csvfile,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(results)


# =========================
# Dry Run Summary
# =========================

successful = [
    row
    for row in results
    if row["status"] == "success"
]

print()
print("========================================")
print("Dry Run Summary")
print("========================================")

print(
    f"Success: "
    f"{len(successful)}/{NUM_REQUESTS}"
)

if successful:

    latencies = [
        row["rtt_ms"]
        for row in successful
    ]

    print(
        f"Min RTT : "
        f"{min(latencies):.3f} ms"
    )

    print(
        f"Max RTT : "
        f"{max(latencies):.3f} ms"
    )

    print(
        f"Mean RTT: "
        f"{sum(latencies) / len(latencies):.3f} ms"
    )

print()
print(
    f"Saved Raw Data: {OUTPUT_FILE}"
)
