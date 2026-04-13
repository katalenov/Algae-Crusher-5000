from guizero import App, Box, Text, PushButton, TextBox
from serial_connection import SerialConnection
import pyvisa

# Arduino COM port assignments
MOTOR_COM = "COM6"
HEATER_COM = "COM4"

try:
    motor_serial = SerialConnection(MOTOR_COM)
except Exception as e:
    print(f"ERROR: Could not open MOTOR Arduino on {MOTOR_COM}")
    print(e)
    exit()

try:
    heater_serial = SerialConnection(HEATER_COM)
except Exception as e:
    print(f"ERROR: Could not open HEATER Arduino on {HEATER_COM}")
    print(e)
    exit()


# Keithley 2110 DMM setup
rm = pyvisa.ResourceManager()
dmm = rm.open_resource("USB0::0x05E6::0x2110::1423119::INSTR")
dmm.write("CONF:VOLT:DC")
dmm.write("VOLT:DC:NPLC 0.1")
dmm.write("ZERO:AUTO OFF")

last_dmm = "NaN"


# DMM disabled - using placeholder
#last_dmm = "0.0000000"

# Data storage
motor_data = {"motorStatus": "0", "motorRuntime": "0"}
heat_data = {
    "temp1": "NaN",
    "temp2": "NaN",
    "fault1": "0",
    "fault2": "0",
    "heaterStatus": "0",
    "heaterRuntime": "0",
}

# Logging
logging_enabled = False
log_file = None
log_path = "data_log.csv"


def main():
    # Start system
    start_logging()

    read_serial()

    read_dmm()
    log_row()

    app.display()


def start_logging():
    global logging_enabled, log_file
    log_file = open(log_path, "w")
    log_file.write(
        "temp1,temp2,fault1,fault2,heaterStatus,heaterRuntime,"
        "motorStatus,motorRuntime,dmm\n"
    )
    logging_enabled = True


def stop_logging():
    global logging_enabled, log_file
    logging_enabled = False
    if log_file:
        log_file.close()


def log_row():
    if logging_enabled and log_file:
        row = (
            f"{heat_data['temp1']},{heat_data['temp2']},{heat_data['fault1']},{heat_data['fault2']},"
            f"{heat_data['heaterStatus']},{heat_data['heaterRuntime']},"
            f"{motor_data['motorStatus']},{motor_data['motorRuntime']},"
            f"{last_dmm}\n"
        )
        log_file.write(row)
        log_file.flush()

    app.after(100, log_row)


# Motor control buttons
def compress_motor():
    set_motor_buttons(motor_on=True, motor_compressed=True)
    motor_serial.send_command("COMPRESS_START")


def decompress_motor():
    set_motor_buttons(motor_on=True, motor_compressed=False)
    motor_serial.send_command("DECOMPRESS_START")


def stop_motor():
    set_motor_buttons(motor_on=False, motor_compressed=None)
    motor_serial.send_command("MOTOR_STOP")


def set_motor_buttons(motor_on, motor_compressed):
    motor_stop_button.enabled = motor_on
    motor_compress_button.enabled = not motor_on or not motor_compressed
    motor_decompress_button.enabled = not motor_on or motor_compressed


# Heater control buttons
def start_heater():
    set_heater_buttons(heater_on=True)
    heater_serial.send_command("HEATER_ON," + desired_temp.value)
    print(f"Heater start command sent with temp: {desired_temp.value}")


def stop_heater():
    set_heater_buttons(heater_on=False)
    heater_serial.send_command("HEATER_OFF")


def set_heater_buttons(heater_on):
    heat_start_button.enabled = not heater_on
    heat_stop_button.enabled = heater_on


def check_heat_text():
    try:
        float(desired_temp.value)
        heat_start_button.enabled = True
    except:
        heat_start_button.enabled = False


def read_serial():
    motor_serial.read_line(parse_motor_data)
    heater_serial.read_line(parse_heat_data)
    app.after(20, read_serial)


def parse_motor_data(parts):

    if len(parts) >= 3 and parts[0] == "MOTOR":
        status = parts[1]
        runtime = parts[2]
        motor_data["motorStatus"] = status
        motor_data["motorRuntime"] = runtime
        motor_time.value = runtime
        motor_light.bg = "green" if status == "1" else "red"
    # Try alternative format without prefix
    elif len(parts) >= 2:
        try:
            status = parts[0]
            runtime = parts[1]
            motor_data["motorStatus"] = status
            motor_data["motorRuntime"] = runtime
            motor_time.value = runtime
            motor_light.bg = "green" if status == "1" else "red"
        except Exception as e:
            print(f"Motor parse error: {e}")
    else:
        print(f"Motor: unexpected format")


def parse_heat_data(parts):

    if len(parts) >= 7 and parts[0] == "HEAT":
        temp1 = parts[1]
        temp2 = parts[2]
        fault1 = parts[3]
        fault2 = parts[4]
        status = parts[5]
        runtime = parts[6]
        heat_data["temp1"] = temp1
        heat_data["temp2"] = temp2
        heat_data["fault1"] = fault1
        heat_data["fault2"] = fault2
        heat_data["heaterStatus"] = status
        heat_data["heaterRuntime"] = runtime
        tc1.value = temp1
        tc2.value = temp2
        heat_time.value = runtime
        heat_light.bg = "green" if status == "1" else "red"


# Read DMM
def read_dmm():
    global last_dmm
    try:
        v = dmm.query("READ?").strip()
        last_dmm = f"{float(v):.7f}" # round to 7 decimal places
        applied_force.value = last_dmm
    except:
        pass
    app.after(100, read_dmm)


# DMM disabled - just update with placeholder
# def read_dmm():
    # global last_dmm
    # applied_force.value = "0.0000000"
    # app.after(100, read_dmm)


# GUI Layout
app = App(title="Main Control", width=600, height=700)

# Title
title_box = Box(app, width="fill", align="top")
Text(title_box, "MAIN CONTROL", size=18, color="blue")

# Motor section
motor_box = Box(app, width="fill", border=True, align="top")
motor_box.padding = 10

Text(motor_box, "MOTOR", size=14)

motor_buttons = Box(motor_box, align="left", width="fill")
motor_compress_button = PushButton(
    motor_buttons, text="Compress", width=10, command=compress_motor
)
motor_decompress_button = PushButton(
    motor_buttons, text="Decompress", width=10, command=decompress_motor
)
motor_stop_button = PushButton(
    motor_buttons, text="Stop", width=10, command=stop_motor, enabled=False
)

motor_indicators = Box(motor_box, align="left", width="fill")
Text(motor_indicators, "Strain Voltage (V):")
applied_force = TextBox(motor_indicators, width=10, enabled=False)
applied_force.value = "0.0000000"

Text(motor_indicators, "Calibrated Force (lb):")
calibrated_force = TextBox(motor_indicators, width=10, enabled=False)
calibrated_force.value = "0.00"

Text(motor_indicators, "Elapsed Time (s):")
motor_time = TextBox(motor_indicators, width=10, enabled=False)

motor_light_box = Box(motor_box, width="fill", align="left")
Text(motor_light_box, "Motor Status:")
motor_light = Box(motor_light_box, width=20, height=20)
motor_light.bg = "red"

# Heater section
heat_box = Box(app, width="fill", border=True, align="top")
heat_box.padding = 10

Text(heat_box, "HEAT TAPE", size=14)

heat_controls = Box(heat_box, align="left", width="fill")
Text(heat_controls, "Desired Temp (°C):")
desired_temp = TextBox(heat_controls, width=10, command=check_heat_text)

heat_buttons = Box(heat_box, align="left", width="fill")
heat_start_button = PushButton(
    heat_buttons, text="Start", width=10, command=start_heater, enabled=False
)
heat_stop_button = PushButton(
    heat_buttons, text="Stop", width=10, command=stop_heater, enabled=False
)

heat_indicators = Box(heat_box, align="left", width="fill")
Text(heat_indicators, "Thermocouple 1:")
tc1 = TextBox(heat_indicators, width=10, enabled=False)

Text(heat_indicators, "Thermocouple 2:")
tc2 = TextBox(heat_indicators, width=10, enabled=False)

Text(heat_indicators, "Elapsed Time (s):")
heat_time = TextBox(heat_indicators, width=10, enabled=False)

heat_light_box = Box(heat_box, width="fill", align="left")
Text(heat_light_box, "Heat Tape Status:")
heat_light = Box(heat_light_box, width=20, height=20)
heat_light.bg = "red"

main()
