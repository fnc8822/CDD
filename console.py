# tp5_console.py
import time

DEVICE_PATH = "/dev/foobar_sdec"

def select_signal(signal: int):
    with open(DEVICE_PATH, "w") as f:
        f.write(f"{signal}\n")

def read_signal():
    with open(DEVICE_PATH, "r") as f:
        return f.read().strip()

def main():
    print("1: Señal cuadrada")
    print("2: Señal triangular")
    while True:
        choice = input("Elegí una señal (1/2) o q para salir: ")
        if choice == "q":
            break
        if choice in ["1", "2"]:
            select_signal(int(choice))
            print("Mostrando valores. Ctrl+C para cambiar de señal.")
            try:
                while True:
                    val = read_signal()
                    print(f"{time.time():.1f} - Valor: {val}")
                    time.sleep(1)
            except KeyboardInterrupt:
                continue

if __name__ == "__main__":
    main()
