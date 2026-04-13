// ========================
// readSerial_motor.ino
// Version 4
// Last Updated: 4/11/26
// ========================

void readSerial_motor()
{
  static String line = "";

  while (Serial.available())
  {
    char c = Serial.read();

    if (c == '\n' || c == '\r')
    {
      line.trim();

      if (line.equals("COMPRESS_START"))
      {
        if (motorStatus == false)
        { // Only set start time if motor was stopped
          motorStartMillis = millis();
        }
        motorStatus = true;
        compress = true;
      }
      else if (line.equals("DECOMPRESS_START"))
      {
        if (motorStatus == false)
        { // Only set start time if motor was stopped
          motorStartMillis = millis();
        }
        motorStatus = true;
        compress = false;
      }
      else if (line.equals("MOTOR_STOP")) // ← ADDED BACK
      {
        motorStatus = false;
      }

      line = "";
    }
    else
    {
      line += c;
    }
  }
}