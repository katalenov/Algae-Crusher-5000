// =========================
// logger_motor.ino
// Version 4
// Last Updated: 4/11/26
// =========================

extern bool motorStatus;
extern double motorRuntime;

void logger_motor()
{
  Serial.print("MOTOR,");
  Serial.print(motorStatus ? "1" : "0");  // Convert bool to "1"/"0"
  Serial.print(",");
  Serial.println(motorRuntime, 2);
}
