// ========================
// readSerial_heater.ino
// Version 4
// Last Updated: 4/11/26
// ========================

void readSerial_heater()
{
  if (Serial.available() == false){
    return;
  }

  String line = Serial.readStringUntil('\n');
  line.trim();

  if (line.startsWith("HEATER_ON"))
  {
    int comma = line.indexOf(',');
    if (comma > 0)
    {
      setTemp = line.substring(comma + 1).toFloat();
    }
  
    heaterStatus = true;
    heaterStartMillis = millis();
    integral = 0;

    return;
  }

  if (line == "HEATER_OFF")
  {
    heaterStatus = false;
    digitalWrite(SSR, LOW);
    
    return;
  }
}