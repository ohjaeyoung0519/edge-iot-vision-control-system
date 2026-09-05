from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

INPUT = (
    ROOT
    / "data"
    / "processed"
    / "pi_resource_summary_20260906_002151.csv"
)

OUT = ROOT / "data" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT)

labels = {
    "http": "HTTP",
    "mqtt_qos0": "MQTT QoS0",
    "mqtt_qos1": "MQTT QoS1",
}

order = [
    "http",
    "mqtt_qos0",
    "mqtt_qos1",
]

summary = (
    df.groupby("protocol")
    .mean(numeric_only=True)
    .loc[order]
)


# CPU graph
fig, ax = plt.subplots(figsize=(9, 5))

x = range(len(order))
width = 0.25

ax.bar(
    [i - width / 2 for i in x],
    summary["worker_cpu_mean_percent"],
    width=width,
    label="Python Worker"
)

ax.bar(
    [i + width / 2 for i in x],
    summary["mosquitto_cpu_mean_percent"],
    width=width,
    label="Mosquitto"
)

ax.set_xticks(
    list(x),
    [labels[p] for p in order]
)

ax.set_ylabel("Mean CPU Usage (%)")
ax.set_title("Raspberry Pi Resource Usage - CPU")
ax.legend()
ax.grid(axis="y", alpha=0.3)

fig.tight_layout()
fig.savefig(
    OUT / "pi_resource_cpu.png",
    dpi=200
)
plt.close(fig)


# RSS graph
worker_rss = (
    summary["worker_rss_mean_bytes"]
    / 1024
    / 1024
)

mosq_rss = (
    summary["mosquitto_rss_mean_bytes"]
    / 1024
    / 1024
)

fig, ax = plt.subplots(figsize=(9, 5))

ax.bar(
    [i - width / 2 for i in x],
    worker_rss,
    width=width,
    label="Python Worker"
)

ax.bar(
    [i + width / 2 for i in x],
    mosq_rss,
    width=width,
    label="Mosquitto"
)

ax.set_xticks(
    list(x),
    [labels[p] for p in order]
)

ax.set_ylabel("Mean RSS (MiB)")
ax.set_title("Raspberry Pi Resource Usage - Memory")
ax.legend()
ax.grid(axis="y", alpha=0.3)

fig.tight_layout()
fig.savefig(
    OUT / "pi_resource_rss.png",
    dpi=200
)
plt.close(fig)


print("Generated:")
print(" - data/figures/pi_resource_cpu.png")
print(" - data/figures/pi_resource_rss.png")
