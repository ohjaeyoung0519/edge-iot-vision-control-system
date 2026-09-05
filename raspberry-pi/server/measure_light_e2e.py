import csv
import json
import statistics
import time
import urllib.request
from datetime import datetime
from pathlib import Path


BASE_URL = "http://192.168.0.21"

NUM_CYCLES = 10
PAUSE_SEC = 1.5

PROGRAMMED_DELAY_MS = 1000.0


ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = (
    ROOT
    / "data"
    / "raw"
    / "end_to_end"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

SESSION_ID = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / f"light_http_e2e_20_{SESSION_ID}.csv"
)


def measure(action):
    url = f"{BASE_URL}/api/light/{action}"

    start = time.perf_counter()

    with urllib.request.urlopen(
        url,
        timeout=5
    ) as response:
        body = response.read().decode("utf-8")

    end = time.perf_counter()

    data = json.loads(body)

    total_ms = (end - start) * 1000.0

    remainder_ms = (
        total_ms
        - PROGRAMMED_DELAY_MS
    )

    return total_ms, remainder_ms, data


rows = []
all_values = []
on_values = []
off_values = []


print()
print("=" * 56)
print("Light Switch End-to-End Latency")
print("=" * 56)
print(f"Cycles            : {NUM_CYCLES}")
print(f"Total Actuations  : {NUM_CYCLES * 2}")
print(f"Programmed Delay  : {PROGRAMMED_DELAY_MS:.0f} ms")
print(f"Pause             : {PAUSE_SEC} sec")
print(f"Output            : {OUTPUT_FILE}")
print("=" * 56)
print()


sequence = 0

for cycle in range(
    1,
    NUM_CYCLES + 1
):
    for action in [
        "on",
        "off"
    ]:
        sequence += 1

        timestamp = (
            datetime.now().isoformat()
        )

        try:
            total_ms, remainder_ms, data = (
                measure(action)
            )

            status = data.get(
                "status",
                ""
            )

            free_heap = data.get(
                "free_heap"
            )

            if status != "ok":
                raise RuntimeError(
                    f"Unexpected status: {status}"
                )

            all_values.append(
                total_ms
            )

            if action == "on":
                on_values.append(
                    total_ms
                )
            else:
                off_values.append(
                    total_ms
                )

            rows.append({
                "timestamp": timestamp,
                "sequence": sequence,
                "cycle": cycle,
                "action": action,
                "status": "success",
                "total_e2e_ms":
                    f"{total_ms:.3f}",
                "programmed_delay_ms":
                    f"{PROGRAMMED_DELAY_MS:.3f}",
                "non_programmed_remainder_ms":
                    f"{remainder_ms:.3f}",
                "free_heap": free_heap,
                "error": "",
            })

            print(
                f"[{sequence:02d}] "
                f"{action.upper():3s} | "
                f"E2E={total_ms:8.3f} ms | "
                f"Remainder={remainder_ms:7.3f} ms | "
                f"success"
            )

        except Exception as e:

            rows.append({
                "timestamp": timestamp,
                "sequence": sequence,
                "cycle": cycle,
                "action": action,
                "status": "error",
                "total_e2e_ms": "",
                "programmed_delay_ms":
                    f"{PROGRAMMED_DELAY_MS:.3f}",
                "non_programmed_remainder_ms": "",
                "free_heap": "",
                "error": str(e),
            })

            print(
                f"[{sequence:02d}] "
                f"{action.upper():3s} | "
                f"ERROR: {e}"
            )

        time.sleep(
            PAUSE_SEC
        )


fieldnames = [
    "timestamp",
    "sequence",
    "cycle",
    "action",
    "status",
    "total_e2e_ms",
    "programmed_delay_ms",
    "non_programmed_remainder_ms",
    "free_heap",
    "error",
]


with OUTPUT_FILE.open(
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(rows)


def print_summary(name, values):
    if not values:
        return

    print()
    print(name)
    print("-" * 36)

    print(
        f"Samples : {len(values)}"
    )

    print(
        f"Mean    : "
        f"{statistics.mean(values):.3f} ms"
    )

    print(
        f"Median  : "
        f"{statistics.median(values):.3f} ms"
    )

    print(
        f"Min     : "
        f"{min(values):.3f} ms"
    )

    print(
        f"Max     : "
        f"{max(values):.3f} ms"
    )


print()
print("=" * 56)
print("FINAL E2E SUMMARY")
print("=" * 56)

print_summary(
    "ON",
    on_values
)

print_summary(
    "OFF",
    off_values
)

print_summary(
    "ALL",
    all_values
)

print()
print(
    f"Saved Raw Data: {OUTPUT_FILE}"
)
