#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>

#include "wifi_config.h"

// =====================
// Light Switch Node Config
// =====================

const char* NODE_NAME = "light-switch-node";
const char* NODE_ROLE = "room-light-control";

// Servo
const int SERVO_PIN = 18;

// Tact switches
// 버튼 한쪽은 GPIO, 반대쪽은 GND에 연결
const int BUTTON_ON_PIN = 21;
const int BUTTON_OFF_PIN = 22;

// Servo angles
// 설치 후 실제 스위치 방향에 맞게 조정
const int REST_ANGLE = 90;
const int PRESS_ON_ANGLE = 50;
const int PRESS_OFF_ANGLE = 140;

// Timing
const int PRESS_HOLD_MS = 400;
const int RETURN_WAIT_MS = 600;
const unsigned long DEBOUNCE_MS = 300;

// Servo attach range
const int SERVO_MIN_US = 500;
const int SERVO_MAX_US = 2400;

// If the servo buzzes at rest, change this to true.
// 처음에는 false로 두고 테스트.
const bool DETACH_AFTER_MOVE = false;

// =====================
// Global Objects
// =====================

WebServer server(80);
Servo servo;

bool servoBusy = false;
bool servoAttached = false;

unsigned long lastButtonOnMs = 0;
unsigned long lastButtonOffMs = 0;

int lastActionAngle = REST_ANGLE;
String lastAction = "rest";

// =====================
// Servo Helper Functions
// =====================

void attachServoIfNeeded() {
  if (!servoAttached) {
    servo.setPeriodHertz(50);
    servo.attach(SERVO_PIN, SERVO_MIN_US, SERVO_MAX_US);
    servoAttached = true;
    delay(100);
  }
}

void detachServoIfNeeded() {
  if (DETACH_AFTER_MOVE && servoAttached) {
    servo.detach();
    servoAttached = false;
  }
}

bool pressServo(int targetAngle, const String& actionName) {
  if (servoBusy) {
    return false;
  }

  servoBusy = true;

  uint32_t heapBefore = ESP.getFreeHeap();
  unsigned long startUs = micros();

  attachServoIfNeeded();

  servo.write(targetAngle);
  delay(PRESS_HOLD_MS);

  servo.write(REST_ANGLE);
  delay(RETURN_WAIT_MS);

  detachServoIfNeeded();

  unsigned long endUs = micros();
  uint32_t heapAfter = ESP.getFreeHeap();

  lastActionAngle = targetAngle;
  lastAction = actionName;

  Serial.print("[SERVO] action=");
  Serial.print(actionName);
  Serial.print(", target_angle=");
  Serial.print(targetAngle);
  Serial.print(", duration_ms=");
  Serial.print((endUs - startUs) / 1000.0);
  Serial.print(", heap_before=");
  Serial.print(heapBefore);
  Serial.print(", heap_after=");
  Serial.print(heapAfter);
  Serial.print(", heap_diff=");
  Serial.println((int)heapAfter - (int)heapBefore);

  servoBusy = false;
  return true;
}

// =====================
// JSON Response Helpers
// =====================

String jsonStatus() {
  String json = "{";
  json += "\"status\":\"ok\",";
  json += "\"node\":\"" + String(NODE_NAME) + "\",";
  json += "\"role\":\"" + String(NODE_ROLE) + "\",";
  json += "\"ip\":\"" + WiFi.localIP().toString() + "\",";
  json += "\"uptime_ms\":" + String(millis()) + ",";
  json += "\"free_heap\":" + String(ESP.getFreeHeap()) + ",";
  json += "\"rssi\":" + String(WiFi.RSSI()) + ",";
  json += "\"servo_busy\":" + String(servoBusy ? "true" : "false") + ",";
  json += "\"servo_attached\":" + String(servoAttached ? "true" : "false") + ",";
  json += "\"rest_angle\":" + String(REST_ANGLE) + ",";
  json += "\"press_on_angle\":" + String(PRESS_ON_ANGLE) + ",";
  json += "\"press_off_angle\":" + String(PRESS_OFF_ANGLE) + ",";
  json += "\"last_action\":\"" + lastAction + "\",";
  json += "\"last_action_angle\":" + String(lastActionAngle);
  json += "}";

  return json;
}

// =====================
// HTTP Handlers
// =====================

void handleRoot() {
  String html = "";
  html += "<!DOCTYPE html><html><head>";
  html += "<meta name='viewport' content='width=device-width, initial-scale=1'>";
  html += "<title>Light Switch Node</title>";
  html += "<style>";
  html += "body{font-family:Arial,sans-serif;background:#111;color:#eee;padding:24px;}";
  html += ".card{background:#1e1e1e;border-radius:16px;padding:20px;max-width:420px;margin:auto;}";
  html += "h1{font-size:24px;margin-top:0;}";
  html += "button{width:100%;padding:18px;margin:8px 0;border:0;border-radius:12px;font-size:18px;font-weight:bold;}";
  html += ".on{background:#f5c542;color:#111;}";
  html += ".off{background:#444;color:white;}";
  html += ".status{background:#2f80ed;color:white;}";
  html += "pre{background:#000;padding:12px;border-radius:8px;overflow:auto;}";
  html += "</style>";
  html += "</head><body>";
  html += "<div class='card'>";
  html += "<h1>Light Switch Node</h1>";
  html += "<p>ESP32 room light control node</p>";
  html += "<button class='on' onclick=\"fetch('/api/light/on').then(r=>r.text()).then(t=>out.textContent=t)\">Light ON</button>";
  html += "<button class='off' onclick=\"fetch('/api/light/off').then(r=>r.text()).then(t=>out.textContent=t)\">Light OFF</button>";
  html += "<button class='status' onclick=\"fetch('/api/status').then(r=>r.text()).then(t=>out.textContent=t)\">Status</button>";
  html += "<pre id='out'>Ready</pre>";
  html += "</div>";
  html += "</body></html>";

  server.send(200, "text/html", html);
}

void handlePing() {
  String json = "{";
  json += "\"status\":\"ok\",";
  json += "\"node\":\"" + String(NODE_NAME) + "\",";
  json += "\"role\":\"" + String(NODE_ROLE) + "\",";
  json += "\"uptime_ms\":" + String(millis()) + ",";
  json += "\"free_heap\":" + String(ESP.getFreeHeap()) + ",";
  json += "\"rssi\":" + String(WiFi.RSSI());
  json += "}";

  server.send(200, "application/json", json);
}

void handleStatus() {
  server.send(200, "application/json", jsonStatus());
}

void handleLightOn() {
  bool result = pressServo(PRESS_ON_ANGLE, "light_on");

  String json = "{";
  json += "\"status\":\"" + String(result ? "ok" : "busy") + "\",";
  json += "\"action\":\"light_on\",";
  json += "\"target_angle\":" + String(PRESS_ON_ANGLE) + ",";
  json += "\"node\":\"" + String(NODE_NAME) + "\",";
  json += "\"free_heap\":" + String(ESP.getFreeHeap());
  json += "}";

  server.send(result ? 200 : 409, "application/json", json);
}

void handleLightOff() {
  bool result = pressServo(PRESS_OFF_ANGLE, "light_off");

  String json = "{";
  json += "\"status\":\"" + String(result ? "ok" : "busy") + "\",";
  json += "\"action\":\"light_off\",";
  json += "\"target_angle\":" + String(PRESS_OFF_ANGLE) + ",";
  json += "\"node\":\"" + String(NODE_NAME) + "\",";
  json += "\"free_heap\":" + String(ESP.getFreeHeap());
  json += "}";

  server.send(result ? 200 : 409, "application/json", json);
}

void handleServoRest() {
  attachServoIfNeeded();
  servo.write(REST_ANGLE);
  delay(300);

  lastAction = "rest";
  lastActionAngle = REST_ANGLE;

  detachServoIfNeeded();

  String json = "{";
  json += "\"status\":\"ok\",";
  json += "\"action\":\"servo_rest\",";
  json += "\"rest_angle\":" + String(REST_ANGLE);
  json += "}";

  server.send(200, "application/json", json);
}

// =====================
// Wi-Fi Setup
// =====================

void connectWiFi() {
  Serial.println();
  Serial.println("[WiFi] Connecting...");

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int retry = 0;

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    retry++;

    if (retry > 60) {
      Serial.println();
      Serial.println("[WiFi] Failed. Restarting...");
      ESP.restart();
    }
  }

  Serial.println();
  Serial.println("[WiFi] Connected");
  Serial.print("[WiFi] IP address: ");
  Serial.println(WiFi.localIP());
  Serial.print("[WiFi] RSSI: ");
  Serial.println(WiFi.RSSI());
}

// =====================
// Button Check
// =====================

void checkButtons() {
  unsigned long now = millis();

  int onState = digitalRead(BUTTON_ON_PIN);
  int offState = digitalRead(BUTTON_OFF_PIN);

  if (onState == LOW && now - lastButtonOnMs > DEBOUNCE_MS) {
    lastButtonOnMs = now;
    Serial.println("[BUTTON] ON button pressed");
    pressServo(PRESS_ON_ANGLE, "local_button_on");
  }

  if (offState == LOW && now - lastButtonOffMs > DEBOUNCE_MS) {
    lastButtonOffMs = now;
    Serial.println("[BUTTON] OFF button pressed");
    pressServo(PRESS_OFF_ANGLE, "local_button_off");
  }
}

// =====================
// Setup / Loop
// =====================

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("=================================");
  Serial.println("ESP32 Light Switch Node Start");
  Serial.println("=================================");

  pinMode(BUTTON_ON_PIN, INPUT_PULLUP);
  pinMode(BUTTON_OFF_PIN, INPUT_PULLUP);

  attachServoIfNeeded();
  servo.write(REST_ANGLE);
  delay(1000);

  connectWiFi();

  server.on("/", HTTP_GET, handleRoot);
  server.on("/api/ping", HTTP_GET, handlePing);
  server.on("/api/status", HTTP_GET, handleStatus);
  server.on("/api/light/on", HTTP_GET, handleLightOn);
  server.on("/api/light/off", HTTP_GET, handleLightOff);
  server.on("/api/servo/rest", HTTP_GET, handleServoRest);

  server.begin();

  Serial.println("[HTTP] Server started");
  Serial.println("[HTTP] Available endpoints:");
  Serial.println("  GET /");
  Serial.println("  GET /api/ping");
  Serial.println("  GET /api/status");
  Serial.println("  GET /api/light/on");
  Serial.println("  GET /api/light/off");
  Serial.println("  GET /api/servo/rest");
  Serial.println();

  Serial.println("[PIN] Servo: GPIO18");
  Serial.println("[PIN] ON button: GPIO21 -> GND");
  Serial.println("[PIN] OFF button: GPIO22 -> GND");
  Serial.println();

  Serial.println("[ANGLE] REST: 90");
  Serial.println("[ANGLE] ON: 50");
  Serial.println("[ANGLE] OFF: 140");
  Serial.println();
}

void loop() {
  server.handleClient();
  checkButtons();
}