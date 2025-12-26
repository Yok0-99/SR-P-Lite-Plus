import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from collections import deque
import sys
import os

# =====================================================
# GLOBALS
# =====================================================
ser = None

root = tk.Tk()
root.title("SR-P Lite+")

adc_var = tk.IntVar(value=0)
history_len = 200
adc_history = deque([0] * history_len, maxlen=history_len)

# =====================================================
# SERIAL
# =====================================================
def list_ports():
    return [p.device for p in serial.tools.list_ports.comports()]

def connect(port):
    global ser
    if not port or (ser and ser.is_open):
        return
    try:
        ser = serial.Serial(port, 115200, timeout=0.01)
        status_var.set(f"Connected: {port}")
    except Exception:
        ser = None
        status_var.set("Disconnected")

def disconnect():
    global ser
    try:
        if ser and ser.is_open:
            ser.close()
    except Exception:
        pass
    ser = None
    status_var.set("Disconnected")

def read_serial_loop():
    if ser and ser.is_open:
        try:
            line = ser.readline()
            if line:
                line = line.decode(errors="ignore").strip()
                if line.startswith("ADC_CAL:"):
                    val = int(line[8:])
                    adc_var.set(val)
                    adc_history.append(val)
                    update_plot()
        except Exception:
            disconnect()
    root.after(10, read_serial_loop)

# =====================================================
# AUTO PORT / CONNECT / RECONNECT
# =====================================================
def ports_loop():
    ports = list_ports()
    current = port_var.get()

    port_cb["values"] = ports

    # Auto-select
    if len(ports) == 1:
        port_var.set(ports[0])
    elif current not in ports:
        port_var.set("")

    # Auto-connect / reconnect
    if not ser and port_var.get():
        connect(port_var.get())

    root.after(1000, ports_loop)

# =====================================================
# GUI
# =====================================================
frame_top = tk.Frame(root)
frame_top.pack(pady=5)

port_var = tk.StringVar()
port_cb = ttk.Combobox(frame_top, textvariable=port_var, width=15)
port_cb.pack(side="left", padx=5)

tk.Button(frame_top, text="Connect", command=lambda: connect(port_var.get())).pack(side="left")

status_var = tk.StringVar(value="Disconnected")
tk.Label(root, textvariable=status_var).pack()

tk.Label(root, text="Position").pack()
tk.Label(root, textvariable=adc_var, font=("Arial", 20)).pack()

# =====================================================
# PLOT
# =====================================================
fig, ax = plt.subplots(figsize=(6, 2))
line_plot, = ax.plot(list(adc_history))
ax.set_ylim(-32768, 32767)
ax.grid(True)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

def update_plot():
    line_plot.set_ydata(list(adc_history))
    canvas.draw_idle()

# =====================================================
# BUTTONS
# =====================================================
frame_cal = tk.Frame(root)
frame_cal.pack(pady=10)

tk.Button(frame_cal, text="Set Min", command=lambda: ser and ser.write(b"min\n")).grid(row=0, column=0, padx=5)
tk.Button(frame_cal, text="Set Max", command=lambda: ser and ser.write(b"max\n")).grid(row=0, column=1, padx=5)
tk.Button(frame_cal, text="Save",    command=lambda: ser and ser.write(b"save\n")).grid(row=1, column=0, padx=5)
tk.Button(frame_cal, text="Load",    command=lambda: ser and ser.write(b"load\n")).grid(row=1, column=1, padx=5)
tk.Button(frame_cal, text="Reset",   command=lambda: ser and ser.write(b"reset\n")).grid(row=2, column=0, padx=5)

# =====================================================
# CLEAN EXIT (CRITICAL)
# =====================================================
def on_close():
    try:
        disconnect()
    except Exception:
        pass

    try:
        root.destroy()
    except Exception:
        pass

    sys.exit(0)
    os._exit(0)

root.protocol("WM_DELETE_WINDOW", on_close)

# =====================================================
# START
# =====================================================
ports_loop()
read_serial_loop()
root.mainloop()
