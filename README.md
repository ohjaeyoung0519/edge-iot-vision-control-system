# Edge IoT Vision & Control System

## Overview

This project implements a Raspberry Pi 5 and ESP32 based edge IoT control system.

The Raspberry Pi 5 acts as a central edge control server, while ESP32 boards operate as wireless hardware control nodes for servo motor control, sensor reading, local button input, and future IR-based device control.

The goal of this project is not only to build a working IoT device, but also to analyze communication latency, control reliability, ESP32 memory usage, and hardware power stability in an embedded edge system.

## Project Goals

- Build a Raspberry Pi 5 based central control server
- Implement ESP32 based wireless hardware control nodes
- Control physical switches using servo motors
- Support remote control through Raspberry Pi
- Support local hardware input using tact switches
- Measure Raspberry Pi to ESP32 communication latency
- Monitor ESP32 free heap during repeated operation
- Test external 5V power for servo motor control
- Measure servo motor surface temperature during repeated actuation
- Use an LDR sensor for basic state verification
- Extend the system with IR communication and camera-based state recognition

## System Architecture

### Current Implemented Test Architecture

```text
MacBook / Web Browser
        |
        v
Raspberry Pi 5
Flask Server
        |
   Wi-Fi / HTTP
        |
        v
ESP32 HTTP Server
        |
        |-- MG90S Servo Motor
        |-- LDR Sensor
```

### Target Architecture

```text
Phone / Web Browser
        |
        v
Raspberry Pi 5 Edge Control Server
        |
   Wi-Fi / HTTP or MQTT
        |
        v
ESP32 Hardware Control Node
        |
        |-- Servo Motor -> Physical Switch
        |-- LDR Sensor -> Device State Check
        |-- Tact Switch -> Local Input
        |-- IR LED / IR Receiver -> IR Device Control
```

### Future Camera Extension

```text
Raspberry Pi 5
        |
        |-- Camera Module
        |
        v
Device Display / Status LED Recognition
```

The camera extension will be used to verify the actual state of a device after a command is sent, especially for one-way IR control scenarios.

## Hardware

| Component | Role |
|---|---|
| Raspberry Pi 5 8GB | Central edge server |
| ESP32-DEVKITC-32E | Wireless hardware control node |
| SG90 Servo Motor | Lightweight physical switch control |
| MG90S Servo Motor | Higher torque servo motor test |
| LDR Sensor Module | Analog light sensing and state checking |
| IR Receiver Module 38kHz | IR signal receiving |
| IR LED 940nm | IR signal transmission |
| 2N2222A NPN Transistor | IR LED driving circuit |
| 5V 5A External Power Adapter | External servo power supply |
| DC Jack Terminal | External power input connection |
| WAGO Connectors | Power distribution |
| Red / Black Power Wires | 5V and GND wiring |
| Wire Stripper | Power wire preparation |
| Tact Switch | Local button input |
| Breadboard and Jumper Wires | Circuit prototyping |
| Digital Multimeter | Voltage and continuity measurement |
| Infrared Thermometer | Servo motor surface temperature measurement |
| Raspberry Pi Camera Module | Future camera-based state recognition |

## Repository Structure

```text
docs/
├── experiment_log.md
├── hardware_list.md
└── project_plan.md

raspberry-pi/
├── scripts/
└── server/
    ├── app.py
    ├── measure_esp32_latency.py
    └── requirements.txt

esp32/
├── board_info_test/
├── wifi_test/
├── http_server_test/
├── servo_measurement_test/
├── ldr_raw_value_test/
├── ldr_threshold_test/
├── servo_ldr_measurement_test/
├── button_test/
├── ir_node/
└── servo_node/

data/
├── raw/
│   ├── esp32_latency_rpi_to_esp32_100.csv
│   └── servo_ldr_measurement_10min_raw_log.txt
│
└── processed/
    ├── esp32_latency_rpi_to_esp32_summary.csv
    ├── servo_ldr_measurement_10min_clean.csv
    ├── servo_ldr_measurement_summary.csv
    └── mg90s_temperature_summary.csv

images/
├── architecture/
├── hardware/
├── results/
├── issues/
└── wiring/

report/
└── figures/
```

## Current Status

- [x] Prepare project repository structure
- [x] Prepare hardware components
- [x] Assemble Raspberry Pi 5 case and active cooler
- [x] Install Raspberry Pi OS 64-bit
- [x] Enable Wi-Fi and SSH access
- [x] Verify headless SSH access from MacBook
- [x] Update Raspberry Pi system packages
- [x] Check Raspberry Pi temperature and throttling status
- [x] Clone GitHub repository on Raspberry Pi
- [x] Run a Flask-based test server on Raspberry Pi
- [x] Access Raspberry Pi server from MacBook browser
- [x] Set up ESP32 development environment
- [x] Verify ESP32 board information
- [x] Connect ESP32 to Wi-Fi
- [x] Run ESP32 HTTP server test
- [x] Connect Raspberry Pi server to ESP32 node
- [x] Measure Raspberry Pi to ESP32 communication latency
- [x] Control MG90S servo motor with ESP32
- [x] Test external 5V servo power with common GND
- [x] Test LDR sensor raw analog values
- [x] Measure MG90S servo motor temperature during repeated operation
- [ ] Integrate Wi-Fi, HTTP, servo, and LDR code into one ESP32 node
- [ ] Implement remote servo actuation through Raspberry Pi
- [ ] Test local button input
- [ ] Test PC power LED detection using LDR sensor
- [ ] Test external power stability using a digital multimeter
- [ ] Test IR communication
- [ ] Test camera-based state recognition
- [ ] Write final report

## Implemented Features

### Raspberry Pi Flask Server

A basic Flask server was implemented to verify that the Raspberry Pi can operate as a central server on the local network.

Implemented endpoints:

```text
GET /
GET /api/ping
GET /api/light/toggle
GET /api/esp32/ping
```

The Raspberry Pi server was successfully accessed from a MacBook browser through the Raspberry Pi local IP address and port `5000`.

This confirms the initial communication path:

```text
MacBook Browser -> Local Wi-Fi Network -> Raspberry Pi Flask Server
```

### ESP32 HTTP Server

ESP32 was configured as a Wi-Fi connected HTTP server.

The ESP32 responded to `/api/ping` requests and returned status information such as device role, uptime, free heap, and RSSI.

### Raspberry Pi to ESP32 Communication

The Raspberry Pi successfully sent HTTP requests to the ESP32 over the local Wi-Fi network.

This confirmed the control path:

```text
Raspberry Pi Flask Server -> Local Wi-Fi Network -> ESP32 HTTP Server
```

## Measurement Results

### Raspberry Pi to ESP32 Latency Test

Raspberry Pi sent 100 repeated HTTP requests to the ESP32 `/api/ping` endpoint.

| Metric | Value |
|---|---:|
| Total requests | 100 |
| Successful requests | 100 |
| Failed requests | 0 |
| Success rate | 100% |
| Minimum latency | 82.42 ms |
| Maximum latency | 126.07 ms |
| Average latency | 114.017 ms |
| Median latency | 114.56 ms |

Raw and processed data:

```text
data/raw/esp32_latency_rpi_to_esp32_100.csv
data/processed/esp32_latency_rpi_to_esp32_summary.csv
```

### MG90S Servo Motor Stability Test

A 10-minute repeated actuation test was performed using an ESP32 and an MG90S servo motor powered by an external 5V supply.

The servo motor was controlled through GPIO18, while an LDR sensor was connected to GPIO34 for analog light sensing.

| Metric | Value |
|---|---:|
| Test duration | 10 minutes |
| Total servo actuation trials | 172 |
| Servo control pin | GPIO18 |
| LDR analog input pin | GPIO34 |
| Initial free heap | 330252 bytes |
| Final free heap | 329648 bytes |
| Heap difference during each trial | 0 bytes |
| Temperature before test | 26.5°C |
| Temperature after 5 minutes | 27.6°C |
| Temperature after 10 minutes | 27.8°C |
| Temperature increase after 10 minutes | +1.3°C |

No ESP32 reset, servo failure, or overheating was observed during the test.

Raw and processed data:

```text
data/raw/servo_ldr_measurement_10min_raw_log.txt
data/processed/servo_ldr_measurement_10min_clean.csv
data/processed/servo_ldr_measurement_summary.csv
data/processed/mg90s_temperature_summary.csv
```

## Experiment Images

Representative hardware setup and result images are stored in:

```text
images/hardware/
images/results/
images/issues/
```

Example images include:

```text
images/hardware/servo_ldr_measurement_setup.jpg
images/hardware/infrared_thermometer_gm320.jpg
images/hardware/additional_power_wiring_components.jpg

images/results/mg90s_temperature_before.jpg
images/results/mg90s_temperature_5min.jpg
images/results/mg90s_temperature_10min.jpg
images/results/servo_ldr_measurement_serial_monitor.png
images/results/rpi_to_esp32_latency_100_requests.png
```

## Planned Experiments

1. Integrated ESP32 control node test
2. Raspberry Pi to ESP32 remote servo control test
3. End-to-end remote control latency measurement
4. Local button input test
5. PC power LED state detection using LDR sensor
6. External 5V power stability test using a digital multimeter
7. IR signal receive/transmit test
8. Camera-based state recognition extension

## Development Log

Detailed daily progress is recorded in:

```text
docs/experiment_log.md
```

The final report will be organized under:

```text
report/
```

## Next Steps

The next step is to implement an integrated ESP32 control node.

The integrated node will combine Wi-Fi connection, HTTP server, servo motor control, and LDR sensor reading in a single ESP32 program.

Planned ESP32 endpoints:

```text
GET /api/ping
GET /api/servo/press
GET /api/ldr
GET /api/status
```

After the integrated ESP32 node is implemented, the Raspberry Pi Flask server will be connected to the node for remote servo control and state checking.