# Experiment Data

This directory contains raw measurements, processed datasets, and figures generated during the performance and bottleneck analysis of the **Edge IoT Vision & Control System**.

The experiments were performed using a Raspberry Pi 5 and ESP32 over a local Wi-Fi network.

---

## Directory Structure

```text
data/
├── raw/
│   ├── main/
│   │   ├── http/
│   │   ├── mqtt_qos0/
│   │   ├── mqtt_qos1/
│   │   ├── resource/
│   │   └── end_to_end/
│   │
│   ├── diagnostic/
│   │   ├── dryrun/
│   │   ├── wifi_sleep/
│   │   └── resource/
│   │
│   ├── excluded/
│   │   ├── keepalive/
│   │   └── uncertain_condition/
│   │
│   └── legacy/
│       └── http_latency/
│
├── processed/
│   ├── diagnostic/
│   └── *.csv
│
└── figures/
```

---

## 1. Main Protocol Benchmark

`raw/main/` contains the datasets used for the final analysis.

The final protocol benchmark compares:

- HTTP
- MQTT QoS 0
- MQTT QoS 1

### Measurement Configuration

- ESP32 Wi-Fi Sleep: **OFF**
- Warm-up: **50 requests per protocol**
- Main measurement: **200 requests × 5 runs**
- Total: **1000 measured requests per protocol**
- Request interval: **0.2 s**
- Sequential request / response measurement
- Protocol order interleaved across runs

The five run orders were:

```text
Run 1: HTTP      -> MQTT QoS0 -> MQTT QoS1
Run 2: MQTT QoS0 -> MQTT QoS1 -> HTTP
Run 3: MQTT QoS1 -> HTTP      -> MQTT QoS0
Run 4: HTTP      -> MQTT QoS1 -> MQTT QoS0
Run 5: MQTT QoS1 -> MQTT QoS0 -> HTTP
```

### Total Main Samples

```text
HTTP       : 1000
MQTT QoS0  : 1000
MQTT QoS1  : 1000
Total      : 3000
```

All **3000/3000** measured requests completed successfully.

### Final Application RTT Results

| Protocol | Mean | Median | Std Dev | P95 | P99 | Min | Max |
|---|---:|---:|---:|---:|---:|---:|---:|
| HTTP | 20.515 ms | 19.450 ms | 4.377 ms | 28.807 ms | 37.038 ms | 13.100 ms | 47.467 ms |
| MQTT QoS0 | 15.319 ms | 13.988 ms | 4.820 ms | 22.980 ms | 31.076 ms | 8.297 ms | 62.187 ms |
| MQTT QoS1 | 61.282 ms | 59.508 ms | 8.360 ms | 79.849 ms | 94.444 ms | 12.318 ms | 105.922 ms |

The measured value is **application-level round-trip time (RTT)**.

It must not be interpreted as pure network propagation latency.

---

## 2. ESP32 Handler Processing

The benchmark endpoint also recorded processing time inside the ESP32 benchmark handler.

### Mean Processing Time

| Protocol | Mean ESP32 Processing |
|---|---:|
| HTTP | 401.999 µs |
| MQTT QoS0 | 419.632 µs |
| MQTT QoS1 | 420.765 µs |

The ESP32 processing interval represents the measured handler-side work before response or MQTT application ACK transmission.

For analysis, the following value was also calculated:

```text
Host / Network / Protocol Remainder
= Application RTT - ESP32 Measured Processing Time
```

Mean values were approximately:

| Protocol | Mean Remainder |
|---|---:|
| HTTP | 20.113 ms |
| MQTT QoS0 | 14.900 ms |
| MQTT QoS1 | 60.862 ms |

This remainder includes multiple components such as host-side processing, network transport, protocol handling, and response processing.

It is **not pure network latency**.

---

## 3. ESP32 Heap Measurements

Each protocol request recorded:

- Free Heap
- Minimum Free Heap
- Maximum Allocatable Heap
- Wi-Fi RSSI

Heap measurements were later reconstructed in **chronological measurement order** using their timestamps.

During the 3000-request benchmark, ESP32 free heap moved between several runtime levels but did not show a continuous downward trend across the complete experiment.

Therefore, the result is stated conservatively as:

> No cumulative free-heap decrease was observed within the scope of the benchmark.

This does **not** prove the complete absence of memory leaks under all possible runtime conditions.

---

## 4. Raspberry Pi Resource Benchmark

The final Raspberry Pi resource measurement is stored under:

```text
raw/main/resource/
```

Each protocol was tested using:

- 200 requests per run
- 3 runs per protocol
- 0.2 s request interval
- Interleaved protocol order
- 0.2 s resource sampling interval

The run orders were:

```text
Run 1: HTTP      -> MQTT QoS0 -> MQTT QoS1
Run 2: MQTT QoS0 -> MQTT QoS1 -> HTTP
Run 3: MQTT QoS1 -> HTTP      -> MQTT QoS0
```

### Measured Resources

- Python worker CPU usage
- Python worker RSS
- Mosquitto CPU usage
- Mosquitto RSS
- Raspberry Pi system CPU usage

### Final Averaged Results

| Protocol | Worker CPU | Worker RSS | Mosquitto CPU | Mosquitto RSS |
|---|---:|---:|---:|---:|
| HTTP | 0.429% | 23.165 MiB | 0.008% | 8.406 MiB |
| MQTT QoS0 | 0.397% | 23.371 MiB | 0.037% | 8.406 MiB |
| MQTT QoS1 | 0.403% | 23.389 MiB | 0.043% | 8.406 MiB |

The CPU values represent average usage over the complete benchmark workload, including the configured request interval.

They should **not** be interpreted as per-request CPU cost.

The final resource benchmark used protocol-specific Python imports so that the worker RSS comparison was cleaner.

---

## 5. Light Switch End-to-End Latency

The physical Light Switch End-to-End dataset is stored under:

```text
raw/main/end_to_end/
```

The experiment executed:

```text
ON  : 10
OFF : 10

Total Actuations: 20
```

All 20 API requests completed successfully.

### Measured Results

| Metric | Value |
|---|---:|
| ON Mean | 1032.498 ms |
| OFF Mean | 1031.995 ms |
| Overall Mean | 1032.247 ms |
| Overall Median | 1031.450 ms |
| Minimum | 1028.087 ms |
| Maximum | 1040.075 ms |

The Light Switch actuator sequence contains:

```text
Servo Press Hold  : 400 ms
Servo Return Wait : 600 ms

Total Programmed Delay = 1000 ms
```

Therefore:

```text
Measured Mean E2E
= 1032.247 ms

Programmed Actuator Delay
= 1000 ms
≈ 96.9%

Non-programmed Remainder
≈ 32.247 ms
≈ 3.1%
```

The non-programmed remainder includes:

- Raspberry Pi request handling
- Wi-Fi / TCP / HTTP communication
- ESP32 handler execution
- Servo command execution
- Response generation
- Response reception

It is **not pure network latency**.

---

## 6. Physical Actuation Reliability

The Light Switch actuator was also evaluated separately for physical reliability.

### Initial Configuration

The original MG90S-based configuration achieved:

```text
Success: 7 / 20
Success Rate: 35%
```

### Final Configuration

After changing the actuator and improving the physical installation and angle calibration:

```text
ON  : 20 / 20
OFF : 20 / 20

Total: 40 / 40
Success Rate: 100%
```

The final Light Switch configuration used:

```text
Servo: MG996R

REST angle : 90°
ON angle   : 50°
OFF angle  : 140°

Press Hold : 400 ms
Return Wait: 600 ms
```

The reliability improvement should not be attributed only to servo torque.

The final configuration combined:

- Higher-torque actuator
- Improved mechanical mounting
- Control-angle calibration

---

## 7. Wi-Fi Sleep Diagnostic

Diagnostic measurements are stored under:

```text
raw/diagnostic/wifi_sleep/
```

During initial MQTT testing, many requests showed Application RTT values near 100 ms.

A controlled comparison of the ESP32 Wi-Fi power-saving configuration was therefore performed.

The final firmware disabled Wi-Fi sleep using:

```cpp
WiFi.setSleep(false);
```

A confirmed MQTT QoS0 dry run with Wi-Fi Sleep enabled produced substantially higher RTT values.

A confirmed Wi-Fi Sleep OFF run reduced latency to approximately the 10–20 ms range.

The final 1000-request MQTT QoS0 benchmark reproduced this lower-latency behavior with a mean RTT of:

```text
15.319 ms
```

Therefore, ESP32 Wi-Fi power-saving behavior was identified as an important latency factor in this system.

The final protocol benchmark used **Wi-Fi Sleep OFF for all protocol conditions**.

---

## 8. Diagnostic Data

`raw/diagnostic/` contains measurements generated during implementation, debugging, and controlled hypothesis testing.

These datasets are preserved for reproducibility but are not mixed into the final protocol benchmark statistics.

### Dry Runs

```text
raw/diagnostic/dryrun/
```

contains small-scale 10-request and 30-request experiments used to verify:

- Endpoint functionality
- MQTT command / ACK behavior
- CSV logging
- Timing behavior
- Experimental scripts

### Resource Diagnostic

```text
raw/diagnostic/resource/
```

contains the preliminary Raspberry Pi resource benchmark.

The first resource worker loaded both HTTP-related and MQTT-related Python modules in the same process.

The final resource benchmark was repeated using protocol-specific imports, and only the corrected measurement is used as the final resource result.

---

## 9. Excluded Data

`raw/excluded/` contains measurements that were intentionally excluded from the final statistical analysis.

These datasets are preserved to document why they were rejected instead of silently deleting them.

### Keep-Alive Experiment

The HTTP Keep-Alive experiment is stored under:

```text
raw/excluded/keepalive/
```

During verification, the ESP32 HTTP server returned:

```text
Connection: close
```

and the client log showed dropped connections being recreated.

Therefore, the measured condition did not represent a true persistent HTTP connection and was excluded from the final protocol comparison.

### Uncertain Wi-Fi Condition

One MQTT QoS0 diagnostic run is stored under:

```text
raw/excluded/uncertain_condition/
```

At the time of that measurement, it was uncertain whether the ESP32 firmware containing:

```cpp
WiFi.setSleep(false);
```

had actually been uploaded.

Because the experimental condition could not be verified, that dataset was excluded from final analysis.

---

## 10. Legacy Data

Earlier development-stage measurements are stored under:

```text
raw/legacy/
```

These measurements may use:

- Older firmware
- Older endpoints
- Different ESP32 IP addresses
- Different network conditions
- Different benchmark implementations

They are retained as historical implementation records and are not directly compared with the final benchmark.

---

## 11. Processed Data

`processed/` contains datasets derived from raw measurements.

Important processed files include:

```text
protocol_summary.csv
protocol_per_run_summary.csv
protocol_samples_combined.csv

pi_resource_summary_20260906_002151.csv

light_e2e_summary.csv
```

The raw CSV files remain the **source of truth**.

Processed files can be regenerated using the scripts under:

```text
analysis/
```

---

## 12. Figures

`figures/` contains visualizations generated from the benchmark datasets.

Major figures include:

```text
latency_boxplot.png
latency_percentiles.png
latency_sequence.png
per_run_mean_latency.png

esp_processing_mean.png
latency_breakdown.png
free_heap_chronological.png

pi_resource_cpu.png
pi_resource_rss.png

light_e2e_on_off.png
light_e2e_breakdown.png
```

These figures visualize:

- Application RTT distribution
- Median / P95 / P99 latency
- Run-to-run repeatability
- Request-sequence latency behavior
- ESP32 handler processing
- Host / Network / Protocol remainder
- ESP32 Free Heap behavior
- Raspberry Pi CPU and memory usage
- Physical Light Switch End-to-End latency
- Actuator-dominated End-to-End bottleneck

---

## 13. Reproducibility

Analysis and plotting scripts are stored under:

```text
analysis/
```

Benchmark execution scripts are stored under:

```text
raspberry-pi/server/
raspberry-pi/server/benchmarks/
```

The repository preserves:

- Final datasets
- Diagnostic datasets
- Explicitly excluded datasets
- Processed summaries
- Analysis scripts
- Generated figures

so that the reasoning behind the final results can be traced back to the original measurements.
