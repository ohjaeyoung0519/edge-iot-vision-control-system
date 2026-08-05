#include <Arduino.h>
#include <ESP32Servo.h>

const int SERVO_PIN = 18;
const int LDR_PIN = 34;

const int REST_ANGLE = 90;
const int PRESS_LEFT = 60;
const int PRESS_RIGHT = 120;

const unsigned long TEST_DURATION_MS = 10UL * 60UL * 1000UL;

Servo servo;

int trial = 0;
unsigned long test_start_ms = 0;

void printTableHeader() {
  Serial.println();

  Serial.printf(
    "%-9s %5s %-11s %5s %12s %12s %12s %10s %8s\n",
    "elapsed", "trial", "action", "angle", "duration_ms",
    "heap_before", "heap_after", "heap_diff", "ldr_raw"
  );

  Serial.printf(
    "%-9s %5s %-11s %5s %12s %12s %12s %10s %8s\n",
    "-------", "-----", "------", "-----", "-----------",
    "-----------", "----------", "---------", "-------"
  );
}

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

  int ldr_raw = analogRead(LDR_PIN);

  unsigned long elapsed_ms = millis() - test_start_ms;
  float elapsed_s = elapsed_ms / 1000.0;
  float duration_ms = (end_us - start_us) / 1000.0;
  int heap_diff = (int)heap_after - (int)heap_before;

  Serial.printf(
    "%-9.1f %5d %-11s %5d %12.2f %12u %12u %10d %8d\n",
    elapsed_s,
    trial,
    label,
    targetAngle,
    duration_ms,
    heap_before,
    heap_after,
    heap_diff,
    ldr_raw
  );
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("Servo + LDR Measurement Test Start");
  Serial.println("MG90S servo pin: GPIO18");
  Serial.println("LDR analog input: GPIO34");
  Serial.println("LDR VCC: ESP32 3.3V");
  Serial.println("Common GND: external 5V GND, ESP32 GND, servo GND, LDR GND");
  Serial.println("Lower LDR raw value = brighter");
  Serial.println("Higher LDR raw value = darker");
  Serial.println("Test duration: 10 minutes");

  servo.setPeriodHertz(50);
  servo.attach(SERVO_PIN, 500, 2400);

  servo.write(REST_ANGLE);
  delay(1000);

  test_start_ms = millis();

  Serial.print("Initial free heap: ");
  Serial.println(ESP.getFreeHeap());

  printTableHeader();
}

void loop() {
  unsigned long elapsed_ms = millis() - test_start_ms;

  if (elapsed_ms >= TEST_DURATION_MS) {
    servo.write(REST_ANGLE);

    Serial.println();
    Serial.println("Test finished: 10 minutes elapsed");
    Serial.print("Total trials: ");
    Serial.println(trial);
    Serial.print("Final free heap: ");
    Serial.println(ESP.getFreeHeap());

    while (true) {
      delay(1000);
    }
  }

  pressServo(PRESS_LEFT, "press_left");
  delay(2000);

  pressServo(PRESS_RIGHT, "press_right");
  delay(3000);
}