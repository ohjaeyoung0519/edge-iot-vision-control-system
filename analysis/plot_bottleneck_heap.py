from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "data" / "figures"

FIGURES.mkdir(parents=True, exist_ok=True)

SAMPLES_FILE = (
    PROCESSED
    / "protocol_samples_combined.csv"
)

SUMMARY_FILE = (
    PROCESSED
    / "protocol_summary.csv"
)


PROTOCOLS = [
    "HTTP",
    "MQTT_QOS0",
    "MQTT_QOS1",
]

LABELS = {
    "HTTP": "HTTP",
    "MQTT_QOS0": "MQTT QoS0",
    "MQTT_QOS1": "MQTT QoS1",
}


samples = pd.read_csv(SAMPLES_FILE)
summary = pd.read_csv(SUMMARY_FILE)


# ============================================================
# 1. Chronological ESP32 Free Heap
# ============================================================

samples["timestamp"] = pd.to_datetime(
    samples["timestamp"]
)

chronological = samples.sort_values(
    "timestamp"
).reset_index(drop=True)

chronological["global_request_index"] = (
    chronological.index + 1
)

chronological["heap_rolling_median"] = (
    chronological["esp_free_heap"]
    .rolling(
        window=50,
        center=True,
        min_periods=1
    )
    .median()
)


fig, ax = plt.subplots(figsize=(12, 5))

for protocol in PROTOCOLS:
    part = chronological[
        chronological["protocol_group"]
        == protocol
    ]

    ax.scatter(
        part["global_request_index"],
        part["esp_free_heap"],
        s=5,
        alpha=0.45,
        label=LABELS[protocol]
    )

ax.plot(
    chronological["global_request_index"],
    chronological["heap_rolling_median"],
    linewidth=1.5,
    label="Rolling Median (50)"
)

ax.set_xlabel(
    "Actual Measurement Sequence"
)

ax.set_ylabel(
    "ESP32 Free Heap (bytes)"
)

ax.set_title(
    "ESP32 Free Heap in Chronological Measurement Order"
)

ax.legend()
ax.grid(alpha=0.3)

fig.tight_layout()

fig.savefig(
    FIGURES
    / "free_heap_chronological.png",
    dpi=200
)

plt.close(fig)


# ============================================================
# 2. RTT Breakdown
# ============================================================

total_rtt = []
esp_processing = []
remainder = []

for protocol in PROTOCOLS:

    row = summary[
        summary["protocol"] == protocol
    ].iloc[0]

    total = float(
        row["rtt_mean_ms"]
    )

    esp = (
        float(
            row["esp_processing_mean_us"]
        )
        / 1000.0
    )

    rest = float(
        row["remainder_mean_ms"]
    )

    total_rtt.append(total)
    esp_processing.append(esp)
    remainder.append(rest)


fig, ax = plt.subplots(figsize=(9, 5))

x_labels = [
    LABELS[p]
    for p in PROTOCOLS
]

ax.bar(
    x_labels,
    remainder,
    label="Host / Network / Protocol Remainder"
)

ax.bar(
    x_labels,
    esp_processing,
    bottom=remainder,
    label="ESP32 Handler Processing"
)

for i, total in enumerate(total_rtt):
    ax.text(
        i,
        total + 1,
        f"{total:.2f} ms",
        ha="center"
    )

ax.set_ylabel(
    "Mean Application RTT (ms)"
)

ax.set_title(
    "Mean Application RTT Breakdown"
)

ax.legend()
ax.grid(
    axis="y",
    alpha=0.3
)

fig.tight_layout()

fig.savefig(
    FIGURES
    / "latency_breakdown.png",
    dpi=200
)

plt.close(fig)


print()
print("Generated:")
print(
    " - data/figures/"
    "free_heap_chronological.png"
)
print(
    " - data/figures/"
    "latency_breakdown.png"
)
print()
print("Done.")
