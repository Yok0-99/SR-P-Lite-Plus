import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading
import time
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from collections import deque

ser = None
running = False

root = tk.Tk()
root.title("SR-P Lite+")

adc_var = tk.IntVar()

history_len = 200
adc_history = deque([0]*history_len, maxlen=history_len)

def list_ports():
    ports = serial.tools.list_ports.comports()
    return [p.device for p in ports]

def connect():
    global ser, running
    port = port_var.get()
    try:
        ser = serial.Serial(port, 115200, timeout=0.1)
        running = True
        threading.Thread(target=read_serial, daemon=True).start()
        messagebox.showinfo("Connected", f"Connected to {port}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not open port {port}\n{e}")

def read_serial():
    global running
    while running:
        if ser:
            try:
                line = ser.readline().decode(errors="ignore").strip()
                if line.startswith("ADC_CAL:"):
                    val = int(line[8:])
                    adc_var.set(val)
                    adc_history.append(val)
                    update_plot()
            except Exception as e:
                print("Serial read error:", e)
        time.sleep(0.01)

def send_cmd(cmd):
    if ser:
        ser.write(f"{cmd}\n".encode())

frame_top = tk.Frame(root)
frame_top.pack(pady=5)

port_var = tk.StringVar()
ports = list_ports()
port_cb = ttk.Combobox(frame_top, values=ports, textvariable=port_var)
if ports: port_cb.current(0)
port_cb.grid(row=0, column=0, padx=5)
tk.Button(frame_top, text="Connect", command=connect).grid(row=0, column=1, padx=5)

tk.Label(root, text="Posistion").pack()
tk.Label(root, textvariable=adc_var, font=("Arial", 20)).pack()

fig, ax = plt.subplots(figsize=(6,2))
line, = ax.plot(list(adc_history))
ax.set_ylim(-32768, 32767)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

def update_plot():
    line.set_ydata(list(adc_history))
    canvas.draw_idle()

frame_cal = tk.Frame(root)
frame_cal.pack(pady=10)
tk.Button(frame_cal, text="Set Min", command=lambda: send_cmd("min")).grid(row=0, column=0, padx=5)
tk.Button(frame_cal, text="Set Max", command=lambda: send_cmd("max")).grid(row=0, column=1, padx=5)
tk.Button(frame_cal, text="Save", command=lambda: send_cmd("save")).grid(row=1, column=0, padx=5)
tk.Button(frame_cal, text="Load", command=lambda: send_cmd("load")).grid(row=1, column=1, padx=5)
tk.Button(frame_cal, text="Reset", command=lambda: send_cmd("reset")).grid(row=2, column=0, padx=10)

root.mainloop()
