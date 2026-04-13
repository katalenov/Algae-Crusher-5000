// =========================
// motorControl.ino (Arduino 1)
// Version 4
// Last Updated: 4/11/26
// =========================

#include <Arduino.h>

// Arduino Pin Assignments
const int DIR = 7; // Direction pin (DIR-)
const int PUL = 6; // Pulse pin on stepper driver (PUL-)
const int ENA = 5; // Enable pin (ENA-)

// States
bool motorStatus = false;
bool compress = false;

// Timing
unsigned long motorStartMillis = 0;
double motorRuntime = 0;

// Motor Pulse Timing
unsigned long lastMotorStep = 0;
unsigned long stepIntervalMs = 5;

// Logging timing
unsigned long lastLog = 0;
const unsigned long logInterval = 100; // 10 Hz logging to GUI

// SETUP
void setup()
{
  Serial.begin(115200);
  delay(1000);
  Serial.println("ID:MOTOR"); // Arduino 1 identifier

  pinMode(PUL, OUTPUT);
  pinMode(DIR, OUTPUT);
  pinMode(ENA, OUTPUT);
  digitalWrite(ENA, HIGH); // HIGH freewheels the rotor; LOW locks it
}

// MAIN LOOP
void loop()
{
  readSerial_motor();
  unsigned long now = millis();

  // Calculate runtime continuously (not just when stepping)
  if (motorStatus == true)
  {
    motorRuntime = (now - motorStartMillis) / 1000.0;
  }
  else
  {
    motorRuntime = 0.0;
  }

  // Motor stepping
  if (motorStatus == true && now - lastMotorStep >= stepIntervalMs)
  {
    lastMotorStep = now;
    if (compress)
    {
      motorCompress();
    }
    else
    {
      motorDecompress();
    }
  }

  // Logging (100 ms)
  if (now - lastLog >= logInterval)
  {
    lastLog = now;
    logger_motor();
  }
}

void motorCompress()
{
  digitalWrite(DIR, HIGH);
  digitalWrite(PUL, HIGH);
  delayMicroseconds(5);
  digitalWrite(PUL, LOW);
  delayMicroseconds(5);
}

void motorDecompress()
{
  digitalWrite(DIR, LOW);
  digitalWrite(PUL, HIGH);
  delayMicroseconds(5);
  digitalWrite(PUL, LOW);
  delayMicroseconds(5);
}
