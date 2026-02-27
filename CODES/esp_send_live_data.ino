#include <Wire.h>
#include <MPU6050.h>
#include "BluetoothSerial.h"

BluetoothSerial SerialBT;
MPU6050 mpu;

#define FLEX1 32
#define FLEX2 33
#define FLEX3 34
#define FLEX4 35
#define FLEX5 36

unsigned long lastSendTime = 0;
unsigned long lastClientTime = 0;

const unsigned long SEND_INTERVAL = 50;
const unsigned long ADVERTISE_TIMEOUT = 30000;

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("=================================");
  Serial.println("ESP32 HAND GLOVE BOOT");
  Serial.println("=================================");

  pinMode(FLEX1, INPUT);
  pinMode(FLEX2, INPUT);
  pinMode(FLEX3, INPUT);
  pinMode(FLEX4, INPUT);
  pinMode(FLEX5, INPUT);
  Serial.println("Flex OK");

  Wire.begin(21, 22);
  mpu.initialize();

  if (!mpu.testConnection()) {
    Serial.println("MPU FAIL");
    while (1);
  }
  Serial.println("MPU OK");

  SerialBT.begin("ESP32_GLOVE");
  Serial.println("BT READY: ESP32_GLOVE");
}

void loop() {
  if (SerialBT.hasClient()) {
    lastClientTime = millis();
    Serial.println("BT CLIENT OK");
  } else if (millis() - lastClientTime > ADVERTISE_TIMEOUT) {
    Serial.println("BT RESTART");
    SerialBT.end();
    delay(200);
    SerialBT.begin("ESP32_GLOVE");
    lastClientTime = millis();
  }

  if (millis() - lastSendTime >= SEND_INTERVAL) {
    lastSendTime = millis();
    if (SerialBT.hasClient()) {
      sendData();
    }
  }
}

void sendData() {
  int f1 = analogRead(FLEX1);
  int f2 = analogRead(FLEX2);
  int f3 = analogRead(FLEX3);
  int f4 = analogRead(FLEX4);
  int f5 = analogRead(FLEX5);

  int16_t ax, ay, az, gx, gy, gz;
  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

  String data =
    String(f1) + "," + String(f2) + "," +
    String(f3) + "," + String(f4) + "," +
    String(f5) + "," +
    String(ax / 16384.0, 3) + "," +
    String(ay / 16384.0, 3) + "," +
    String(az / 16384.0, 3) + "," +
    String(gx / 131.0, 3) + "," +
    String(gy / 131.0, 3) + "," +
    String(gz / 131.0, 3);

  SerialBT.println(data);
}
