# Project Plan

## Project Title

Edge IoT Vision & Control System

## Objective

The objective of this project is to build an edge IoT control system using Raspberry Pi and ESP32.

The system supports local button input, remote control, servo-based physical switching, and future IR/camera-based state recognition.

## Development Phases

### Phase 1: Basic Hardware Setup

- Raspberry Pi OS setup
- ESP32 development environment setup
- GPIO and button input test
- Servo motor control test

### Phase 2: Remote Control System

- Raspberry Pi server implementation
- ESP32 wireless communication
- HTTP or MQTT based command transfer
- Mobile/web control interface

### Phase 3: Measurement and Analysis

- Command latency measurement
- Servo response reliability test
- Wi-Fi reconnection test
- External power stability test

### Phase 4: Extension

- IR receiver/transmitter test
- Air conditioner remote control experiment
- Camera-based state recognition

## Success Criteria

- ESP32 receives commands from Raspberry Pi over Wi-Fi.
- Servo motor can reliably actuate a physical switch.
- Local button input and remote command input can coexist.
- Command latency can be measured and recorded.
- External servo power is verified using a digital multimeter.