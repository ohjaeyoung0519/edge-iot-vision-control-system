#include <Arduino.h>

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("=== ESP32 Board Information Test ===");

  Serial.print("Chip model: ");
  Serial.println(ESP.getChipModel());

  Serial.print("Chip revision: ");
  Serial.println(ESP.getChipRevision());

  Serial.print("CPU cores: ");
  Serial.println(ESP.getChipCores());

  Serial.print("CPU frequency: ");
  Serial.print(ESP.getCpuFreqMHz());
  Serial.println(" MHz");

  Serial.print("Flash size: ");
  Serial.print(ESP.getFlashChipSize());
  Serial.println(" bytes");

  Serial.print("Free heap: ");
  Serial.print(ESP.getFreeHeap());
  Serial.println(" bytes");
}

void loop() {
  Serial.print("Uptime: ");
  Serial.print(millis());
  Serial.print(" ms, Free heap: ");
  Serial.print(ESP.getFreeHeap());
  Serial.println(" bytes");

  delay(1000);
}