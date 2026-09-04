import csv
import json
import statistics
import threading
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

import paho.mqtt.client as mqtt


# ============================================================
# Experiment Configuration
# ============================================================

HTTP_BASE_URL = "http://192.168.0.21/api/benchmark"

BROKER_HOST = "localhost"
BROKER_PORT = 1883

MQTT_CMD_TOPIC = "edge/light/benchmark/cmd"
MQTT_ACK_TOPIC = "edge/light/benchmark/ack"

WARMUP_REQUESTS = 50
REQUESTS_PER_RUN = 200
NUM_RUNS = 5

REQUEST_INTERVAL_SEC = 0.2
BETWEEN_RUN_PAUSE_SEC = 3.0

HTTP_TIMEOUT_SEC = 3.0
MQTT_ACK_TIMEOUT_SEC = 3.0


# Interleaved / rotated measurement order
ROUND_ORDERS = [
    ["HTTP", "MQTT_QOS0", "MQTT_QOS1"],
    ["MQTT_QOS0", "MQTT_QOS1", "HTTP"],
    ["MQTT_QOS1", "HTTP", "MQTT_QOS0"],
    ["HTTP", "MQTT_QOS1", "MQTT_QOS0"],
    ["MQTT_QOS1", "MQTT_QOS0", "HTTP"],
]


# ============================================================
# Output Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SESSION_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

OUTPUT_PATHS = {
    "HTTP": (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "http"
        / f"http_main_1000_nosleep_{SESSION_ID}.csv"
    ),
    "MQTT_QOS0": (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "mqtt_qos0"
        / f"mqtt_qos0_main_1000_nosleep_{SESSION_ID}.csv"
    ),
    "MQTT_QOS1": (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "mqtt_qos1"
        / f"mqtt_qos1_main_1000_nosleep_{SESSION_ID}.csv"
    ),
}

for path in OUTPUT_PATHS.values():
    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )


FIELDNAMES = [
    "timestamp",
    "protocol",
    "run_id",
    "round_id",
    "position_in_round",
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
    "error",
]


# ============================================================
# MQTT Shared State
# ============================================================

mqtt_connected_event = threading.Event()
mqtt_ack_event = threading.Event()
mqtt_ack_lock = threading.Lock()

expected_command_id = None
received_ack = None


# ============================================================
# MQTT Callbacks
# ============================================================

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("[MQTT] Connected to broker")

        result, _ = client.subscribe(
            MQTT_ACK_TOPIC,
            qos=1
        )

        if result == mqtt.MQTT_ERR_SUCCESS:
            print(
                f"[MQTT] Subscribed: "
                f"{MQTT_ACK_TOPIC}"
            )
        else:
            print(
                f"[MQTT] Subscribe failed: "
                f"{result}"
            )

        mqtt_connected_event.set()

    else:
        print(
            f"[MQTT] Connection failed: "
            f"{reason_code}"
        )


def on_message(client, userdata, msg):
    global received_ack

    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)

        command_id = str(
            data.get("command_id", "")
        )

        with mqtt_ack_lock:
            if command_id == expected_command_id:
                received_ack = data
                mqtt_ack_event.set()

    except Exception as e:
        print(
            f"[MQTT] ACK parse error: {e}"
        )


# ============================================================
# MQTT Client
# ============================================================

mqtt_client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=f"pi-main-benchmark-{SESSION_ID}"
)

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(
    BROKER_HOST,
    BROKER_PORT,
    keepalive=60
)

mqtt_client.loop_start()

if not mqtt_connected_event.wait(timeout=5.0):
    mqtt_client.loop_stop()
    raise RuntimeError(
        "MQTT broker connection timeout"
    )

# Give subscription time to settle
time.sleep(1.0)


# ============================================================
# Measurement Functions
# ============================================================

def send_http_request(command_id):
    query = urllib.parse.urlencode({
        "id": command_id
    })

    url = f"{HTTP_BASE_URL}?{query}"

    start = time.perf_counter()

    with urllib.request.urlopen(
        url,
        timeout=HTTP_TIMEOUT_SEC
    ) as response:

        body = response.read().decode("utf-8")

    end = time.perf_counter()

    data = json.loads(body)

    returned_id = str(
        data.get("command_id", "")
    )

    if returned_id != command_id:
        raise ValueError(
            "command_id mismatch: "
            f"sent={command_id}, "
            f"received={returned_id}"
        )

    rtt_ms = (end - start) * 1000

    return rtt_ms, data


def send_mqtt_request(command_id, qos):
    global expected_command_id
    global received_ack

    payload = f"{command_id}|{qos}"

    with mqtt_ack_lock:
        expected_command_id = command_id
        received_ack = None

    mqtt_ack_event.clear()

    start = time.perf_counter()

    publish_info = mqtt_client.publish(
        MQTT_CMD_TOPIC,
        payload,
        qos=qos,
        retain=False
    )

    if publish_info.rc != mqtt.MQTT_ERR_SUCCESS:
        raise RuntimeError(
            f"MQTT publish failed: "
            f"rc={publish_info.rc}"
        )

    publish_info.wait_for_publish(
        timeout=MQTT_ACK_TIMEOUT_SEC
    )

    ack_received = mqtt_ack_event.wait(
        timeout=MQTT_ACK_TIMEOUT_SEC
    )

    end = time.perf_counter()

    if not ack_received:
        raise TimeoutError(
            f"Application ACK timeout "
            f"after {MQTT_ACK_TIMEOUT_SEC}s"
        )

    with mqtt_ack_lock:
        data = dict(received_ack)

    returned_id = str(
        data.get("command_id", "")
    )

    if returned_id != command_id:
        raise ValueError(
            "command_id mismatch: "
            f"sent={command_id}, "
            f"received={returned_id}"
        )

    rtt_ms = (end - start) * 1000

    return rtt_ms, data


def send_request(protocol, command_id):
    if protocol == "HTTP":
        return send_http_request(
            command_id
        )

    if protocol == "MQTT_QOS0":
        return send_mqtt_request(
            command_id,
            qos=0
        )

    if protocol == "MQTT_QOS1":
        return send_mqtt_request(
            command_id,
            qos=1
        )

    raise ValueError(
        f"Unknown protocol: {protocol}"
    )


# ============================================================
# Statistics Helper
# ============================================================

def percentile(values, percentile_value):
    if not values:
        return None

    sorted_values = sorted(values)

    if len(sorted_values) == 1:
        return sorted_values[0]

    k = (
        (len(sorted_values) - 1)
        * percentile_value
        / 100.0
    )

    lower = int(k)
    upper = min(
        lower + 1,
        len(sorted_values) - 1
    )

    fraction = k - lower

    return (
        sorted_values[lower]
        + (
            sorted_values[upper]
            - sorted_values[lower]
        )
        * fraction
    )


# ============================================================
# Warm-up
# ============================================================

print()
print("=" * 64)
print("Edge IoT Protocol Main Benchmark")
print("=" * 64)
print(f"Session ID       : {SESSION_ID}")
print(f"HTTP Target      : {HTTP_BASE_URL}")
print(
    f"MQTT Broker      : "
    f"{BROKER_HOST}:{BROKER_PORT}"
)
print(
    f"Warm-up          : "
    f"{WARMUP_REQUESTS} / protocol"
)
print(
    f"Main Measurement : "
    f"{REQUESTS_PER_RUN} × "
    f"{NUM_RUNS} = "
    f"{REQUESTS_PER_RUN * NUM_RUNS}"
    f" / protocol"
)
print(
    f"Interval         : "
    f"{REQUEST_INTERVAL_SEC} sec"
)
print()
print(
    "*** IMPORTANT: ESP32 Wi-Fi Sleep "
    "must remain OFF for entire experiment ***"
)
print("=" * 64)
print()


for protocol in [
    "HTTP",
    "MQTT_QOS0",
    "MQTT_QOS1"
]:

    print(
        f"[WARM-UP] {protocol} starting..."
    )

    success_count = 0

    for seq in range(
        1,
        WARMUP_REQUESTS + 1
    ):

        if protocol == "HTTP":
            command_id = (
                f"http-warmup-{seq}"
            )

        elif protocol == "MQTT_QOS0":
            command_id = (
                f"mqtt-qos0-warmup-{seq}"
            )

        else:
            command_id = (
                f"mqtt-qos1-warmup-{seq}"
            )

        try:
            send_request(
                protocol,
                command_id
            )

            success_count += 1

        except Exception as e:
            print(
                f"[WARM-UP] "
                f"{protocol} "
                f"#{seq} ERROR: {e}"
            )

        if seq % 10 == 0:
            print(
                f"[WARM-UP] "
                f"{protocol} "
                f"{seq}/{WARMUP_REQUESTS}"
            )

        time.sleep(
            REQUEST_INTERVAL_SEC
        )

    print(
        f"[WARM-UP] {protocol} complete: "
        f"{success_count}/"
        f"{WARMUP_REQUESTS}"
    )

    print()


print(
    "Warm-up complete. "
    "Main measurement starts in 3 seconds..."
)
time.sleep(3.0)


# ============================================================
# Open Raw CSV Files
# ============================================================

output_files = {}
writers = {}

for protocol, path in OUTPUT_PATHS.items():
    f = path.open(
        "w",
        newline="",
        encoding="utf-8"
    )

    writer = csv.DictWriter(
        f,
        fieldnames=FIELDNAMES
    )

    writer.writeheader()
    f.flush()

    output_files[protocol] = f
    writers[protocol] = writer


# ============================================================
# Result Storage
# ============================================================

all_rtts = {
    "HTTP": [],
    "MQTT_QOS0": [],
    "MQTT_QOS1": [],
}

attempt_counts = {
    "HTTP": 0,
    "MQTT_QOS0": 0,
    "MQTT_QOS1": 0,
}

success_counts = {
    "HTTP": 0,
    "MQTT_QOS0": 0,
    "MQTT_QOS1": 0,
}


# ============================================================
# Main Measurement
# ============================================================

try:
    total_blocks = (
        len(ROUND_ORDERS) * 3
    )

    completed_blocks = 0

    for round_id, order in enumerate(
        ROUND_ORDERS,
        start=1
    ):

        print()
        print("=" * 64)
        print(
            f"ROUND {round_id}/{NUM_RUNS}"
        )
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
                f"[ROUND {round_id}] "
                f"{protocol} "
                f"({REQUESTS_PER_RUN} requests)"
            )
            print(
                f"Position in round: {position}/3"
            )
            print("-" * 64)

            run_rtts = []
            run_success = 0

            for seq in range(
                1,
                REQUESTS_PER_RUN + 1
            ):

                attempt_counts[protocol] += 1

                if protocol == "HTTP":
                    command_id = (
                        f"http-main-"
                        f"{round_id}-{seq}"
                    )
                    qos_value = ""

                elif protocol == "MQTT_QOS0":
                    command_id = (
                        f"mqtt-qos0-main-"
                        f"{round_id}-{seq}"
                    )
                    qos_value = 0

                else:
                    command_id = (
                        f"mqtt-qos1-main-"
                        f"{round_id}-{seq}"
                    )
                    qos_value = 1

                timestamp = (
                    datetime.now().isoformat()
                )

                try:
                    rtt_ms, data = (
                        send_request(
                            protocol,
                            command_id
                        )
                    )

                    esp_processing_us = (
                        data.get(
                            "esp_processing_us"
                        )
                    )

                    free_heap = data.get(
                        "free_heap"
                    )

                    min_free_heap = data.get(
                        "min_free_heap"
                    )

                    max_alloc_heap = data.get(
                        "max_alloc_heap"
                    )

                    rssi_dbm = data.get(
                        "rssi_dbm"
                    )

                    success_counts[
                        protocol
                    ] += 1

                    run_success += 1

                    all_rtts[
                        protocol
                    ].append(rtt_ms)

                    run_rtts.append(rtt_ms)

                    writers[
                        protocol
                    ].writerow({
                        "timestamp": timestamp,
                        "protocol": protocol,
                        "run_id": round_id,
                        "round_id": round_id,
                        "position_in_round": (
                            position
                        ),
                        "seq": seq,
                        "command_id": command_id,
                        "status": "success",
                        "rtt_ms": (
                            f"{rtt_ms:.3f}"
                        ),
                        "esp_processing_us": (
                            esp_processing_us
                        ),
                        "esp_free_heap": (
                            free_heap
                        ),
                        "esp_min_free_heap": (
                            min_free_heap
                        ),
                        "esp_max_alloc_heap": (
                            max_alloc_heap
                        ),
                        "rssi_dbm": rssi_dbm,
                        "qos": qos_value,
                        "error": "",
                    })

                    # Flush every request so
                    # already-collected raw data
                    # survives an interruption.
                    output_files[
                        protocol
                    ].flush()

                    if (
                        seq == 1
                        or seq % 20 == 0
                        or seq == REQUESTS_PER_RUN
                    ):
                        print(
                            f"[{protocol} "
                            f"R{round_id} "
                            f"{seq:03d}/"
                            f"{REQUESTS_PER_RUN}] "
                            f"RTT="
                            f"{rtt_ms:.3f} ms | "
                            f"ESP="
                            f"{esp_processing_us} us | "
                            f"Heap={free_heap} | "
                            f"RSSI={rssi_dbm} dBm"
                        )

                except Exception as e:

                    writers[
                        protocol
                    ].writerow({
                        "timestamp": timestamp,
                        "protocol": protocol,
                        "run_id": round_id,
                        "round_id": round_id,
                        "position_in_round": (
                            position
                        ),
                        "seq": seq,
                        "command_id": command_id,
                        "status": "error",
                        "rtt_ms": "",
                        "esp_processing_us": "",
                        "esp_free_heap": "",
                        "esp_min_free_heap": "",
                        "esp_max_alloc_heap": "",
                        "rssi_dbm": "",
                        "qos": qos_value,
                        "error": str(e),
                    })

                    output_files[
                        protocol
                    ].flush()

                    print(
                        f"[{protocol} "
                        f"R{round_id} "
                        f"{seq:03d}] "
                        f"ERROR: {e}"
                    )

                time.sleep(
                    REQUEST_INTERVAL_SEC
                )

            print()

            if run_rtts:
                run_mean = statistics.mean(
                    run_rtts
                )

                run_median = (
                    statistics.median(
                        run_rtts
                    )
                )

                run_p95 = percentile(
                    run_rtts,
                    95
                )

                print(
                    f"[RUN SUMMARY] "
                    f"{protocol} "
                    f"Round {round_id}"
                )

                print(
                    f"Success : "
                    f"{run_success}/"
                    f"{REQUESTS_PER_RUN}"
                )

                print(
                    f"Mean    : "
                    f"{run_mean:.3f} ms"
                )

                print(
                    f"Median  : "
                    f"{run_median:.3f} ms"
                )

                print(
                    f"P95     : "
                    f"{run_p95:.3f} ms"
                )

                print(
                    f"Min     : "
                    f"{min(run_rtts):.3f} ms"
                )

                print(
                    f"Max     : "
                    f"{max(run_rtts):.3f} ms"
                )

            completed_blocks += 1

            if completed_blocks < total_blocks:
                print()
                print(
                    f"Pause "
                    f"{BETWEEN_RUN_PAUSE_SEC} sec..."
                )

                time.sleep(
                    BETWEEN_RUN_PAUSE_SEC
                )

finally:
    for f in output_files.values():
        f.flush()
        f.close()

    mqtt_client.loop_stop()
    mqtt_client.disconnect()


# ============================================================
# Final Summary
# ============================================================

print()
print()
print("=" * 72)
print("FINAL BENCHMARK SUMMARY")
print("=" * 72)


for protocol in [
    "HTTP",
    "MQTT_QOS0",
    "MQTT_QOS1"
]:

    values = all_rtts[protocol]

    print()
    print(protocol)
    print("-" * 40)

    print(
        f"Attempts : "
        f"{attempt_counts[protocol]}"
    )

    print(
        f"Success  : "
        f"{success_counts[protocol]}/"
        f"{attempt_counts[protocol]}"
    )

    if values:
        mean_value = statistics.mean(
            values
        )

        median_value = statistics.median(
            values
        )

        p95_value = percentile(
            values,
            95
        )

        p99_value = percentile(
            values,
            99
        )

        min_value = min(values)
        max_value = max(values)

        if len(values) >= 2:
            std_value = statistics.stdev(
                values
            )
        else:
            std_value = 0.0

        print(
            f"Mean     : "
            f"{mean_value:.3f} ms"
        )

        print(
            f"Median   : "
            f"{median_value:.3f} ms"
        )

        print(
            f"Std Dev  : "
            f"{std_value:.3f} ms"
        )

        print(
            f"P95      : "
            f"{p95_value:.3f} ms"
        )

        print(
            f"P99      : "
            f"{p99_value:.3f} ms"
        )

        print(
            f"Min      : "
            f"{min_value:.3f} ms"
        )

        print(
            f"Max      : "
            f"{max_value:.3f} ms"
        )


print()
print("=" * 72)
print("RAW DATA FILES")
print("=" * 72)

for protocol, path in OUTPUT_PATHS.items():
    print(
        f"{protocol:10s}: {path}"
    )

print()
print(
    "Benchmark complete. "
    "Do not delete or edit the raw CSV files."
)
