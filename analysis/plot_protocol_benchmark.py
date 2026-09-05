from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "data" / "figures"

FIGURES.mkdir(parents=True, exist_ok=True)


SUMMARY_FILE = PROCESSED / "protocol_summary.csv"
RUN_FILE = PROCESSED / "protocol_per_run_summary.csv"
SAMPLES_FILE = PROCESSED / "protocol_samples_combined.csv"


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


summary = pd.read_csv(SUMMARY_FILE)
runs = pd.read_csv(RUN_FILE)
samples = pd.read_csv(SAMPLES_FILE)


# ============================================================
# Prepare sample order
# ============================================================

samples = samples.sort_values(
    ["protocol_group", "run_id", "seq"]
).copy()

samples["sample_index"] = (
    samples.groupby("protocol_group")
    .cumcount()
    + 1
)


# ============================================================
# 1. RTT Boxplot
# ============================================================

box_data = [
    samples.loc[
        samples["protocol_group"] == protocol,
        "rtt_ms"
    ].dropna()
    for protocol in PROTOCOLS
]

fig, ax = plt.subplots(figsize=(8, 5))

ax.boxplot(
    box_data,
    tick_labels=[LABELS[p] for p in PROTOCOLS],
    showfliers=True
)

ax.set_title("Application RTT Distribution")
ax.set_ylabel("RTT (ms)")
ax.grid(axis="y", alpha=0.3)

fig.tight_layout()

fig.savefig(
    FIGURES / "latency_boxplot.png",
    dpi=200
)

plt.close(fig)


# ============================================================
# 2. Median / P95 / P99
# ============================================================

metric_names = [
    "rtt_median_ms",
    "rtt_p95_ms",
    "rtt_p99_ms",
]

metric_labels = [
    "Median",
    "P95",
    "P99",
]

x = range(len(PROTOCOLS))

fig, ax = plt.subplots(figsize=(9, 5))

width = 0.24

for i, (metric, label) in enumerate(
    zip(metric_names, metric_labels)
):
    values = []

    for protocol in PROTOCOLS:
        row = summary[
            summary["protocol"] == protocol
        ]

        values.append(
            float(row.iloc[0][metric])
        )

    positions = [
        value + (i - 1) * width
        for value in x
    ]

    ax.bar(
        positions,
        values,
        width=width,
        label=label
    )

ax.set_xticks(
    list(x),
    [LABELS[p] for p in PROTOCOLS]
)

ax.set_ylabel("RTT (ms)")
ax.set_title("Latency Percentile Comparison")
ax.legend()
ax.grid(axis="y", alpha=0.3)

fig.tight_layout()

fig.savefig(
    FIGURES / "latency_percentiles.png",
    dpi=200
)

plt.close(fig)


# ============================================================
# 3. RTT over request sequence
# ============================================================

fig, ax = plt.subplots(figsize=(10, 5))

for protocol in PROTOCOLS:

    part = samples[
        samples["protocol_group"] == protocol
    ]

    ax.plot(
        part["sample_index"],
        part["rtt_ms"],
        label=LABELS[protocol],
        linewidth=0.8,
        alpha=0.8
    )

ax.set_xlabel("Request Sequence")
ax.set_ylabel("RTT (ms)")
ax.set_title("RTT over Request Sequence")
ax.legend()
ax.grid(alpha=0.3)

fig.tight_layout()

fig.savefig(
    FIGURES / "latency_sequence.png",
    dpi=200
)

plt.close(fig)


# ============================================================
# 4. ESP processing time
# ============================================================

esp_values = []

for protocol in PROTOCOLS:
    row = summary[
        summary["protocol"] == protocol
    ]

    esp_values.append(
        float(
            row.iloc[0][
                "esp_processing_mean_us"
            ]
        )
        / 1000.0
    )

fig, ax = plt.subplots(figsize=(8, 5))

ax.bar(
    [LABELS[p] for p in PROTOCOLS],
    esp_values
)

ax.set_ylabel("ESP32 Processing Time (ms)")
ax.set_title("Mean ESP32 Handler Processing Time")
ax.grid(axis="y", alpha=0.3)

fig.tight_layout()

fig.savefig(
    FIGURES / "esp_processing_mean.png",
    dpi=200
)

plt.close(fig)


# ============================================================
# 5. Free Heap over request sequence
# ============================================================

fig, ax = plt.subplots(figsize=(10, 5))

for protocol in PROTOCOLS:

    part = samples[
        samples["protocol_group"] == protocol
    ]

    ax.plot(
        part["sample_index"],
        part["esp_free_heap"],
        label=LABELS[protocol],
        linewidth=0.8
    )

ax.set_xlabel("Request Sequence")
ax.set_ylabel("ESP32 Free Heap (bytes)")
ax.set_title("ESP32 Free Heap over Request Sequence")
ax.legend()
ax.grid(alpha=0.3)

fig.tight_layout()

fig.savefig(
    FIGURES / "free_heap_sequence.png",
    dpi=200
)

plt.close(fig)


# ============================================================
# 6. Mean RTT per run
# ============================================================

fig, ax = plt.subplots(figsize=(8, 5))

for protocol in PROTOCOLS:

    part = runs[
        runs["protocol"] == protocol
    ].sort_values("run_id")

    ax.plot(
        part["run_id"],
        part["mean_ms"],
        marker="o",
        label=LABELS[protocol]
    )

ax.set_xticks([1, 2, 3, 4, 5])
ax.set_xlabel("Run")
ax.set_ylabel("Mean RTT (ms)")
ax.set_title("Mean RTT per 200-Request Run")
ax.legend()
ax.grid(alpha=0.3)

fig.tight_layout()

fig.savefig(
    FIGURES / "per_run_mean_latency.png",
    dpi=200
)

plt.close(fig)


print()
print("Generated figures:")

for path in sorted(FIGURES.glob("*.png")):
    print(f" - {path}")

print()
print("Plot generation complete.")
