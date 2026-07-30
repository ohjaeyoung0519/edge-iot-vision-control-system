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

