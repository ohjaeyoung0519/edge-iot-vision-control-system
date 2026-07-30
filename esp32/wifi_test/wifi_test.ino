#include <Arduino.h>
#include <WiFi.h>

const char* WIFI_SSID = "WIFI_SSID";
const char* WIFI_PASSWORD = "WIFI_PASSWORD";

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("=== ESP32 Wi-Fi Test ===");

  Serial.print("Free heap before Wi-Fi: ");
  Serial.print(ESP.getFreeHeap());
  Serial.println(" bytes");

  WiFi.mode(WIFI_STA);
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
    Serial.println("Wi-Fi connected");

    Serial.print("ESP32 IP address: ");
    Serial.println(WiFi.localIP());

    Serial.print("RSSI: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");

    Serial.print("Free heap after Wi-Fi: ");
    Serial.print(ESP.getFreeHeap());
    Serial.println(" bytes");
  } else {
    Serial.println("Wi-Fi connection failed");
  }
}

void loop() {
  delay(1000);
}