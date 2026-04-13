// =========================
// logger_heater.ino
// Version 4
// Last Updated: 4/11/26
// =========================

extern double temp1, temp2;
extern bool fault1, fault2;
extern bool heaterStatus;
extern double heaterRuntime;

void logger_heater()
{
  Serial.print("HEAT,");
  Serial.print(temp1);
  Serial.print(",");
  Serial.print(temp2);
  Serial.print(",");
  Serial.print(fault1);
  Serial.print(",");
  Serial.print(fault2);
  Serial.print(",");
  Serial.print(heaterStatus);
  Serial.print(",");
  Serial.println(heaterRuntime);
}
