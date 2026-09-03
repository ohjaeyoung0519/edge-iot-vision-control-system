#include <Arduino.h>
#include <WiFi.h>
#include <MQTT.h>

#include "wifi_config.h"

// Raspberry Pi Mosquitto Broker
const char* MQTT_BROKER = "192.168.0.35";
const int MQTT_PORT = 1883;

// 이번 연결 확인용 Topic
const char* MQTT_TEST_TOPIC = "edge/esp32-test";

WiFiClient mqttNetwork;
MQTTClient mqttClient(512);


// ========================
// MQTT Message Callback
// ========================

void messageReceived(String& topic, String& payload) {
  Serial.println();
  Serial.println("[MQTT] Message received");

  Serial.print("[MQTT] Topic: ");
  Serial.println(topic);

  Serial.print("[MQTT] Payload: ");
  Serial.println(payload);
}


// ========================
// Wi-Fi Connection
// ========================

void connectWiFi() {
  Serial.println();
  Serial.println("[WiFi] Connecting...");

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("[WiFi] Connected");

  Serial.print("[WiFi] IP: ");
  Serial.println(WiFi.localIP());

  Serial.print("[WiFi] RSSI: ");
  Serial.println(WiFi.RSSI());
}


// ========================
// MQTT Connection
// ========================

void connectMQTT() {
  Serial.println();
  Serial.println("[MQTT] Connecting to broker...");

  while (!mqttClient.connected()) {

    String clientId =
      "esp32-test-" +
      String((uint32_t)ESP.getEfuseMac(), HEX);

    Serial.print("[MQTT] Client ID: ");
    Serial.println(clientId);

    if (mqttClient.connect(clientId.c_str())) {

      Serial.println("[MQTT] Connected!");

      bool subscribed =
        mqttClient.subscribe(
          MQTT_TEST_TOPIC,
          0
        );

      Serial.print("[MQTT] Subscribe result: ");
      Serial.println(
        subscribed ? "OK" : "FAILED"
      );

      Serial.print("[MQTT] Subscribed topic: ");
      Serial.println(MQTT_TEST_TOPIC);

    } else {

      Serial.println(
        "[MQTT] Connection failed. Retry in 1 sec..."
      );

      delay(1000);
    }
  }
}


// ========================
// Setup
// ========================

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("==============================");
  Serial.println("ESP32 MQTT Connection Test");
  Serial.println("==============================");

  connectWiFi();

  mqttClient.begin(
    MQTT_BROKER,
    MQTT_PORT,
    mqttNetwork
  );

  mqttClient.onMessage(
    messageReceived
  );

  connectMQTT();
}


// ========================
// Loop
// ========================

void loop() {

  mqttClient.loop();

  delay(10);

  if (!mqttClient.connected()) {
    connectMQTT();
  }
}
