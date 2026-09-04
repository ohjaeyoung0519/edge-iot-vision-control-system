import csv
import json
import statistics
import threading
import time
from datetime import datetime
from pathlib import Path

import paho.mqtt.client as mqtt


# ==========================
# Experiment Configuration
# ==========================

BROKER_HOST = "localhost"
BROKER_PORT = 1883

CMD_TOPIC = "edge/light/benchmark/cmd"
ACK_TOPIC = "edge/light/benchmark/ack"

QOS = 1

NUM_REQUESTS = 30
REQUEST_INTERVAL_SEC = 0.2
ACK_TIMEOUT_SEC = 3.0

RUN_ID = 1
PROTOCOL = "MQTT_QOS1_DRYRUN"


# ==========================
# Output Configuration
# ==========================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "mqtt_qos1"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "mqtt_qos1_dryrun_30_nosleep_confirmed.csv"
)


# ==========================
# Shared ACK State
# ==========================

ack_event = threading.Event()
ack_lock = threading.Lock()

expected_command_id = None
received_ack = None


# ==========================
# MQTT Callbacks
# ==========================

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("[MQTT] Connected to broker")
        client.subscribe(ACK_TOPIC, qos=1)
    else:
        print(f"[MQTT] Connection failed: {reason_code}")


def on_message(client, userdata, msg):
    global received_ack

    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)

        command_id = str(data.get("command_id", ""))

        with ack_lock:
            if command_id == expected_command_id:
                received_ack = data
                ack_event.set()

    except Exception as e:
        print(f"[MQTT] ACK parse error: {e}")


# ==========================
# MQTT Client Setup
# ==========================

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="pi-mqtt-qos1-dryrun"
)

client.on_connect = on_connect
client.on_message = on_message

client.connect(
    BROKER_HOST,
    BROKER_PORT,
    keepalive=60
)

client.loop_start()


# Give connection/subscription a moment to settle
time.sleep(1.0)


# ==========================
# Benchmark
# ==========================

rows = []
successful_rtts = []

print()
print("=" * 38)
print("MQTT QoS1 Benchmark Dry Run")
print("=" * 38)
print(f"Broker      : {BROKER_HOST}:{BROKER_PORT}")
print(f"CMD Topic   : {CMD_TOPIC}")
print(f"ACK Topic   : {ACK_TOPIC}")
print(f"QoS         : {QOS}")
print(f"Requests    : {NUM_REQUESTS}")
print(f"Interval    : {REQUEST_INTERVAL_SEC} sec")
print(f"Output      : {OUTPUT_FILE}")
print("=" * 38)
print()


try:
    for seq in range(1, NUM_REQUESTS + 1):

        command_id = f"mqtt-qos1-dryrun-{RUN_ID}-{seq}"
        payload = f"{command_id}|{QOS}"

        with ack_lock:
            expected_command_id = command_id
            received_ack = None

        ack_event.clear()

        start = time.perf_counter()

        try:
            publish_info = client.publish(
                CMD_TOPIC,
                payload,
                qos=QOS,
                retain=False
            )

            publish_info.wait_for_publish(
                timeout=ACK_TIMEOUT_SEC
            )

            ack_received = ack_event.wait(
                timeout=ACK_TIMEOUT_SEC
            )

            end = time.perf_counter()

            if not ack_received:
                elapsed_ms = (end - start) * 1000

                rows.append({
                    "timestamp": datetime.now().isoformat(),
                    "protocol": PROTOCOL,
                    "run_id": RUN_ID,
                    "seq": seq,
                    "command_id": command_id,
                    "status": "timeout",
                    "rtt_ms": "",
                    "esp_processing_us": "",
                    "esp_free_heap": "",
                    "esp_min_free_heap": "",
                    "esp_max_alloc_heap": "",
                    "rssi_dbm": "",
                    "qos": QOS,
                    "error": f"ACK timeout after {elapsed_ms:.3f} ms"
                })

                print(
                    f"[{seq:02d}] TIMEOUT after "
                    f"{elapsed_ms:.3f} ms"
                )

            else:
                rtt_ms = (end - start) * 1000

                with ack_lock:
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

                esp_processing_us = data.get(
                    "esp_processing_us"
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

                successful_rtts.append(rtt_ms)

                rows.append({
                    "timestamp": datetime.now().isoformat(),
                    "protocol": PROTOCOL,
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
                    "qos": QOS,
                    "error": ""
                })

                print(
                    f"[{seq:02d}] "
                    f"RTT={rtt_ms:7.3f} ms | "
                    f"ESP={esp_processing_us} us | "
                    f"Heap={free_heap} | "
                    f"RSSI={rssi_dbm} dBm | "
                    f"success"
                )

        except Exception as e:
            end = time.perf_counter()
            elapsed_ms = (end - start) * 1000

            rows.append({
                "timestamp": datetime.now().isoformat(),
                "protocol": PROTOCOL,
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
                "qos": QOS,
                "error": str(e)
            })

            print(
                f"[{seq:02d}] ERROR after "
                f"{elapsed_ms:.3f} ms | {e}"
            )

        time.sleep(REQUEST_INTERVAL_SEC)

finally:
    client.loop_stop()
    client.disconnect()


# ==========================
# Save CSV
# ==========================

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


# ==========================
# Summary
# ==========================

print()
print("=" * 38)
print("MQTT QoS1 Dry Run Summary")
print("=" * 38)

print(
    f"Success: "
    f"{len(successful_rtts)}/{NUM_REQUESTS}"
)

if successful_rtts:
    print(
        f"Min RTT : "
        f"{min(successful_rtts):.3f} ms"
    )

    print(
        f"Max RTT : "
        f"{max(successful_rtts):.3f} ms"
    )

    print(
        f"Mean RTT: "
        f"{statistics.mean(successful_rtts):.3f} ms"
    )

    print(
        f"Median  : "
        f"{statistics.median(successful_rtts):.3f} ms"
    )

print()
print(f"Saved Raw Data: {OUTPUT_FILE}")
