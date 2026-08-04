#include <Arduino.h>

const int LDR_PIN = 34;

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("LDR Sensor Test Start");
  Serial.println("Reading analog value from GPIO34");
}

void loop() {
  int raw = analogRead(LDR_PIN);

  Serial.print("LDR raw value: ");
  Serial.println(raw);

  delay(500);
}