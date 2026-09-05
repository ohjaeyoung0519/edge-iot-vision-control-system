from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = (
    ROOT
    / "data"
    / "raw"
    / "end_to_end"
)

PROCESSED_DIR = (
    ROOT
    / "data"
    / "processed"
)

FIGURES_DIR = (
    ROOT
    / "data"
    / "figures"
)

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

FIGURES_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# Load newest E2E measurement
# ============================================================

files = sorted(
    RAW_DIR.glob(
        "light_http_e2e_20_*.csv"
    )
)

if not files:
    raise FileNotFoundError(
        "No Light E2E CSV found"
    )

input_file = files[-1]

df = pd.read_csv(input_file)

success = df[
    df["status"] == "success"
].copy()

success["total_e2e_ms"] = pd.to_numeric(
    success["total_e2e_ms"]
)

success["programmed_delay_ms"] = pd.to_numeric(
    success["programmed_delay_ms"]
)

success["non_programmed_remainder_ms"] = pd.to_numeric(
    success["non_programmed_remainder_ms"]
)


# ============================================================
# Summary
# ============================================================

summary_rows = []

for action in [
    "on",
    "off",
    "all",
]:
    if action == "all":
        part = success
    else:
        part = success[
            success["action"] == action
        ]

    values = part[
        "total_e2e_ms"
    ]

    summary_rows.append({
        "action": action,
        "samples": len(values),
        "mean_e2e_ms": values.mean(),
        "median_e2e_ms": values.median(),
        "min_e2e_ms": values.min(),
        "max_e2e_ms": values.max(),
        "mean_remainder_ms": (
            part[
                "non_programmed_remainder_ms"
            ].mean()
        ),
    })


summary = pd.DataFrame(
    summary_rows
)

summary_file = (
    PROCESSED_DIR
    / "light_e2e_summary.csv"
)

summary.to_csv(
    summary_file,
    index=False
)


# ============================================================
# Figure 1: ON / OFF E2E distribution
# ============================================================

on_values = success.loc[
    success["action"] == "on",
    "total_e2e_ms"
]

off_values = success.loc[
    success["action"] == "off",
    "total_e2e_ms"
]


fig, ax = plt.subplots(
    figsize=(8, 5)
)

ax.boxplot(
    [
        on_values,
        off_values,
    ],
    tick_labels=[
        "ON",
        "OFF",
    ],
    showfliers=True,
)

ax.set_ylabel(
    "End-to-End Latency (ms)"
)

ax.set_title(
    "Light Switch End-to-End Latency"
)

ax.grid(
    axis="y",
    alpha=0.3
)

fig.tight_layout()

fig.savefig(
    FIGURES_DIR
    / "light_e2e_on_off.png",
    dpi=200
)

plt.close(fig)


# ============================================================
# Figure 2: E2E breakdown
# ============================================================

mean_total = (
    success[
        "total_e2e_ms"
    ].mean()
)

mean_programmed = (
    success[
        "programmed_delay_ms"
    ].mean()
)

mean_remainder = (
    success[
        "non_programmed_remainder_ms"
    ].mean()
)

programmed_ratio = (
    mean_programmed
    / mean_total
    * 100
)

remainder_ratio = (
    mean_remainder
    / mean_total
    * 100
)


fig, ax = plt.subplots(
    figsize=(8, 6)
)

ax.bar(
    ["Light Control"],
    [mean_programmed],
    label="Programmed Actuator Delay"
)

ax.bar(
    ["Light Control"],
    [mean_remainder],
    bottom=[mean_programmed],
    label="Non-programmed Remainder"
)


# Main 1000 ms label
ax.text(
    0,
    mean_programmed / 2,
    (
        f"{mean_programmed:.0f} ms\n"
        f"({programmed_ratio:.1f}%)"
    ),
    ha="center",
    va="center",
    fontsize=12
)


# Thin remainder section is too small for an internal label,
# so annotate it outside the bar.
ax.annotate(
    (
        f"Non-programmed remainder\n"
        f"{mean_remainder:.2f} ms "
        f"({remainder_ratio:.1f}%)"
    ),
    xy=(
        0,
        mean_programmed
        + mean_remainder / 2
    ),
    xytext=(
        0.30,
        mean_programmed + 75
    ),
    ha="left",
    va="center",
    fontsize=11,
    arrowprops={
        "arrowstyle": "->"
    }
)


# Total E2E label
ax.text(
    0,
    mean_total + 55,
    f"Total E2E: {mean_total:.2f} ms",
    ha="center",
    va="bottom",
    fontsize=13,
    fontweight="bold"
)


ax.set_ylabel(
    "Mean End-to-End Latency (ms)"
)

ax.set_title(
    "Light Control End-to-End Latency Breakdown"
)

ax.set_ylim(
    0,
    mean_total + 170
)

ax.legend(
    loc="lower left"
)

ax.grid(
    axis="y",
    alpha=0.3
)

fig.tight_layout()

fig.savefig(
    FIGURES_DIR
    / "light_e2e_breakdown.png",
    dpi=200
)

plt.close(fig)


# ============================================================
# Print result
# ============================================================

print()
print("Input:")
print(f" - {input_file}")

print()
print("Summary:")
print(
    summary.to_string(
        index=False,
        float_format=lambda x: f"{x:.3f}"
    )
)

print()
print("Generated:")
print(
    " - data/figures/"
    "light_e2e_on_off.png"
)

print(
    " - data/figures/"
    "light_e2e_breakdown.png"
)

print(
    " - data/processed/"
    "light_e2e_summary.csv"
)

print()
print("Done.")
