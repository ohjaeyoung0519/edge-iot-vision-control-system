# Edge IoT Vision & Control System

## Overview

This project implements a Raspberry Pi and ESP32 based edge IoT control system.

The Raspberry Pi acts as a central server, while ESP32 boards operate as wireless control nodes for servo motor control, local button input, and infrared communication.

The goal of this project is not only to build a working IoT device, but also to analyze communication latency, control reliability, and power stability in an embedded edge system.

## Goals

- Build a Raspberry Pi based central control server
- Implement ESP32 based wireless actuator nodes
- Control a physical switch using a servo motor
- Support both local button input and remote control
- Measure command latency between Raspberry Pi and ESP32
- Analyze power stability when using external servo power
- Extend the system with IR communication and camera-based state recognition

## System Architecture

```text
Phone / Web Browser
        |
        v
Raspberry Pi 5 Server
        |
   Wi-Fi / MQTT
        |
        v
ESP32 Control Node
   |       |       |
 Servo   Button   IR Module
```

## Hardware

- Raspberry Pi 5 8GB
- ESP32-DEVKITC-32E
- SG90 Servo Motor
- MG90S Servo Motor
- IR Receiver Module 38kHz
- IR LED 940nm
- 2N2222A NPN Transistor
- 5V 5A External Power Adapter
- Tact Switch
- Breadboard and jumper wires
- Digital Multimeter

## Current Status

- [x] Hardware ordered
- [x] Raspberry Pi received
- [ ] ESP32 received
- [ ] Raspberry Pi OS setup
- [ ] ESP32 development environment setup
- [ ] Servo motor control test
- [ ] Local button input test
- [ ] Remote control test
- [ ] Latency measurement
- [ ] IR communication test
- [ ] Final report

## Planned Experiments

1. Servo control test
2. Local button input test
3. Raspberry Pi to ESP32 communication test
4. Remote control latency measurement
5. External power stability test
6. IR signal receive/transmit test
7. Camera-based state recognition extension

## Repository Structure

```text
docs/           Project documents and report drafts
raspberry-pi/   Raspberry Pi server scripts
esp32/          ESP32 firmware projects
data/           Experiment data and CSV logs
images/         Hardware, wiring, architecture, and result images
report/         Final PDF report and figures
```