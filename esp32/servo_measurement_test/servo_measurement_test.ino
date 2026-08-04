#include <Arduino.h>
#include <ESP32Servo.h>

const int SERVO_PIN = 18;

Servo servo;

const int REST_ANGLE = 90;
const int PRESS_LEFT = 60;
const int PRESS_RIGHT = 120;

int trial = 0;

void pressServo(int targetAngle, const char* label) {
  trial++;

  unsigned long start_us = micros();
  uint32_t heap_before = ESP.getFreeHeap();

  servo.write(targetAngle);
  delay(400);

  servo.write(REST_ANGLE);
  delay(600);

  unsigned long end_us = micros();
  uint32_t heap_after = ESP.getFreeHeap();

  Serial.print("trial=");
  Serial.print(trial);

  Serial.print(", action=");
  Serial.print(label);

  Serial.print(", target_angle=");
  Serial.print(targetAngle);

  Serial.print(", duration_ms=");
  Serial.print((end_us - start_us) / 1000.0);

  Serial.print(", free_heap_before=");
  Serial.print(heap_before);

  Serial.print(", free_heap_after=");
  Serial.print(heap_after);

  Serial.print(", heap_diff=");
  Serial.println((int)heap_after - (int)heap_before);
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  servo.setPeriodHertz(50);
  servo.attach(SERVO_PIN, 500, 2400);

  servo.write(REST_ANGLE);
  delay(1000);

  Serial.println("MG90S Servo Measurement Test Start");
  Serial.print("Initial free heap: ");
  Serial.println(ESP.getFreeHeap());
}

void loop() {
  pressServo(PRESS_LEFT, "press_left");
  delay(2000);

  pressServo(PRESS_RIGHT, "press_right");
  delay(3000);
}