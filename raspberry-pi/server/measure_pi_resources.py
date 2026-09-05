from pathlib import Path
from datetime import datetime
import csv
import statistics
import subprocess
import sys
import time

import psutil


ROOT = Path(__file__).resolve().parents[2]

WORKER = (
    ROOT
    / "raspberry-pi"
    / "server"
    / "resource_worker.py"
)

RAW_DIR = (
    ROOT
    / "data"
    / "raw"
    / "resource"
)

PROCESSED_DIR = (
    ROOT
    / "data"
    / "processed"
)

RAW_DIR.mkdir(
    parents=True,
    exist_ok=True
)

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


REQUESTS_PER_RUN = 200
REQUEST_INTERVAL_SEC = 0.2

SAMPLE_INTERVAL_SEC = 0.2
BETWEEN_RUN_PAUSE_SEC = 3.0


RUN_ORDERS = [
    ["http", "mqtt_qos0", "mqtt_qos1"],
    ["mqtt_qos0", "mqtt_qos1", "http"],
    ["mqtt_qos1", "http", "mqtt_qos0"],
]


SESSION_ID = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

RAW_FILE = (
    RAW_DIR
    / f"pi_resource_samples_{SESSION_ID}.csv"
)

SUMMARY_FILE = (
    PROCESSED_DIR
    / f"pi_resource_summary_{SESSION_ID}.csv"
)


def find_mosquitto():
    matches = []

    for proc in psutil.process_iter(
        ["pid", "name", "cmdline"]
    ):
        try:
            name = proc.info["name"] or ""
            cmdline = proc.info["cmdline"] or []

            if (
                name == "mosquitto"
                or any(
                    "mosquitto" in str(x)
                    for x in cmdline
                )
            ):
                matches.append(proc)

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied
        ):
            pass

    if not matches:
        raise RuntimeError(
            "Mosquitto process not found"
        )

    return matches[0]


def percentile(values, q):
    if not values:
        return 0.0

    values = sorted(values)

    if len(values) == 1:
        return values[0]

    position = (
        (len(values) - 1)
        * q
        / 100.0
    )

    lower = int(position)
    upper = min(
        lower + 1,
        len(values) - 1
    )

    fraction = position - lower

    return (
        values[lower]
        + (
            values[upper]
            - values[lower]
        )
        * fraction
    )


mosquitto = find_mosquitto()

print()
print("=" * 64)
print("Raspberry Pi Resource Benchmark")
print("=" * 64)
print(f"Mosquitto PID      : {mosquitto.pid}")
print(f"Requests / Run     : {REQUESTS_PER_RUN}")
print(f"Request interval   : {REQUEST_INTERVAL_SEC} sec")
print(f"Sample interval    : {SAMPLE_INTERVAL_SEC} sec")
print(f"Runs / protocol    : 3")
print(f"Raw output         : {RAW_FILE}")
print(f"Summary output     : {SUMMARY_FILE}")
print("=" * 64)
print()


fieldnames = [
    "timestamp",
    "protocol",
    "run_id",
    "position_in_run",
    "sample_index",
    "worker_pid",
    "worker_cpu_percent",
    "worker_rss_bytes",
    "mosquitto_pid",
    "mosquitto_cpu_percent",
    "mosquitto_rss_bytes",
    "system_cpu_percent",
]


summary_rows = []


with RAW_FILE.open(
    "w",
    newline="",
    encoding="utf-8"
) as raw_fp:

    writer = csv.DictWriter(
        raw_fp,
        fieldnames=fieldnames
    )

    writer.writeheader()
    raw_fp.flush()

    total_blocks = 9
    completed_blocks = 0

    for run_id, order in enumerate(
        RUN_ORDERS,
        start=1
    ):

        print()
        print("=" * 64)
        print(f"RUN {run_id}/3")
        print(
            "Order: "
            + " -> ".join(order)
        )
        print("=" * 64)

        for position, protocol in enumerate(
            order,
            start=1
        ):

            print()
            print(
                f"[START] {protocol} "
                f"Run {run_id} "
                f"Position {position}/3"
            )

            command = [
                sys.executable,
                str(WORKER),
                "--protocol",
                protocol,
                "--requests",
                str(REQUESTS_PER_RUN),
                "--interval",
                str(REQUEST_INTERVAL_SEC),
            ]

            proc = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            worker = psutil.Process(
                proc.pid
            )

            # Prime CPU counters.
            worker.cpu_percent(None)
            mosquitto.cpu_percent(None)
            psutil.cpu_percent(None)

            worker_cpu_values = []
            worker_rss_values = []

            mosq_cpu_values = []
            mosq_rss_values = []

            system_cpu_values = []

            sample_index = 0

            while proc.poll() is None:

                time.sleep(
                    SAMPLE_INTERVAL_SEC
                )

                sample_index += 1

                try:
                    worker_cpu = (
                        worker.cpu_percent(None)
                    )

                    worker_rss = (
                        worker.memory_info().rss
                    )

                except psutil.NoSuchProcess:
                    worker_cpu = 0.0
                    worker_rss = 0

                try:
                    mosq_cpu = (
                        mosquitto.cpu_percent(None)
                    )

                    mosq_rss = (
                        mosquitto
                        .memory_info()
                        .rss
                    )

                except psutil.NoSuchProcess:
                    mosq_cpu = 0.0
                    mosq_rss = 0

                system_cpu = (
                    psutil.cpu_percent(None)
                )

                worker_cpu_values.append(
                    worker_cpu
                )

                worker_rss_values.append(
                    worker_rss
                )

                mosq_cpu_values.append(
                    mosq_cpu
                )

                mosq_rss_values.append(
                    mosq_rss
                )

                system_cpu_values.append(
                    system_cpu
                )

                writer.writerow({
                    "timestamp":
                        datetime.now().isoformat(),

                    "protocol":
                        protocol,

                    "run_id":
                        run_id,

                    "position_in_run":
                        position,

                    "sample_index":
                        sample_index,

                    "worker_pid":
                        proc.pid,

                    "worker_cpu_percent":
                        f"{worker_cpu:.3f}",

                    "worker_rss_bytes":
                        worker_rss,

                    "mosquitto_pid":
                        mosquitto.pid,

                    "mosquitto_cpu_percent":
                        f"{mosq_cpu:.3f}",

                    "mosquitto_rss_bytes":
                        mosq_rss,

                    "system_cpu_percent":
                        f"{system_cpu:.3f}",
                })

                raw_fp.flush()

            output, _ = proc.communicate()

            success_line = ""

            for line in output.splitlines():
                if line.startswith(
                    "RESOURCE_WORKER_DONE"
                ):
                    success_line = line

            print(
                f"[DONE] {protocol} "
                f"Run {run_id}"
            )

            if success_line:
                print(success_line)

            else:
                print(
                    "[WARNING] Worker completion "
                    "line not found"
                )

            if not worker_cpu_values:
                raise RuntimeError(
                    "No resource samples collected"
                )

            summary = {
                "protocol":
                    protocol,

                "run_id":
                    run_id,

                "position_in_run":
                    position,

                "samples":
                    len(worker_cpu_values),

                "worker_cpu_mean_percent":
                    statistics.mean(
                        worker_cpu_values
                    ),

                "worker_cpu_p95_percent":
                    percentile(
                        worker_cpu_values,
                        95
                    ),

                "worker_cpu_max_percent":
                    max(
                        worker_cpu_values
                    ),

                "worker_rss_mean_bytes":
                    statistics.mean(
                        worker_rss_values
                    ),

                "worker_rss_max_bytes":
                    max(
                        worker_rss_values
                    ),

                "mosquitto_cpu_mean_percent":
                    statistics.mean(
                        mosq_cpu_values
                    ),

                "mosquitto_cpu_p95_percent":
                    percentile(
                        mosq_cpu_values,
                        95
                    ),

                "mosquitto_cpu_max_percent":
                    max(
                        mosq_cpu_values
                    ),

                "mosquitto_rss_mean_bytes":
                    statistics.mean(
                        mosq_rss_values
                    ),

                "mosquitto_rss_max_bytes":
                    max(
                        mosq_rss_values
                    ),

                "system_cpu_mean_percent":
                    statistics.mean(
                        system_cpu_values
                    ),

                "system_cpu_p95_percent":
                    percentile(
                        system_cpu_values,
                        95
                    ),

                "worker_result":
                    success_line,
            }

            summary_rows.append(
                summary
            )

            print(
                f"Worker CPU mean : "
                f"{summary['worker_cpu_mean_percent']:.3f}%"
            )

            print(
                f"Worker RSS mean : "
                f"{summary['worker_rss_mean_bytes'] / 1024 / 1024:.3f} MiB"
            )

            print(
                f"Mosquitto CPU   : "
                f"{summary['mosquitto_cpu_mean_percent']:.3f}%"
            )

            print(
                f"Mosquitto RSS   : "
                f"{summary['mosquitto_rss_mean_bytes'] / 1024 / 1024:.3f} MiB"
            )

            print(
                f"System CPU mean : "
                f"{summary['system_cpu_mean_percent']:.3f}%"
            )

            completed_blocks += 1

            if completed_blocks < total_blocks:
                print(
                    f"Pause "
                    f"{BETWEEN_RUN_PAUSE_SEC} sec..."
                )

                time.sleep(
                    BETWEEN_RUN_PAUSE_SEC
                )


summary_fields = list(
    summary_rows[0].keys()
)

with SUMMARY_FILE.open(
    "w",
    newline="",
    encoding="utf-8"
) as summary_fp:

    writer = csv.DictWriter(
        summary_fp,
        fieldnames=summary_fields
    )

    writer.writeheader()
    writer.writerows(
        summary_rows
    )


print()
print("=" * 72)
print("FINAL RESOURCE SUMMARY")
print("=" * 72)

for protocol in [
    "http",
    "mqtt_qos0",
    "mqtt_qos1",
]:

    rows = [
        row
        for row in summary_rows
        if row["protocol"] == protocol
    ]

    worker_cpu = statistics.mean(
        row["worker_cpu_mean_percent"]
        for row in rows
    )

    worker_rss = statistics.mean(
        row["worker_rss_mean_bytes"]
        for row in rows
    )

    mosq_cpu = statistics.mean(
        row["mosquitto_cpu_mean_percent"]
        for row in rows
    )

    mosq_rss = statistics.mean(
        row["mosquitto_rss_mean_bytes"]
        for row in rows
    )

    system_cpu = statistics.mean(
        row["system_cpu_mean_percent"]
        for row in rows
    )

    print()
    print(protocol)
    print("-" * 40)

    print(
        f"Worker CPU mean   : "
        f"{worker_cpu:.3f}%"
    )

    print(
        f"Worker RSS mean   : "
        f"{worker_rss / 1024 / 1024:.3f} MiB"
    )

    print(
        f"Mosquitto CPU mean: "
        f"{mosq_cpu:.3f}%"
    )

    print(
        f"Mosquitto RSS mean: "
        f"{mosq_rss / 1024 / 1024:.3f} MiB"
    )

    print(
        f"System CPU mean   : "
        f"{system_cpu:.3f}%"
    )


print()
print(f"Raw samples : {RAW_FILE}")
print(f"Run summary : {SUMMARY_FILE}")
print()
print("Resource benchmark complete.")
