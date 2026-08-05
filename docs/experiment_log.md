## 2026-07-24

### 작업 내용

GitHub 저장소 기본 구조를 만들고 README 작성함.

### 결과

프로젝트 개요, 목표, 하드웨어 목록, 실험 계획을 정리함.

### 문제점

아직 없음.

### 다음 작업

Raspberry Pi OS 설치 및 SSH 접속 테스트

## 2026-07-25

### 작업 내용
Raspberry Pi Imager를 사용해 Raspberry Pi OS 64-bit를 microSD 카드에 설치함.
호스트 이름은 `edge-pi`, 사용자 이름은 `jaeyoung`으로 설정함, Wi-Fi와 SSH를 활성화함.

MacBook에서 SSH를 통해 Raspberry Pi에 접속, 시스템 업데이트 및 재부팅을 완료함.
이후 HDMI를 제거한 상태에서도 SSH로 정상 접속되는 것을 확인함.

Flask 기반 테스트 서버를 Raspberry Pi에서 실행함, MacBook 브라우저에서 `http://192.168.0.35:5000` 주소로 접속되는 것을 확인함.

### 결과
Raspberry Pi 5가 중앙 서버로 동작할 수 있음을 확인함.

### 확인한 값
- Hostname: `edge-pi`
- IP address: `192.168.0.35`
- CPU temperature: 약 46도
- Throttling status: `throttled=0x0`
- Python version: 3.13.5
- Git version: 2.47.3

### 발생한 문제 및 해결
GitHub 저장소가 private 상태라 Raspberry Pi에서 clone 시 인증을 요구함. 저장소를 public으로 변경한 뒤 정상적으로 clone을 완료함.

### 다음 작업
ESP32 개발환경을 설정하고, Blink 테스트 및 Wi-Fi 연결 테스트를 진행

## 2026-07-27

### 작업 내용
프로젝트 보고서의 전체 틀을 구성함. 기존 과제 보고서 형식과 유사하게 표지, 목차, 프로젝트 개요, 개발 환경, 구현 과정, 실험 결과, 문제 해결 과정, 향후 개선 방향으로 구성하기로 함.

보고서 작성 도구는 Google Docs를 사용하기로 결정함. 본 프로젝트처럼 사진, 실험 과정, 구현 기록, 문제 해결 과정을 많이 포함하는 기술 보고서에는 Google Docs가 더 적합하다고 판단함.

### 정리한 보고서 방향
본 프로젝트는 단순한 IoT 제어 기능 구현이 아니라, Raspberry Pi와 ESP32를 이용한 엣지 IoT 제어 시스템을 구성하고, 제한된 하드웨어 환경에서 통신 지연시간, CPU 및 메모리 사용량, 전원 안정성 등을 측정하는 방향으로 정리하기로 함.

Raspberry Pi는 일반 데스크톱이나 노트북이 아닌 엣지 제어 서버로 사용하고, ESP32는 실제 하드웨어 제어를 담당하는 무선 제어 노드로 사용하기로 함. 이를 통해 클라이언트 요청이 Raspberry Pi를 거쳐 ESP32로 전달되고, 실제 하드웨어 제어로 이어지는 전체 제어 경로를 구성하는 것을 목표로 함.

### 결과
보고서의 큰 목차와 작성 방향을 정리함. 이후 실험 과정에서 발생하는 질문과 결과는 단순 메모로 남기지 않고, 보고서의 설계 이유, 구현 과정, 실험 결과 해석, 문제 해결 과정에 반영하기로 함.

### 다음 작업
Raspberry Pi 초기 설정과 서버 구성 과정을 보고서에 정리하고, 이후 ESP32 개발환경 설정 및 통신 실험 결과를 추가함.

## 2026-07-29

### 작업 내용
Raspberry Pi 초기 설정 및 서버 구성 과정을 최종 보고서에 정리함. Raspberry Pi OS 설치, Wi-Fi 및 SSH 설정, headless 접속 환경 구성, 시스템 업데이트, 온도 및 throttling 상태 확인, Flask 기반 테스트 서버 실행 과정을 보고서 형식으로 작성함.

Raspberry Pi를 일반 컴퓨터가 아니라 엣지 제어 서버로 사용한 이유를 정리함. Raspberry Pi는 GPIO, 카메라 인터페이스, 저전력 동작, 소형 폼팩터를 제공하므로 실제 하드웨어 제어와 엣지 장치 실험을 수행하기에 적합하다고 작성함.

### 보고서에 정리한 주요 내용
- Raspberry Pi 5를 엣지 제어 서버로 사용하는 이유
- Raspberry Pi OS 설치 및 초기 설정 과정
- SSH를 이용한 headless 접속 환경 구성
- HDMI 제거 후 원격 접속으로 Raspberry Pi를 제어한 과정
- Flask 기반 테스트 서버 실행 과정
- 동일 네트워크의 클라이언트 브라우저에서 Raspberry Pi 서버 접속을 확인한 결과
- Raspberry Pi 온도 및 throttling 상태 확인 결과
- Raspberry Pi가 중앙 제어 서버로 동작하기 위한 기반 구성

### 결과
Raspberry Pi 단독 서버 구성 과정까지 보고서에 정리함. 이 단계에서는 Raspberry Pi가 클라이언트 요청을 수신하고 응답할 수 있음을 확인하였으며, 이후 ESP32와 연결하여 실제 하드웨어 제어 노드와 통신하는 구조로 확장할 수 있는 기반을 마련함.

### 다음 작업
ESP32 개발환경을 설정하고, ESP32 보드 정보 확인, Wi-Fi 연결, HTTP server 실행, Raspberry Pi와 ESP32 간 통신 테스트를 진행함.

## 2026-07-30

### 작업 내용
ESP32 개발환경을 설정하고 Raspberry Pi와 ESP32 간 통신 실험을 진행함. Arduino IDE에서 ESP32 보드 패키지를 설치하고, ESP32 Dev Module과 `/dev/cu.usbserial-130` 포트를 선택하여 테스트 코드를 업로드함.

먼저 ESP32 보드 정보 출력 테스트를 수행하여 칩 모델, CPU core 수, CPU 동작 주파수, flash memory 크기, free heap 값을 확인함. 이후 ESP32를 Wi-Fi에 연결하고 IP 주소, RSSI, Wi-Fi 연결 전후의 free heap 변화를 확인함.

다음으로 ESP32에서 HTTP server를 실행하고, 브라우저에서 ESP32의 `/api/ping` endpoint에 접속하여 JSON 응답이 정상적으로 반환되는 것을 확인함. 이후 Raspberry Pi에서 `curl` 명령을 사용하여 ESP32의 `/api/ping` endpoint에 직접 요청을 보내고 응답을 수신함.

마지막으로 Raspberry Pi Flask 서버에 `/api/esp32/ping` endpoint를 추가함. 해당 endpoint는 클라이언트 요청을 받은 뒤 Raspberry Pi가 ESP32의 `/api/ping` endpoint로 HTTP 요청을 전달하고, ESP32 응답을 다시 클라이언트에게 반환하도록 구현함. 이를 통해 클라이언트 → Raspberry Pi → ESP32로 이어지는 기본 제어 경로를 확인함.

### 구현 및 실험 내용
- ESP32 보드 정보 출력 테스트 수행
- ESP32 Wi-Fi 연결 테스트 수행
- ESP32 HTTP server 실행
- 브라우저에서 ESP32 `/api/ping` 접속 확인
- Raspberry Pi에서 ESP32로 `curl` 요청 전송
- Raspberry Pi Flask 서버에서 ESP32 ping forwarding endpoint 구현
- Raspberry Pi에서 ESP32로 100회 반복 HTTP 요청을 전송하여 latency 측정
- 측정 결과를 CSV 파일로 저장
- 결과 캡처 이미지를 `images/results/` 폴더에 정리
- 수정된 `app.py`, latency 측정 스크립트, CSV 파일, 결과 이미지를 GitHub에 정리

### 확인한 값
ESP32 보드 정보 테스트 결과, ESP32-D0WD-V3 칩, 2개의 CPU core, 240 MHz 동작 주파수, 4 MB flash memory를 확인함. 기본 보드 정보 출력 테스트에서는 free heap 값이 안정적으로 유지됨을 확인함.

Wi-Fi 연결 테스트에서는 ESP32가 정상적으로 Wi-Fi에 연결되었고, IP 주소를 할당받음을 확인함. RSSI는 약 -30 dBm대에서 -40 dBm대 초반으로 측정되어 실험 환경에서 Wi-Fi 신호가 비교적 안정적인 것으로 판단함.

Raspberry Pi에서 ESP32로 100회 반복 HTTP 요청을 수행한 결과는 다음과 같음.

- 요청 횟수: 100회
- 성공 횟수: 100회
- 실패 횟수: 0회
- 최소 지연시간: 82.42 ms
- 최대 지연시간: 224.07 ms
- 평균 지연시간: 114.02 ms

### 결과
ESP32가 Wi-Fi 기반 하드웨어 제어 노드로 동작할 수 있음을 확인함. 또한 Raspberry Pi가 ESP32에 HTTP 요청을 전송하고 응답을 수신할 수 있음을 확인함.

Raspberry Pi Flask 서버의 `/api/esp32/ping` endpoint를 통해 클라이언트 요청이 Raspberry Pi를 거쳐 ESP32로 전달되고, ESP32 응답이 다시 클라이언트에게 반환되는 구조를 구현함. 이를 통해 본 프로젝트의 기본 제어 경로인 클라이언트 → Raspberry Pi → ESP32 구조가 정상적으로 동작함을 확인함.

100회 반복 latency 측정 결과 모든 요청이 성공하였으며, 평균 latency는 114.02 ms로 측정됨. 이를 통해 Raspberry Pi와 ESP32 사이의 기본 HTTP 통신이 안정적으로 수행됨을 확인하였고, 단일 요청 결과만으로 통신 성능을 판단하기보다 반복 측정을 통해 최소, 최대, 평균값을 함께 확인해야 함을 확인함.

### 발생한 문제 및 해결
초기 ESP32 Serial Monitor에서 `invalid header` 메시지가 출력됨. 이는 ESP32에 아직 정상적인 프로그램이 업로드되지 않았거나 플래시에 실행 가능한 코드가 없는 상태에서 발생할 수 있는 메시지로 판단함. 이후 테스트 코드를 업로드하고 `Hash of data verified` 메시지를 확인한 뒤 정상적으로 Serial Monitor 출력이 이루어짐.

GitHub에 파일을 정리하는 과정에서 Raspberry Pi 내부에서 생성된 `app.py`, `measure_esp32_latency.py`, CSV 파일을 MacBook의 GitHub 프로젝트 폴더로 복사해야 했음. `scp` 명령을 사용하여 Raspberry Pi의 파일을 MacBook 프로젝트 폴더로 옮긴 뒤 GitHub Desktop에서 commit 및 push를 진행함.

### 다음 작업
ESP32와 서보모터를 연결하여 실제 물리 제어 동작을 구현함. 서보모터는 외부 5V 전원을 사용하고, ESP32 GND와 외부 전원 GND를 공통으로 연결하여 제어 신호 기준을 맞춤. 이후 Raspberry Pi Flask 서버에서 ESP32로 제어 명령을 보내고, ESP32가 서보모터를 동작시키는 구조로 확장함.

추가로 로컬 버튼 입력을 연결하여 원격 제어와 물리 버튼 입력이 동일한 제어 대상에 적용될 수 있도록 구현함. 이후 서보모터 동작 성공률, 명령 전달 지연시간, 전원 안정성, free heap 변화 등을 측정하여 보고서에 정리함.

## 2026-08-04

### 작업 내용
ESP32와 서보모터를 연결하여 실제 물리 제어 테스트를 진행함. 초기에는 SG90 서보모터를 사용하여 GPIO18 기반 PWM 제어를 테스트하였으나, 전원 연결 과정에서 전원 극성을 반대로 연결하는 문제가 발생함. 이로 인해 SG90 서보모터에서 발열이 발생하여 내부 칩이 녹는 상황이 발생하였고 이로 인해 외부 플라스틱 케이스 일부가 변형됨.

이후 서보모터 제어 코드와 GPIO18 설정 자체에 문제가 있는지 확인하기 위해 Wokwi 시뮬레이션 환경에서 동일한 ESP32Servo 라이브러리와 GPIO18 핀 설정을 사용하여 테스트함. 시뮬레이션에서는 서보모터가 정상적으로 회전하였으며, Serial Monitor에서도 각도 변경 로그가 정상적으로 출력됨을 확인함.

시뮬레이션 결과를 바탕으로 코드와 GPIO18 설정에는 문제가 없다고 판단하고, 실제 하드웨어에서는 MG90S 서보모터를 이용하여 다시 테스트를 진행함. ESP32는 USB로 전원을 공급하고, MG90S 서보모터는 별도의 외부 5V 전원을 사용함. 또한 외부 전원 GND와 ESP32 GND를 공통으로 연결하여 PWM 신호의 기준 전위를 맞춤. 해당 구성에서 MG90S 서보모터가 정상적으로 동작함을 확인함.

서보모터 기본 동작 확인 이후 LDR 조도센서 모듈 테스트를 진행함. LDR 모듈의 VCC는 ESP32 3.3V에 연결하고, GND는 ESP32 GND에 연결하였으며, AO 핀은 ESP32 GPIO34에 연결함. Serial Monitor를 통해 조도 변화에 따른 analog raw value 변화를 확인함.

### 구현 및 실험 내용
- ESP32 GPIO18을 이용한 서보모터 PWM 제어 테스트
- SG90 서보모터 초기 연결 문제 확인
- Wokwi 시뮬레이션을 이용한 서보모터 코드 및 GPIO18 설정 검증
- MG90S 서보모터를 이용한 실제 하드웨어 동작 확인
- 외부 5V 전원과 ESP32 공통 GND 구성 확인
- ESP32 GPIO34를 이용한 LDR 조도센서 analog raw value 측정
- 조도 변화에 따른 LDR 센서 값 변화 확인
- LDR raw value를 기반으로 밝음/어두움 판단 threshold 임시 설정

### 확인한 값
LDR 조도센서 테스트 결과는 다음과 같음.

- 밝은 환경: 약 300
- 기본 실내 환경: 약 1300
- 센서를 손으로 가린 어두운 환경: 약 3500

측정 결과, 현재 사용한 LDR 모듈은 밝을수록 raw value가 작아지고, 어두울수록 raw value가 커지는 특성을 보임을 확인함. 기본 테스트용 threshold는 1800으로 임시 설정하였으며, raw value가 1800보다 작으면 밝은 상태, 1800 이상이면 어두운 상태로 판단하도록 구성함.

### 결과
Wokwi 시뮬레이션에서 ESP32Servo 라이브러리와 GPIO18 기반 서보모터 제어 코드가 정상적으로 동작함을 확인함. 이를 통해 초기 서보모터 동작 실패의 원인은 코드나 GPIO18 설정 문제가 아니라, 실제 하드웨어 연결 과정에서 발생한 전원 극성 오류와 SG90 서보모터 손상 가능성으로 판단함.

MG90S 서보모터를 이용한 실제 하드웨어 테스트에서는 외부 5V 전원과 공통 GND 구성을 적용한 뒤 정상 동작을 확인함. 이를 통해 ESP32가 PWM 신호를 출력하여 실제 서보모터를 제어할 수 있음을 확인함.

LDR 조도센서 테스트에서는 조도 변화에 따라 raw analog value가 크게 변화하는 것을 확인함. 이를 통해 향후 PC 전원 LED 상태 확인이나 장치 상태 판단에 LDR 센서를 활용할 수 있는 가능성을 확인함.

### 발생한 문제 및 해결
초기 SG90 서보모터 테스트 과정에서 전원 극성을 반대로 연결하여 서보모터 발열 및 외형 변형이 발생함. 이후 해당 서보모터는 손상 가능성이 있다고 판단하여 추가 테스트에서 제외함.

서보모터가 동작하지 않는 원인이 코드 문제인지 하드웨어 문제인지 구분하기 위해 Wokwi 시뮬레이션에서 동일한 코드와 GPIO18 핀 설정을 검증함. 시뮬레이션에서는 정상 동작하였으므로 코드와 핀 설정은 문제가 없다고 판단함.

이후 실제 회로에서는 ESP32를 USB로 전원 공급하고, 서보모터는 별도의 외부 5V 전원으로 구동함. 외부 전원 GND와 ESP32 GND를 공통으로 연결한 뒤 MG90S 서보모터가 정상적으로 동작함을 확인함.

오늘 실험은 임시 배선 환경에서 진행되었고, 멀티탭과 전원 배선 정리가 완료되지 않은 상태였기 때문에 하드웨어 사진과 정량 측정 결과는 다음 실험에서 정리하여 추가하기로 함.

### 다음 작업
다음 실험에서는 멀티탭과 전원 배선을 정리한 뒤 MG90S 서보모터를 다시 연결하여 안정성 측정을 진행함. 비접촉 적외선 온도계를 사용하여 서보모터 반복 동작 전후의 표면 온도를 측정하고, 멀티미터를 사용하여 서보모터 동작 중 외부 5V 전원의 전압 안정성을 확인함.

새 SG90 서보모터가 도착하면 동일한 외부 5V 전원 및 공통 GND 구성에서 정상 동작 여부를 확인함. 이후 SG90은 PC 전원 버튼 제어용으로, MG90S는 방 불 스위치와 같이 더 큰 힘이 필요한 제어 대상으로 사용하는 방향을 검토함.

LDR 조도센서는 PC 전원 LED 앞에 배치하여 PC OFF 상태와 ON 상태의 raw value를 측정함. 주변광 영향을 줄이기 위해 검정 테이프나 차광 구조를 사용하고, PC 전원 상태 판단에 사용할 threshold 값을 다시 설정함.

## 2026-08-05

### 작업 내용
ESP32, MG90S 서보모터, LDR 조도센서를 이용하여 서보모터 반복 동작 안정성 및 센서 측정 실험을 진행함. MG90S 서보모터는 외부 5V 전원으로 구동하였고, ESP32와 외부 전원 GND를 공통으로 연결하여 PWM 신호의 기준 전위를 맞춤. LDR 조도센서는 ESP32의 3.3V 전원과 GPIO34 ADC 입력에 연결함.

### 실험 구성
- 제어 보드: ESP32
- 서보모터: MG90S
- 서보모터 제어 핀: GPIO18
- 조도센서 입력 핀: GPIO34
- 서보모터 전원: 외부 5V 전원
- 공통 GND: 외부 5V GND, ESP32 GND, 서보모터 GND, LDR GND
- 실험 시간: 10분
- 동작 조건: 60도 → 90도 → 120도 → 90도 반복

### 측정 결과
10분간 반복 동작 실험을 수행한 결과, 총 172회의 서보모터 동작이 정상적으로 수행됨. 실험 중 ESP32 재부팅이나 서보모터 동작 실패는 관찰되지 않음.

ESP32 free heap은 초기 330252 bytes에서 최종 329648 bytes로 변화하였다. 반복 동작 중 각 trial의 heap_diff는 0으로 유지되어, 실험 중 메모리 사용량이 지속적으로 증가하는 현상은 관찰되지 않음.

MG90S 서보모터 외부 케이스 표면 온도는 시작 전 26.5℃, 5분 후 27.6℃, 10분 후 27.8℃로 측정됨. 10분 반복 동작 후 온도 상승폭은 약 1.3℃였으며, 과열은 관찰되지 않음.

### 데이터 파일
- Raw serial log: `data/raw/servo_ldr_measurement_10min_raw_log.txt`
- Cleaned measurement data: `data/processed/servo_ldr_measurement_10min_clean.csv`
- Servo/LDR summary: `data/processed/servo_ldr_measurement_summary.csv`
- Temperature summary: `data/processed/mg90s_temperature_summary.csv`

### 이미지 파일
- 실험 구성 사진: `images/hardware/servo_ldr_measurement_setup.jpg`
- 시작 전 온도 측정: `images/results/mg90s_temperature_before.jpg`
- 5분 후 온도 측정: `images/results/mg90s_temperature_5min.jpg`
- 10분 후 온도 측정: `images/results/mg90s_temperature_10min.jpg`
- Serial Monitor 캡처: `images/results/servo_ldr_measurement_serial_monitor.png`

### 결과 해석
MG90S 서보모터는 외부 5V 전원과 공통 GND 구성에서 10분간 안정적으로 반복 동작함. 실험 중 ESP32 재부팅, 서보모터 동작 실패, 급격한 온도 상승은 발생하지 않음. 이를 통해 ESP32 기반 서보모터 제어가 기본적인 반복 동작 환경에서 안정적으로 수행됨을 확인함.