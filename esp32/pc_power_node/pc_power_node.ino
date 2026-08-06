#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>
#include "wifi_config.h"

// =========================
// Node Info
// =========================

const char* DEVICE_NAME = "pc-power-node";
const char* DEVICE_ROLE = "ldr-servo-pc-power-control";

// =========================
// Pin Configuration
// =========================

const int LDR_PIN = 34;
const int SERVO_PIN = 18;

// 로컬 택트 스위치
// 한쪽 GPIO21, 반대쪽 GND
const int LOCAL_POWER_BUTTON_PIN = 21;

// =========================
// LDR Configuration
// =========================

// 측정 결과:
// PC ON  : 57 ~ 2905 정도까지 관찰
// PC OFF : 4095 거의 고정
// 따라서 3000보다 여유 있게 3500 사용
int LDR_THRESHOLD = 3500;

const int LDR_SAMPLE_COUNT = 20;
const int LDR_SAMPLE_DELAY_MS = 5;

// 네 LDR 기준:
// 밝을수록 raw 작음
// 어두울수록 raw 큼
//
// raw < threshold  => PC LED ON
// raw >= threshold => PC LED OFF

// =========================
// Servo Configuration
// =========================

const int REST_ANGLE = 90;

// 시계반대방향으로 누르는 각도
// 너무 많이 누르면 125 -> 120 -> 115로 줄이기
// 반대 방향이면 55 근처로 바꾸기
const int PRESS_ANGLE = 125;

// PC 전원 버튼은 짧게 누르기
const int PRESS_HOLD_MS = 450;
const int RETURN_WAIT_MS = 700;

// 동작 후 detach해서 지이이잉 방지
const bool DETACH_AFTER_MOVE = true;

// =========================
// State
// =========================

WebServer server(80);
Servo servo;

bool servoBusy = false;

int lastRaw = -1;
int lastAvg = -1;
bool lastLedOn = false;

int pressCount = 0;

String lastAction = "boot";
String lastResult = "none";

unsigned long lastLocalButtonMs = 0;
const unsigned long DEBOUNCE_MS = 400;

// =========================
// Utility
// =========================

String boolStr(bool v) {
  return v ? "true" : "false";
}

String ledStateStr(bool ledOn) {
  return ledOn ? "ON" : "OFF";
}

int readLdrAverage() {
  long sum = 0;

  for (int i = 0; i < LDR_SAMPLE_COUNT; i++) {
    int raw = analogRead(LDR_PIN);
    sum += raw;
    delay(LDR_SAMPLE_DELAY_MS);
  }

  int avg = sum / LDR_SAMPLE_COUNT;

  lastRaw = analogRead(LDR_PIN);
  lastAvg = avg;
  lastLedOn = avg < LDR_THRESHOLD;

  return avg;
}

bool getPcLedOn() {
  int avg = readLdrAverage();
  return avg < LDR_THRESHOLD;
}

void attachServoIfNeeded() {
  if (!servo.attached()) {
    servo.setPeriodHertz(50);
    servo.attach(SERVO_PIN, 500, 2400);
    delay(100);
  }
}

// =========================
// Servo Functions
// =========================

void servoInit() {
  attachServoIfNeeded();

  Serial.println();
  Serial.println("[SERVO] init start");
  Serial.print("[SERVO] rest_angle=");
  Serial.println(REST_ANGLE);

  servo.write(REST_ANGLE);
  delay(1000);

  if (DETACH_AFTER_MOVE) {
    servo.detach();
  }

  lastAction = "servo_init";
  lastResult = "ok";

  Serial.println("[SERVO] init done");
}

void servoRest() {
  servoInit();
}

bool pressPowerButton(const char* source) {
  if (servoBusy) {
    lastAction = String("press_ignored_busy_") + source;
    lastResult = "busy";
    return false;
  }

  servoBusy = true;

  uint32_t heapBefore = ESP.getFreeHeap();
  unsigned long startMs = millis();

  lastAction = String("press_power_") + source;
  lastResult = "running";

  Serial.println();
  Serial.println("[SERVO] PC power button press start");
  Serial.print("[SERVO] source=");
  Serial.println(source);
  Serial.print("[SERVO] rest_angle=");
  Serial.println(REST_ANGLE);
  Serial.print("[SERVO] press_angle_ccw=");
  Serial.println(PRESS_ANGLE);

  // 1. 누르기 전에 항상 REST 위치로 초기화
  attachServoIfNeeded();
  servo.write(REST_ANGLE);
  delay(800);

  // 2. 시계반대방향으로 이동해서 PC 전원 버튼 누르기
  servo.write(PRESS_ANGLE);
  delay(PRESS_HOLD_MS);

  // 3. REST 위치로 복귀
  servo.write(REST_ANGLE);
  delay(RETURN_WAIT_MS);

  // 4. 지이이잉 방지
  if (DETACH_AFTER_MOVE) {
    servo.detach();
  }

  unsigned long durationMs = millis() - startMs;
  uint32_t heapAfter = ESP.getFreeHeap();

  pressCount++;
  lastResult = "ok";

  Serial.print("[SERVO] duration_ms=");
  Serial.println(durationMs);
  Serial.print("[SERVO] heap_before=");
  Serial.println(heapBefore);
  Serial.print("[SERVO] heap_after=");
  Serial.println(heapAfter);
  Serial.print("[SERVO] heap_diff=");
  Serial.println((int)heapAfter - (int)heapBefore);
  Serial.println("[SERVO] PC power button press end");

  servoBusy = false;
  return true;
}

// =========================
// JSON Builders
// =========================

String makeLdrJson() {
  int avg = readLdrAverage();
  bool ledOn = avg < LDR_THRESHOLD;

  String json = "{";
  json += "\"status\":\"ok\",";
  json += "\"device\":\"" + String(DEVICE_NAME) + "\",";
  json += "\"ldr_raw\":" + String(lastRaw) + ",";
  json += "\"ldr_avg\":" + String(avg) + ",";
  json += "\"ldr_threshold\":" + String(LDR_THRESHOLD) + ",";
  json += "\"pc_led_on\":" + boolStr(ledOn) + ",";
  json += "\"pc_led_state\":\"" + ledStateStr(ledOn) + "\",";
  json += "\"rule\":\"raw < threshold means PC LED ON\"";
  json += "}";

  return json;
}

String makeStatusJson() {
  int avg = readLdrAverage();
  bool ledOn = avg < LDR_THRESHOLD;

  String json = "{";
  json += "\"status\":\"ok\",";
  json += "\"device\":\"" + String(DEVICE_NAME) + "\",";
  json += "\"role\":\"" + String(DEVICE_ROLE) + "\",";
  json += "\"ip\":\"" + WiFi.localIP().toString() + "\",";
  json += "\"uptime_ms\":" + String(millis()) + ",";
  json += "\"free_heap\":" + String(ESP.getFreeHeap()) + ",";
  json += "\"rssi\":" + String(WiFi.RSSI()) + ",";
  json += "\"ldr_raw\":" + String(lastRaw) + ",";
  json += "\"ldr_avg\":" + String(avg) + ",";
  json += "\"ldr_threshold\":" + String(LDR_THRESHOLD) + ",";
  json += "\"pc_led_on\":" + boolStr(ledOn) + ",";
  json += "\"pc_led_state\":\"" + ledStateStr(ledOn) + "\",";
  json += "\"servo_busy\":" + boolStr(servoBusy) + ",";
  json += "\"press_count\":" + String(pressCount) + ",";
  json += "\"last_action\":\"" + lastAction + "\",";
  json += "\"last_result\":\"" + lastResult + "\"";
  json += "}";

  return json;
}

// =========================
// HTTP Handlers
// =========================

void handleRoot() {
  int avg = readLdrAverage();
  bool ledOn = avg < LDR_THRESHOLD;

  String html = "";
  html += "<!DOCTYPE html><html><head>";
  html += "<meta charset='UTF-8'>";
  html += "<meta name='viewport' content='width=device-width, initial-scale=1.0'>";
  html += "<title>PC Power Node</title>";

  html += "<style>";
  html += "body{font-family:Arial,sans-serif;background:#111;color:#eee;margin:0;padding:24px;}";
  html += ".card{max-width:520px;margin:0 auto;background:#1b1b1b;border-radius:18px;padding:22px;box-shadow:0 0 20px rgba(0,0,0,.35);}";
  html += "h1{font-size:24px;margin:0 0 8px;}";
  html += ".sub{color:#aaa;margin-bottom:18px;}";
  html += ".box{background:#262626;border-radius:14px;padding:14px;margin:10px 0;}";
  html += ".label{color:#aaa;font-size:13px;}";
  html += ".value{font-size:24px;font-weight:bold;margin-top:4px;}";
  html += "button{width:100%;padding:15px;margin:8px 0;border:0;border-radius:14px;font-size:17px;font-weight:bold;}";
  html += ".refresh{background:#4da3ff;color:#fff;}";
  html += ".press{background:#ffcc00;color:#111;}";
  html += ".rest{background:#555;color:#fff;}";
  html += "pre{white-space:pre-wrap;background:#0b0b0b;padding:12px;border-radius:12px;color:#ddd;overflow:auto;}";
  html += "</style>";

  html += "</head><body>";
  html += "<div class='card'>";
  html += "<h1>PC Power Node</h1>";
  html += "<div class='sub'>ESP32 + LDR + Servo Motor</div>";

  html += "<div class='box'>";
  html += "<div class='label'>PC LED State</div>";
  html += "<div class='value' id='ledState'>";
  html += ledOn ? "ON" : "OFF";
  html += "</div>";
  html += "</div>";

  html += "<div class='box'>";
  html += "<div class='label'>LDR Average</div>";
  html += "<div class='value' id='ldrAvg'>";
  html += String(avg);
  html += "</div>";
  html += "</div>";

  html += "<div class='box'>";
  html += "<div class='label'>Threshold</div>";
  html += "<div class='value' id='threshold'>";
  html += String(LDR_THRESHOLD);
  html += "</div>";
  html += "</div>";

  html += "<button class='refresh' onclick='refreshLdr()'>현재 조도값 새로고침</button>";
  html += "<button class='press' onclick='pressPower()'>PC 전원 버튼 누르기</button>";
  html += "<button class='rest' onclick='servoInit()'>서보 초기화</button>";
  html += "<button class='rest' onclick='servoRest()'>서보 REST</button>";

  html += "<pre id='jsonBox'>ready</pre>";

  html += "<script>";
  html += "function refreshLdr(){";
  html += "fetch('/api/ldr').then(r=>r.json()).then(j=>{";
  html += "document.getElementById('ledState').innerText=j.pc_led_state;";
  html += "document.getElementById('ldrAvg').innerText=j.ldr_avg;";
  html += "document.getElementById('threshold').innerText=j.ldr_threshold;";
  html += "document.getElementById('jsonBox').innerText=JSON.stringify(j,null,2);";
  html += "});";
  html += "}";

  html += "function pressPower(){";
  html += "fetch('/api/pc/power/press').then(r=>r.json()).then(j=>{";
  html += "document.getElementById('jsonBox').innerText=JSON.stringify(j,null,2);";
  html += "refreshLdr();";
  html += "});";
  html += "}";

  html += "function servoInit(){";
  html += "fetch('/api/servo/init').then(r=>r.json()).then(j=>{";
  html += "document.getElementById('jsonBox').innerText=JSON.stringify(j,null,2);";
  html += "});";
  html += "}";

  html += "function servoRest(){";
  html += "fetch('/api/servo/rest').then(r=>r.json()).then(j=>{";
  html += "document.getElementById('jsonBox').innerText=JSON.stringify(j,null,2);";
  html += "});";
  html += "}";

  html += "setInterval(refreshLdr, 2000);";
  html += "</script>";

  html += "</div></body></html>";

  server.send(200, "text/html", html);
}

void handlePing() {
  String json = "{";
  json += "\"status\":\"ok\",";
  json += "\"device\":\"" + String(DEVICE_NAME) + "\",";
  json += "\"uptime_ms\":" + String(millis()) + ",";
  json += "\"free_heap\":" + String(ESP.getFreeHeap()) + ",";
  json += "\"rssi\":" + String(WiFi.RSSI());
  json += "}";

  server.send(200, "application/json", json);
}

void handleLdr() {
  server.send(200, "application/json", makeLdrJson());
}

void handleStatus() {
  server.send(200, "application/json", makeStatusJson());
}

// Raspberry Pi app.py가 호출하는 endpoint
void handlePcStatus() {
  server.send(200, "application/json", makeLdrJson());
}

// Raspberry Pi app.py가 호출하는 endpoint
void handlePowerPress() {
  bool beforeLedOn = getPcLedOn();

  bool ok = pressPowerButton("http");

  delay(300);

  bool afterLedOn = getPcLedOn();

  String json = "{";
  json += "\"status\":\"" + String(ok ? "ok" : "busy") + "\",";
  json += "\"action\":\"pc_power_press\",";
  json += "\"before_pc_led_on\":" + boolStr(beforeLedOn) + ",";
  json += "\"after_pc_led_on\":" + boolStr(afterLedOn) + ",";
  json += "\"ldr_avg\":" + String(lastAvg) + ",";
  json += "\"ldr_threshold\":" + String(LDR_THRESHOLD) + ",";
  json += "\"press_count\":" + String(pressCount) + ",";
  json += "\"last_result\":\"" + lastResult + "\"";
  json += "}";

  server.send(ok ? 200 : 409, "application/json", json);
}

void handleServoInit() {
  servoInit();

  String json = "{";
  json += "\"status\":\"ok\",";
  json += "\"action\":\"servo_init\",";
  json += "\"rest_angle\":" + String(REST_ANGLE);
  json += "}";

  server.send(200, "application/json", json);
}

void handleServoRest() {
  servoRest();

  String json = "{";
  json += "\"status\":\"ok\",";
  json += "\"action\":\"servo_rest\",";
  json += "\"rest_angle\":" + String(REST_ANGLE);
  json += "}";

  server.send(200, "application/json", json);
}

void handleNotFound() {
  String json = "{";
  json += "\"status\":\"error\",";
  json += "\"message\":\"not_found\",";
  json += "\"path\":\"" + server.uri() + "\"";
  json += "}";

  server.send(404, "application/json", json);
}

// =========================
// Setup / Loop
// =========================

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("======================================");
  Serial.println("PC Power Node Start");
  Serial.println("ESP32 + LDR + Servo");
  Serial.println("======================================");

  pinMode(LOCAL_POWER_BUTTON_PIN, INPUT_PULLUP);

  analogReadResolution(12);
  analogSetPinAttenuation(LDR_PIN, ADC_11db);

  Serial.print("[BOOT] free_heap=");
  Serial.println(ESP.getFreeHeap());

  // 부팅 시 한 번 REST 위치로 초기화
  servoInit();

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print("[WIFI] connecting");

  int retry = 0;

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    retry++;

    if (retry > 60) {
      Serial.println();
      Serial.println("[WIFI] failed. restart");
      ESP.restart();
    }
  }

  Serial.println();
  Serial.println("[WIFI] connected");
  Serial.print("[WIFI] ip=");
  Serial.println(WiFi.localIP());
  Serial.print("[WIFI] rssi=");
  Serial.println(WiFi.RSSI());
  Serial.print("[WIFI] free_heap=");
  Serial.println(ESP.getFreeHeap());

  server.on("/", HTTP_GET, handleRoot);
  server.on("/api/ping", HTTP_GET, handlePing);
  server.on("/api/status", HTTP_GET, handleStatus);
  server.on("/api/ldr", HTTP_GET, handleLdr);
  server.on("/api/pc/status", HTTP_GET, handlePcStatus);
  server.on("/api/pc/power/press", HTTP_GET, handlePowerPress);
  server.on("/api/servo/init", HTTP_GET, handleServoInit);
  server.on("/api/servo/rest", HTTP_GET, handleServoRest);
  server.onNotFound(handleNotFound);

  server.begin();

  Serial.println("[HTTP] server started");
  Serial.print("[HTTP] open http://");
  Serial.println(WiFi.localIP());

  lastAction = "boot_complete";
  lastResult = "ok";
}

void loop() {
  server.handleClient();

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WIFI] disconnected. reconnecting");
    WiFi.disconnect();
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    delay(1000);
    return;
  }

  int buttonState = digitalRead(LOCAL_POWER_BUTTON_PIN);

  if (buttonState == LOW) {
    unsigned long now = millis();

    if (now - lastLocalButtonMs > DEBOUNCE_MS) {
      lastLocalButtonMs = now;
      Serial.println("[BUTTON] local power press");
      pressPowerButton("local_button");
    }
  }
}