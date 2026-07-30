#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>

const char* WIFI_SSID = "WIFI_SSID";
const char* WIFI_PASSWORD = "WIFI_PASSWORD";

WebServer server(80);

unsigned long wifi_start_time = 0;
unsigned long wifi_connected_time = 0;

void handleRoot() {
  server.send(200, "text/plain", "ESP32 HTTP server is running.");
}

void handlePing() {
  String json = "{";
  json += "\"status\":\"ok\",";
  json += "\"device\":\"esp32\",";
  json += "\"role\":\"hardware-control-node\",";
  json += "\"uptime_ms\":";
  json += millis();
  json += ",";
  json += "\"free_heap\":";
  json += ESP.getFreeHeap();
  json += ",";
  json += "\"rssi\":";
  json += WiFi.RSSI();
  json += "}";

  server.send(200, "application/json", json);
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("=== ESP32 HTTP Server Test ===");

  Serial.print("Free heap before Wi-Fi: ");
  Serial.print(ESP.getFreeHeap());
  Serial.println(" bytes");

  WiFi.mode(WIFI_STA);

  wifi_start_time = millis();
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print("Connecting to Wi-Fi");

  int retry_count = 0;
  while (WiFi.status() != WL_CONNECTED && retry_count < 30) {
    delay(500);
    Serial.print(".");
    retry_count++;
  }

  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    wifi_connected_time = millis();

    Serial.println("Wi-Fi connected");
    Serial.print("ESP32 IP address: ");
    Serial.println(WiFi.localIP());

    Serial.print("Wi-Fi connection time: ");
    Serial.print(wifi_connected_time - wifi_start_time);
    Serial.println(" ms");

    Serial.print("RSSI: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");

    Serial.print("Free heap after Wi-Fi: ");
    Serial.print(ESP.getFreeHeap());
    Serial.println(" bytes");

    server.on("/", handleRoot);
    server.on("/api/ping", handlePing);
    server.begin();

    Serial.println("HTTP server started");

    Serial.print("Free heap after HTTP server start: ");
    Serial.print(ESP.getFreeHeap());
    Serial.println(" bytes");
  } else {
    Serial.println("Wi-Fi connection failed");
  }
}

void loop() {
  server.handleClient();
}