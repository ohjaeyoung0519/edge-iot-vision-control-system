# Edge IoT Vision & Control System

## Overview

This project implements a Raspberry Pi and ESP32 based edge IoT control system.

The Raspberry Pi 5 acts as a central server, while ESP32 boards operate as wireless control nodes for servo motor control, local button input, and infrared communication.

The goal of this project is not only to build a working IoT device, but also to analyze communication latency, control reliability, and power stability in an embedded edge system.

## Project Goals

- Build a Raspberry Pi based central control server
- Implement ESP32 based wireless actuator nodes
- Control a physical switch using a servo motor
- Support both local button input and remote control
- Measure command latency between Raspberry Pi and ESP32
- Analyze power stability when using external servo power
- Extend the system with IR communication and camera-based state recognition

## System Architecture

### Current Test Architecture

```text
MacBook / Web Browser
        |
        v
Raspberry Pi 5
Flask Test Server
        |
        v
HTTP Response
```

### Target Architecture

```text
Phone / Web Browser
        |
        v
Raspberry Pi 5 Central Server
        |
   Wi-Fi / HTTP or MQTT
        |
        v
ESP32 Control Node
   |       |       |
 Servo   Button   IR Module
```

## Hardware

| Component | Role |
|---|---|
| Raspberry Pi 5 8GB | Central server |
| ESP32-DEVKITC-32E | Wireless control node |
| SG90 Servo Motor | Physical switch control |
| MG90S Servo Motor | Higher torque servo test |
| IR Receiver Module 38kHz | IR signal receiving |
| IR LED 940nm | IR signal transmission |
| 2N2222A NPN Transistor | IR LED driving circuit |
| 5V 5A External Power Adapter | External servo power |
| Tact Switch | Local button input |
| Breadboard and Jumper Wires | Circuit prototyping |
| Digital Multimeter | Voltage and continuity measurement |

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
- [ ] Set up ESP32 development environment
- [ ] Run ESP32 Blink test
- [ ] Connect ESP32 to Wi-Fi
- [ ] Control servo motor with ESP32
- [ ] Connect Raspberry Pi server to ESP32 node
- [ ] Test local button input
- [ ] Measure command latency
- [ ] Test external servo power stability
- [ ] Test IR communication
- [ ] Write final report

## Raspberry Pi Server Test

A basic Flask server was implemented to verify that the Raspberry Pi can operate as a central server on the local network.

Implemented endpoints:

```text
GET /
GET /api/ping
GET /api/light/toggle
```

The server was successfully accessed from a MacBook browser through the Raspberry Pi local IP address and port `5000`.

This confirms the initial communication path:

```text
MacBook Browser -> Local Wi-Fi Network -> Raspberry Pi Flask Server
```

## Planned Experiments

1. Raspberry Pi server test
2. ESP32 Blink test
3. ESP32 Wi-Fi connection test
4. Servo motor control test
5. Local button input test
6. Raspberry Pi to ESP32 communication test
7. Remote control latency measurement
8. External power stability test
9. IR signal receive/transmit test
10. Camera-based state recognition extension

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
    └── requirements.txt

esp32/
├── button_test/
├── ir_node/
└── servo_node/

data/

images/
├── architecture/
├── hardware/
├── results/
└── wiring/

report/
└── figures/
```

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

The next step is to set up the ESP32 development environment and run the first Blink test. After that, the ESP32 will be connected to Wi-Fi and used as a wireless control node for servo motor control.