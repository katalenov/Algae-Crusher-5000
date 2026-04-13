import serial
import time


class SerialConnection:
    def __init__(self, port, baudrate=115200):
        self.ser = serial.Serial(port, baudrate, timeout=0.1)
        self.ser.setDTR(False)
        time.sleep(2)
        print(f"Connected to {port}")
        self.buffer = ""

    def read_line(self, parse_method):
        while self.ser.in_waiting:
            c = self.ser.read().decode(errors="ignore")
            if c == "\n":
                line = self.buffer.strip()
                self.buffer = ""
                if not line.startswith("ID:"):
                    parts = line.split(",")
                    parse_method(parts)

            else:
                self.buffer += c

    def send_command(self, cmd):
        print("SEND CMD:", cmd)
        self.ser.write((cmd + "\n").encode())
