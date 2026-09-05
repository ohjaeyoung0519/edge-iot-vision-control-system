import argparse
import json
import threading
import time

HTTP_URL = "http://192.168.0.21/api/benchmark"

BROKER_HOST = "localhost"
BROKER_PORT = 1883

CMD_TOPIC = "edge/light/benchmark/cmd"
ACK_TOPIC = "edge/light/benchmark/ack"


parser = argparse.ArgumentParser()

parser.add_argument(
    "--protocol",
    required=True,
    choices=[
        "http",
        "mqtt_qos0",
        "mqtt_qos1",
    ],
)

parser.add_argument(
    "--requests",
    type=int,
    default=200,
)

parser.add_argument(
    "--interval",
    type=float,
    default=0.2,
)

args = parser.parse_args()

if args.protocol == "http":
    import urllib.parse
    import urllib.request
else:
    import paho.mqtt.client as mqtt

ack_event = threading.Event()
ack_lock = threading.Lock()

expected_command_id = None
received_ack = None


def on_connect(
    client,
    userdata,
    flags,
    reason_code,
    properties
):
    if reason_code == 0:
        client.subscribe(
            ACK_TOPIC,
            qos=1
        )


def on_message(
    client,
    userdata,
    msg
):
    global received_ack

    try:
        data = json.loads(
            msg.payload.decode("utf-8")
        )

        command_id = str(
            data.get("command_id", "")
        )

        with ack_lock:
            if command_id == expected_command_id:
                received_ack = data
                ack_event.set()

    except Exception:
        pass


def do_http(seq):
    command_id = f"resource-http-{seq}"

    query = urllib.parse.urlencode({
        "id": command_id
    })

    url = f"{HTTP_URL}?{query}"

    with urllib.request.urlopen(
        url,
        timeout=3
    ) as response:
        response.read()


def do_mqtt(
    client,
    seq,
    qos
):
    global expected_command_id
    global received_ack

    command_id = (
        f"resource-mqtt-qos{qos}-{seq}"
    )

    payload = f"{command_id}|{qos}"

    with ack_lock:
        expected_command_id = command_id
        received_ack = None

    ack_event.clear()

    info = client.publish(
        CMD_TOPIC,
        payload,
        qos=qos,
        retain=False
    )

    info.wait_for_publish(
        timeout=3
    )

    if not ack_event.wait(
        timeout=3
    ):
        raise TimeoutError(
            f"ACK timeout: {command_id}"
        )


mqtt_client = None

if args.protocol.startswith("mqtt"):

    mqtt_client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=(
            f"resource-worker-"
            f"{args.protocol}-"
            f"{int(time.time())}"
        )
    )

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(
        BROKER_HOST,
        BROKER_PORT,
        keepalive=60
    )

    mqtt_client.loop_start()

    time.sleep(1.0)


print(
    f"RESOURCE_WORKER_START "
    f"protocol={args.protocol} "
    f"requests={args.requests}"
)

success = 0

try:
    for seq in range(
        1,
        args.requests + 1
    ):

        try:
            if args.protocol == "http":
                do_http(seq)

            elif args.protocol == "mqtt_qos0":
                do_mqtt(
                    mqtt_client,
                    seq,
                    qos=0
                )

            elif args.protocol == "mqtt_qos1":
                do_mqtt(
                    mqtt_client,
                    seq,
                    qos=1
                )

            success += 1

        except Exception as e:
            print(
                f"ERROR seq={seq} "
                f"{e}"
            )

        if (
            seq == 1
            or seq % 20 == 0
            or seq == args.requests
        ):
            print(
                f"{args.protocol} "
                f"{seq}/{args.requests}"
            )

        time.sleep(
            args.interval
        )

finally:
    if mqtt_client is not None:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()


print(
    f"RESOURCE_WORKER_DONE "
    f"protocol={args.protocol} "
    f"success={success}/{args.requests}"
)
