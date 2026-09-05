from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_ROOT = PROJECT_ROOT / "data" / "raw" / "main"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


PROTOCOL_CONFIG = {
    "HTTP": {
        "dir": DATA_ROOT / "http",
        "pattern": "http_main_1000_nosleep_*.csv",
    },
    "MQTT_QOS0": {
        "dir": DATA_ROOT / "mqtt_qos0",
        "pattern": "mqtt_qos0_main_1000_nosleep_*.csv",
    },
    "MQTT_QOS1": {
        "dir": DATA_ROOT / "mqtt_qos1",
        "pattern": "mqtt_qos1_main_1000_nosleep_*.csv",
    },
}


# ============================================================
# Helpers
# ============================================================

def find_single_file(directory, pattern):
    files = sorted(directory.glob(pattern))

    if len(files) == 0:
        raise FileNotFoundError(
            f"No file found: {directory / pattern}"
        )

    if len(files) > 1:
        raise RuntimeError(
            f"Multiple matching files found in {directory}:\n"
            + "\n".join(str(f) for f in files)
        )

    return files[0]


def percentile(series, q):
    return float(np.percentile(series, q))


def safe_numeric(df, columns):
    for column in columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


# ============================================================
# Load + Validate
# ============================================================

all_frames = []

print()
print("=" * 72)
print("PROTOCOL BENCHMARK RAW DATA VALIDATION")
print("=" * 72)

for protocol, config in PROTOCOL_CONFIG.items():

    file_path = find_single_file(
        config["dir"],
        config["pattern"]
    )

    df = pd.read_csv(file_path)

    df = safe_numeric(
        df,
        [
            "run_id",
            "round_id",
            "position_in_round",
            "seq",
            "rtt_ms",
            "esp_processing_us",
            "esp_free_heap",
            "esp_min_free_heap",
            "esp_max_alloc_heap",
            "rssi_dbm",
            "qos",
        ],
    )

    print()
    print(protocol)
    print("-" * 72)
    print(f"File              : {file_path.name}")
    print(f"Rows              : {len(df)}")

    success_count = (
        df["status"].eq("success").sum()
    )

    error_count = len(df) - success_count

    print(f"Success           : {success_count}/{len(df)}")
    print(f"Errors            : {error_count}")

    unique_ids = df["command_id"].nunique()
    duplicate_ids = (
        df["command_id"].duplicated().sum()
    )

    print(f"Unique command IDs: {unique_ids}")
    print(f"Duplicate IDs     : {duplicate_ids}")

    missing_rtt = (
        df.loc[
            df["status"].eq("success"),
            "rtt_ms"
        ]
        .isna()
        .sum()
    )

    print(f"Missing success RTT: {missing_rtt}")

    print()
    print("Rows per run:")

    run_counts = (
        df.groupby("run_id")
        .size()
        .sort_index()
    )

    for run_id, count in run_counts.items():
        print(
            f"  Run {int(run_id)}: "
            f"{count}"
        )

    # Validation warnings
    warnings = []

    if len(df) != 1000:
        warnings.append(
            f"Expected 1000 rows, got {len(df)}"
        )

    if success_count != 1000:
        warnings.append(
            f"Expected 1000 successes, got {success_count}"
        )

    if unique_ids != len(df):
        warnings.append(
            "command_id is not unique"
        )

    if missing_rtt != 0:
        warnings.append(
            "Successful rows contain missing RTT"
        )

    expected_runs = {
        1: 200,
        2: 200,
        3: 200,
        4: 200,
        5: 200,
    }

    actual_runs = {
        int(k): int(v)
        for k, v in run_counts.items()
    }

    if actual_runs != expected_runs:
        warnings.append(
            f"Unexpected run distribution: {actual_runs}"
        )

    if warnings:
        print()
        print("[WARNING]")
        for warning in warnings:
            print(f"  - {warning}")
    else:
        print()
        print("[VALIDATION] PASS")

    df["protocol_group"] = protocol
    df["source_file"] = file_path.name

    all_frames.append(df)


# ============================================================
# Combine
# ============================================================

combined = pd.concat(
    all_frames,
    ignore_index=True
)

successful = combined[
    combined["status"].eq("success")
].copy()

successful["esp_processing_ms"] = (
    successful["esp_processing_us"] / 1000.0
)

# IMPORTANT:
# This is NOT "pure network latency".
#
# It contains all RTT time not included in the measured
# ESP handler processing interval:
# host + network + protocol + response handling, etc.
successful["host_network_protocol_remainder_ms"] = (
    successful["rtt_ms"]
    - successful["esp_processing_ms"]
)


# ============================================================
# Overall Protocol Summary
# ============================================================

summary_rows = []

for protocol in [
    "HTTP",
    "MQTT_QOS0",
    "MQTT_QOS1",
]:

    df = successful[
        successful["protocol_group"].eq(protocol)
    ].copy()

    rtt = df["rtt_ms"].dropna()
    esp = df["esp_processing_us"].dropna()
    remainder = (
        df[
            "host_network_protocol_remainder_ms"
        ]
        .dropna()
    )

    heap = df["esp_free_heap"].dropna()
    min_heap = df["esp_min_free_heap"].dropna()
    max_alloc = df["esp_max_alloc_heap"].dropna()
    rssi = df["rssi_dbm"].dropna()

    summary_rows.append({
        "protocol": protocol,

        "samples": len(df),

        "rtt_mean_ms": rtt.mean(),
        "rtt_median_ms": rtt.median(),
        "rtt_std_ms": rtt.std(ddof=1),
        "rtt_p95_ms": percentile(rtt, 95),
        "rtt_p99_ms": percentile(rtt, 99),
        "rtt_min_ms": rtt.min(),
        "rtt_max_ms": rtt.max(),

        "esp_processing_mean_us": esp.mean(),
        "esp_processing_median_us": esp.median(),
        "esp_processing_p95_us": percentile(
            esp,
            95
        ),
        "esp_processing_max_us": esp.max(),

        "remainder_mean_ms": remainder.mean(),
        "remainder_median_ms": remainder.median(),
        "remainder_p95_ms": percentile(
            remainder,
            95
        ),
        "remainder_p99_ms": percentile(
            remainder,
            99
        ),

        "free_heap_first_bytes": heap.iloc[0],
        "free_heap_last_bytes": heap.iloc[-1],
        "free_heap_change_bytes": (
            heap.iloc[-1] - heap.iloc[0]
        ),
        "free_heap_mean_bytes": heap.mean(),
        "free_heap_min_bytes": heap.min(),
        "free_heap_max_bytes": heap.max(),

        "min_free_heap_min_bytes": min_heap.min(),
        "min_free_heap_last_bytes": min_heap.iloc[-1],

        "max_alloc_heap_mean_bytes": max_alloc.mean(),
        "max_alloc_heap_min_bytes": max_alloc.min(),
        "max_alloc_heap_max_bytes": max_alloc.max(),

        "rssi_mean_dbm": rssi.mean(),
        "rssi_min_dbm": rssi.min(),
        "rssi_max_dbm": rssi.max(),
    })


summary_df = pd.DataFrame(summary_rows)


# ============================================================
# Per-Run Summary
# ============================================================

run_rows = []

for (
    protocol,
    run_id
), df in successful.groupby(
    [
        "protocol_group",
        "run_id"
    ]
):

    rtt = df["rtt_ms"].dropna()

    run_rows.append({
        "protocol": protocol,
        "run_id": int(run_id),
        "samples": len(df),
        "mean_ms": rtt.mean(),
        "median_ms": rtt.median(),
        "std_ms": rtt.std(ddof=1),
        "p95_ms": percentile(rtt, 95),
        "p99_ms": percentile(rtt, 99),
        "min_ms": rtt.min(),
        "max_ms": rtt.max(),
        "mean_esp_processing_us": (
            df["esp_processing_us"].mean()
        ),
        "mean_free_heap_bytes": (
            df["esp_free_heap"].mean()
        ),
        "mean_rssi_dbm": (
            df["rssi_dbm"].mean()
        ),
    })


per_run_df = pd.DataFrame(run_rows)

protocol_order = pd.CategoricalDtype(
    categories=[
        "HTTP",
        "MQTT_QOS0",
        "MQTT_QOS1",
    ],
    ordered=True,
)

per_run_df["protocol"] = (
    per_run_df["protocol"]
    .astype(protocol_order)
)

per_run_df = per_run_df.sort_values(
    [
        "protocol",
        "run_id"
    ]
)


# ============================================================
# Save Processed Results
# ============================================================

summary_path = (
    OUTPUT_DIR
    / "protocol_summary.csv"
)

per_run_path = (
    OUTPUT_DIR
    / "protocol_per_run_summary.csv"
)

combined_path = (
    OUTPUT_DIR
    / "protocol_samples_combined.csv"
)

summary_df.to_csv(
    summary_path,
    index=False
)

per_run_df.to_csv(
    per_run_path,
    index=False
)

successful.to_csv(
    combined_path,
    index=False
)


# ============================================================
# Print Results
# ============================================================

pd.set_option(
    "display.max_columns",
    None
)

pd.set_option(
    "display.width",
    200
)

print()
print()
print("=" * 72)
print("RECOMPUTED LATENCY SUMMARY")
print("=" * 72)

display_columns = [
    "protocol",
    "samples",
    "rtt_mean_ms",
    "rtt_median_ms",
    "rtt_std_ms",
    "rtt_p95_ms",
    "rtt_p99_ms",
    "rtt_min_ms",
    "rtt_max_ms",
]

print(
    summary_df[
        display_columns
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:.3f}"
    )
)


print()
print("=" * 72)
print("ESP32 PROCESSING")
print("=" * 72)

display_columns = [
    "protocol",
    "esp_processing_mean_us",
    "esp_processing_median_us",
    "esp_processing_p95_us",
    "esp_processing_max_us",
]

print(
    summary_df[
        display_columns
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:.3f}"
    )
)


print()
print("=" * 72)
print("HOST / NETWORK / PROTOCOL REMAINDER")
print("=" * 72)
print(
    "NOTE: This is RTT - measured ESP processing."
)
print(
    "It must NOT be interpreted as pure network latency."
)

display_columns = [
    "protocol",
    "remainder_mean_ms",
    "remainder_median_ms",
    "remainder_p95_ms",
    "remainder_p99_ms",
]

print(
    summary_df[
        display_columns
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:.3f}"
    )
)


print()
print("=" * 72)
print("ESP32 HEAP SUMMARY")
print("=" * 72)

display_columns = [
    "protocol",
    "free_heap_first_bytes",
    "free_heap_last_bytes",
    "free_heap_change_bytes",
    "free_heap_mean_bytes",
    "free_heap_min_bytes",
    "free_heap_max_bytes",
    "min_free_heap_min_bytes",
    "max_alloc_heap_mean_bytes",
]

print(
    summary_df[
        display_columns
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:.1f}"
    )
)


print()
print("=" * 72)
print("PER-RUN LATENCY SUMMARY")
print("=" * 72)

print(
    per_run_df[
        [
            "protocol",
            "run_id",
            "samples",
            "mean_ms",
            "median_ms",
            "p95_ms",
            "p99_ms",
            "min_ms",
            "max_ms",
        ]
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:.3f}"
    )
)


print()
print("=" * 72)
print("OUTPUT FILES")
print("=" * 72)
print(f"Overall summary : {summary_path}")
print(f"Per-run summary : {per_run_path}")
print(f"Combined samples: {combined_path}")
print()
print("Analysis complete.")
