// =========================
// heaterControl.ino
// Version 4
// Last Updated: 4/11/26
// =========================

#include <Arduino.h>
#include <Adafruit_MAX31856.h>

const int SSR = 8;

Adafruit_MAX31856 thermo1 = Adafruit_MAX31856(51, 49, 47, 45);
Adafruit_MAX31856 thermo2 = Adafruit_MAX31856(35, 33, 31, 30);

bool heaterStatus = false;
double setTemp = 0.0;

double temp1 = 0;
double temp2 = 0;
bool fault1 = false;
bool fault2 = false;

// Update with tuned gains
double Kp = 10;
double Ki = 0.05;
double integral = 0;

unsigned long prevPITime = 0;
const unsigned long PI_interval = 100;

unsigned long switchStart = 0;
const unsigned long switchDuration = 1000;

unsigned long heaterStartMillis = 0;
double heaterRuntime = 0;

void setup()
{
  Serial.begin(115200);
  delay(1000);
  Serial.println("ID:HEATER");

  pinMode(SSR, OUTPUT);
  digitalWrite(SSR, LOW);

  thermo1.begin();
  thermo2.begin();
  thermo1.setThermocoupleType(MAX31856_TCTYPE_J);
  thermo2.setThermocoupleType(MAX31856_TCTYPE_J);

  prevPITime = millis();
  switchStart = millis();
}

void loop()
{
  readSerial_heater();
  unsigned long now = millis();

  temp1 = thermo1.readThermocoupleTemperature();
  temp2 = thermo2.readThermocoupleTemperature();

  fault1 = thermo1.readFault() != 0;
  fault2 = thermo2.readFault() != 0;

  // Runtime
  if (heaterStatus == true)
  {
    heaterRuntime = (now - heaterStartMillis) / 1000.0;
  }
  else
  {
    heaterRuntime = 0.0;
  }

  // PI loop
  if (heaterStatus && now - prevPITime >= PI_interval)
  {
    runPI();
  }

  logger_heater();
}

void runPI()
{
  unsigned long now = millis();
  double dt = (now - prevPITime) / 1000.0;
  prevPITime = now;

  if (fault2)
  {
    digitalWrite(SSR, LOW);
    return;
  }

  double error = setTemp - temp1;
  double P = Kp * error;
  double I = Ki * integral;

  if (!(((P + I) > 255 && error > 0) || ((P + I) < 0 && error < 0)))
  {
    integral += error * dt;
  }

  I = Ki * integral;
  double Gc = constrain(P + I, 0, 255);
  double dutyCycle = Gc / 255.0;

  if (now - switchStart >= switchDuration)
  {
    switchStart = now;
  }

  digitalWrite(SSR, (now - switchStart) < (dutyCycle * switchDuration));
}