#include <Arduino.h>

const int LDR_PIN = 34;

// 현재 측정값 기준
// 밝을 때: 약 300
// 기본 실내: 약 1300
// 손으로 가림: 약 3500
// 따라서 1800 이상이면 어두움으로 임시 판단
const int LIGHT_THRESHOLD = 1800;

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("LDR Threshold Test Start");
  Serial.println("GPIO34 analog input");
  Serial.println("Lower raw value = brighter");
  Serial.println("Higher raw value = darker");
}

void loop() {
  int raw = analogRead(LDR_PIN);

  Serial.print("LDR raw value: ");
  Serial.print(raw);

  if (raw < LIGHT_THRESHOLD) {
    Serial.println(" -> BRIGHT");
  } else {
    Serial.println(" -> DARK");
  }

  delay(300);
}