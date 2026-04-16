from guizero import App, Box, Text, PushButton, TextBox
import tkinter as tk
from serial_connection import SerialConnection
import pyvisa

# Arduino COM port assignments
MOTOR_COM = "COM12"
HEATER_COM = "COM7"

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
dmm.write("VOLT:DC:NPLC 1")
dmm.write("ZERO:AUTO OFF")
dmm.write("SENS:AVER:STAT ON;SENS:AVER:COUN 500")

last_dmm = "NaN"

# Data history for embedded plots
motor_history = []
heater_history = []

# Global canvas references
motor_canvas = None
heater_canvas = None

def draw_motor_plot():
    """Draw motor plot on canvas"""
    if motor_canvas is None:
        return
    motor_canvas.delete("all")
    w = 450
    h = 300
    padding_left = 90
    padding_right = 20
    padding_top = 20
    padding_bottom = 80
    
    if len(motor_history) < 2:
        # Draw message if no data
        motor_canvas.create_text(w/2, h/2, text="Waiting for data...", font=("Arial", 14), fill="gray")
        return
    
    # Calculate scaling - use actual force values
    try:
        max_y = max(motor_history)
        min_y = min(motor_history)
    except:
        max_y = 1
        min_y = 0
    
    # Add some padding to the y-range
    span = max_y - min_y
    if span == 0:
        span = 1
    y_min_display = min_y - span * 0.1
    y_max_display = max_y + span * 0.1
    span_display = y_max_display - y_min_display
    
    # Draw axes
    motor_canvas.create_line(padding_left, h-padding_bottom, w-padding_right, h-padding_bottom, fill="black", width=2)  # X-axis
    motor_canvas.create_line(padding_left, padding_top, padding_left, h-padding_bottom, fill="black", width=2)  # Y-axis
    
    # Draw data line
    x_scale = (w - padding_left - padding_right) / max(len(motor_history)-1, 1)
    for i in range(len(motor_history)-1):
        x1 = padding_left + i * x_scale
        x2 = padding_left + (i+1) * x_scale
        y1 = h - padding_bottom - ((motor_history[i] - y_min_display) / span_display) * (h - padding_top - padding_bottom)
        y2 = h - padding_bottom - ((motor_history[i+1] - y_min_display) / span_display) * (h - padding_top - padding_bottom)
        motor_canvas.create_line(x1, y1, x2, y2, fill="green", width=2)
    
    # Add y-axis numbers (5 ticks)
    for i in range(5):
        value = y_min_display + (span_display * i / 4)
        y_pos = h - padding_bottom - (i / 4) * (h - padding_top - padding_bottom)
        motor_canvas.create_line(padding_left-5, y_pos, padding_left, y_pos, fill="black", width=1)
        motor_canvas.create_text(padding_left-10, y_pos, text=f"{value:.2f}", anchor="e", font=("Arial", 11))
    
    # Add x-axis numbers (5 ticks)
    if len(motor_history) > 1:
        for i in range(5):
            point = int(i * (len(motor_history)-1) / 4)
            x_pos = padding_left + (point * x_scale)
            motor_canvas.create_line(x_pos, h-padding_bottom, x_pos, h-padding_bottom+5, fill="black", width=1)
            motor_canvas.create_text(x_pos, h-padding_bottom+15, text=str(point), anchor="n", font=("Arial", 11))
    
    # Add labels - moved to not overlap
    motor_canvas.create_text(w/2, h-15, text="Data Point", anchor="s", font=("Arial", 15, "bold"))
    motor_canvas.create_text(20, h/2, text="Force (lbf)", angle=90, anchor="center", font=("Arial", 15, "bold"))

def draw_heater_plot():
    """Draw heater plot on canvas"""
    if heater_canvas is None:
        return
    heater_canvas.delete("all")
    w = 450
    h = 300
    padding_left = 90
    padding_right = 20
    padding_top = 20
    padding_bottom = 80
    
    if len(heater_history) < 2:
        # Draw message if no data
        heater_canvas.create_text(w/2, h/2, text="Waiting for data...", font=("Arial", 14), fill="gray")
        return
    
    # Calculate scaling - use actual temperature values
    try:
        max_y = max(heater_history)
        min_y = min(heater_history)
    except:
        max_y = 30
        min_y = 20
    
    # Add some padding to the y-range
    span = max_y - min_y
    if span == 0:
        span = 1
    y_min_display = min_y - span * 0.1
    y_max_display = max_y + span * 0.1
    span_display = y_max_display - y_min_display
    
    # Draw axes
    heater_canvas.create_line(padding_left, h-padding_bottom, w-padding_right, h-padding_bottom, fill="black", width=2)  # X-axis
    heater_canvas.create_line(padding_left, padding_top, padding_left, h-padding_bottom, fill="black", width=2)  # Y-axis
    
    # Draw data line
    x_scale = (w - padding_left - padding_right) / max(len(heater_history)-1, 1)
    for i in range(len(heater_history)-1):
        x1 = padding_left + i * x_scale
        x2 = padding_left + (i+1) * x_scale
        y1 = h - padding_bottom - ((heater_history[i] - y_min_display) / span_display) * (h - padding_top - padding_bottom)
        y2 = h - padding_bottom - ((heater_history[i+1] - y_min_display) / span_display) * (h - padding_top - padding_bottom)
        heater_canvas.create_line(x1, y1, x2, y2, fill="green", width=2)
    
    # Add Y-axis numbers (5 ticks)
    for i in range(5):
        value = y_min_display + (span_display * i / 4)
        y_pos = h - padding_bottom - (i / 4) * (h - padding_top - padding_bottom)
        heater_canvas.create_line(padding_left-5, y_pos, padding_left, y_pos, fill="black", width=1)
        heater_canvas.create_text(padding_left-10, y_pos, text=f"{value:.1f}", anchor="e", font=("Arial", 11))
    
    # Add X-axis numbers (5 ticks)
    if len(heater_history) > 1:
        for i in range(5):
            point = int(i * (len(heater_history)-1) / 4)
            x_pos = padding_left + (point * x_scale)
            heater_canvas.create_line(x_pos, h-padding_bottom, x_pos, h-padding_bottom+5, fill="black", width=1)
            heater_canvas.create_text(x_pos, h-padding_bottom+15, text=str(point), anchor="n", font=("Arial", 11))
    
    # Add labels - moved to not overlap
    heater_canvas.create_text(w/2, h-15, text="Data Point", anchor="s", font=("Arial", 15, "bold"))
    heater_canvas.create_text(20, h/2, text="Therm 1 Temp (°C)", angle=90, anchor="center", font=("Arial", 15, "bold"))

def refresh_plots():
    """Update plots - runs on main thread only"""
    try:
        # Try to get calibrated force value instead of voltage
        motor_history.append(float(calibrated_force.value))
    except:
        try:
            motor_history.append(float(applied_force.value))
        except:
            motor_history.append(0)

    try:
        heater_history.append(float(tc1.value))
    except:
        heater_history.append(0)

    # Keep only last 100 points
    if len(motor_history) > 100:
        motor_history.pop(0)
    if len(heater_history) > 100:
        heater_history.pop(0)

    draw_motor_plot()
    draw_heater_plot()
    
    app.after(500, refresh_plots)

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

# Serial reading
def read_serial():
    motor_serial.read_line(parse_motor_data)
    heater_serial.read_line(parse_heat_data)
    app.after(20, read_serial)

def parse_motor_data(parts):
    if len(parts) >= 3 and parts[0] == "MOTOR":
        status = parts[1]
        runtime = parts[2]
    elif len(parts) >= 2:
        status = parts[0]
        runtime = parts[1]
    else:
        return

    motor_data["motorStatus"] = status
    motor_data["motorRuntime"] = runtime
    motor_time.value = runtime
    motor_light.bg = "green" if status == "1" else "red"

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

# DMM reading + calibration
def read_dmm():
    global last_dmm
    try:
        v = dmm.query("READ?").strip()
        v_float = float(v)

        last_dmm = f"{v_float:.7f}"
        applied_force.value = last_dmm

        m = -17.37
        b = -51.83
        F = m*(v_float*1000.0)+b

        calibrated_force.value = f"{F:.2f}"

    except:
        pass

    app.after(100, read_dmm)

# GUI Layout
app = App(title="Main Control", width=600, height=900)
app.text_size = 21
app.padding = 20
app.bg = "#baccb2"

main_container = Box(app, width="fill", height="fill")
main_container.tk.pack_configure(expand=True)
main_container.bg = "#baccb2"

center_wrapper = Box(main_container, align="top", width="fill")
center_wrapper.tk.pack_configure(expand=True)
center_wrapper.bg = "#baccb2"

top_line = Box(center_wrapper, width="fill", height=2, align="top")
top_line.bg = "gray"

# Title
title_box = Box(center_wrapper, width="fill", align="top")
title_box.bg = "white"
Text(title_box, "ALGAE CRUSHER 5000", size=30, color="green", align="top")
Text(title_box, "MAIN CONTROL", size=20, color="green", align="top")

# Motor section
motor_box = Box(center_wrapper, width="fill", border=True, align="top")
motor_box.padding = 20
motor_box.bg = "white"

Text(motor_box, "MOTOR", size=24)

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

motor_compress_button.bg = "#cce2c3"
motor_decompress_button.bg = "#bcd5b1"
motor_stop_button.bg = "#a7bc9e"

motor_indicators = Box(motor_box, align="left", width="fill")
Text(motor_indicators, "Strain Voltage (V):")
applied_force = TextBox(motor_indicators, width=10, enabled=False)

Text(motor_indicators, "Calibrated Force (lb):")
calibrated_force = TextBox(motor_indicators, width=10, enabled=False)

Text(motor_indicators, "Elapsed Time (s):")
motor_time = TextBox(motor_indicators, width=10, enabled=False)

motor_light_box = Box(motor_box, width="fill", align="left")
Text(motor_light_box, "Motor Status:")
motor_light = Box(motor_light_box, width=40, height=40)
motor_light.bg = "red"

# Motor plot - using Tkinter Canvas with white background
motor_plot_row = Box(motor_box, width="fill", align="top")
Box(motor_plot_row, width="fill", align="left")
motor_canvas_container = Box(motor_plot_row, width=450, height=300, align="right")
motor_canvas_container.bg = "white"
motor_canvas = tk.Canvas(motor_canvas_container.tk, width=450, height=300, bg="white", highlightthickness=0)
motor_canvas.pack()

# Heater section
heat_box = Box(center_wrapper, width="fill", border=True, align="top")
heat_box.padding = 10
heat_box.bg = "white"

Text(heat_box, "HEATER", size=24)

heat_controls = Box(heat_box, align="left", width="fill")
Text(heat_controls, "Desired Temp (°C):")
desired_temp = TextBox(heat_controls, width=12, command=check_heat_text)
desired_temp.bg = "#c8cec6"
desired_temp.value = "0"

heat_start_button = PushButton(
    heat_controls, text="Start", width=10, command=start_heater, enabled=False
)
heat_stop_button = PushButton(
    heat_controls, text="Stop", width=10, command=stop_heater, enabled=False
)

heat_start_button.bg = "#bcd5b1"
heat_stop_button.bg = "#a7bc9e"

heat_indicators = Box(heat_box, align="left", width="fill")
Text(heat_indicators, "Thermocouple 1:")
tc1 = TextBox(heat_indicators, width=10, enabled=False)

Text(heat_indicators, "Thermocouple 2:")
tc2 = TextBox(heat_indicators, width=10, enabled=False)

Text(heat_indicators, "Elapsed Time (s):")
heat_time = TextBox(heat_indicators, width=10, enabled=False)

heat_light_box = Box(heat_box, width="fill", align="left")
Text(heat_light_box, "Heat Tape Status:")
heat_light = Box(heat_light_box, width=40, height=40)
heat_light.bg = "red"

# Heater plot - using Tkinter Canvas with white background
heater_plot_row = Box(heat_box, width="fill", align="top")
Box(heater_plot_row, width="fill", align="left")
heater_canvas_container = Box(heater_plot_row, width=450, height=300, align="right")
heater_canvas_container.bg = "white"
heater_canvas = tk.Canvas(heater_canvas_container.tk, width=450, height=300, bg="white", highlightthickness=0)
heater_canvas.pack()

# Start everything
start_logging()
read_serial()
read_dmm()
log_row()
refresh_plots()

app.display()