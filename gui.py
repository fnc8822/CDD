import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
import os

DEVICE_PATH = "/dev/foobar_sdec"

class SignalReader:
    def __init__(self):
        self.running = True
        self.signal = 1  # default: square
        self.values = []
        self.times = []
        self.start_time = time.time()
    
    def read_value(self):
        try:
            with open(DEVICE_PATH, "r") as f:
                return int(f.read().strip())
        except Exception as e:
            print(f"Error leyendo valor: {e}")
            return 0

    def write_signal(self, signal):
        try:
            with open(DEVICE_PATH, "w") as f:
                f.write(str(signal))
        except Exception as e:
            print(f"Error seleccionando señal: {e}")

    def update(self):
        while self.running:
            val = self.read_value()
            t = time.time() - self.start_time
            self.values.append(val)
            self.times.append(t)
            time.sleep(0.02)

    def start(self):
        self.running = True
        self.start_time = time.time()
        self.values = []
        self.times = []
        threading.Thread(target=self.update, daemon=True).start()

    def stop(self):
        self.running = False

class SignalGUI:
    def __init__(self, root):
        self.reader = SignalReader()

        self.root = root
        self.root.title("Visualización de Señales")
        self.create_widgets()

        self.reader.start()
        self.update_plot()

    def create_widgets(self):
        self.signal_var = tk.IntVar(value=1)

        frame = ttk.Frame(self.root)
        frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(frame, text="Señal:").pack(side=tk.LEFT, padx=5)

        ttk.Radiobutton(frame, text="Cuadrada", variable=self.signal_var, value=1, command=self.change_signal).pack(side=tk.LEFT)
        ttk.Radiobutton(frame, text="Triangular", variable=self.signal_var, value=2, command=self.change_signal).pack(side=tk.LEFT)

        self.toggle_button = ttk.Button(frame, text="Pausar", command=self.toggle)
        self.toggle_button.pack(side=tk.LEFT, padx=10)

        # Gráfico
        self.fig, self.ax = plt.subplots(figsize=(6, 3))
        self.ax.set_title("Valor de la Señal")
        self.ax.set_xlabel("Tiempo [s]")
        self.ax.set_ylabel("Valor")
        self.line, = self.ax.plot([], [], lw=2)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def change_signal(self):
        signal = self.signal_var.get()
        self.reader.write_signal(signal)

    def toggle(self):
        if self.reader.running:
            self.reader.stop()
            self.toggle_button.config(text="Reanudar")
        else:
            self.reader.start()
            self.toggle_button.config(text="Pausar")

    def update_plot(self):
        self.line.set_data(self.reader.times, self.reader.values)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()
        self.root.after(100, self.update_plot)

def main():
    root = tk.Tk()
    app = SignalGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
