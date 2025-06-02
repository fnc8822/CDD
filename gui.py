import sys
import time
import threading
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QRadioButton, QPushButton, QLabel, QButtonGroup
from PySide6.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

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

class SignalGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.reader = SignalReader()

        self.setWindowTitle("Visualización de Señales")
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.layout = QVBoxLayout(self.main_widget)
        self.create_widgets()

        self.reader.start()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)

    def create_widgets(self):
        # Signal selection
        self.signal_label = QLabel("Señal:")
        self.layout.addWidget(self.signal_label)

        self.signal_group = QButtonGroup(self)
        self.square_button = QRadioButton("Cuadrada")
        self.square_button.setChecked(True)
        self.signal_group.addButton(self.square_button, 1)
        self.layout.addWidget(self.square_button)

        self.triangular_button = QRadioButton("Triangular")
        self.signal_group.addButton(self.triangular_button, 2)
        self.layout.addWidget(self.triangular_button)

        # Add sawtooth signal button
        self.sawtooth_button = QRadioButton("Diente de Sierra")
        self.signal_group.addButton(self.sawtooth_button, 3)
        self.layout.addWidget(self.sawtooth_button)

        self.signal_group.buttonClicked.connect(self.change_signal)

        # Toggle button
        self.toggle_button = QPushButton("Pausar")
        self.toggle_button.clicked.connect(self.toggle)
        self.layout.addWidget(self.toggle_button)

        # Matplotlib plot
        self.fig, self.ax = plt.subplots(figsize=(6, 3))
        self.ax.set_title("Valor de la Señal")
        self.ax.set_xlabel("Tiempo [s]")
        self.ax.set_ylabel("Valor")
        self.line, = self.ax.plot([], [], lw=2)

        self.canvas = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas)

    def change_signal(self):
        signal = self.signal_group.checkedId()
        self.reader.write_signal(signal)

    def toggle(self):
        if self.reader.running:
            self.reader.stop()
            self.toggle_button.setText("Reanudar")
        else:
            self.reader.start()
            self.toggle_button.setText("Pausar")

    def update_plot(self):
        self.line.set_data(self.reader.times, self.reader.values)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

def main():
    app = QApplication(sys.argv)
    window = SignalGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()