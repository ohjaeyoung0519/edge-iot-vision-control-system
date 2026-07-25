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
