#!/usr/bin/env python3

#pip install pyserial
# serial_to_csv.py
import argparse, csv, sys, time
from datetime import datetime
import serial
import serial.tools.list_ports

def list_ports():
    print("Puertos serie disponibles:")
    for p in serial.tools.list_ports.comports():
        print(f"  - {p.device}  ({p.description})")

def main():
    parser = argparse.ArgumentParser(description="Leer IMU por Serial y guardar a CSV.")
    parser.add_argument("--port", "-p", required=False, help="Puerto serie (ej: COM5, /dev/ttyACM0, /dev/tty.usbmodemXXXX)")
    parser.add_argument("--baud", "-b", type=int, default=115200, help="Baudrate (default: 115200)")
    parser.add_argument("--out", "-o", required=False, help="Ruta del CSV de salida")
    parser.add_argument("--seconds", "-s", type=float, default=0, help="Duración en segundos (0 = hasta Ctrl+C)")
    parser.add_argument("--label", "-l", default="", help="Etiqueta opcional para añadir como columna extra")
    parser.add_argument("--list", action="store_true", help="Listar puertos y salir")
    args = parser.parse_args()

    if args.list:
        list_ports()
        return

    if not args.port:
        print("ERROR: Debes especificar --port (usa --list para ver opciones).")
        sys.exit(1)

    out_path = args.out or f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    print(f"Abrir puerto: {args.port} @ {args.baud}")
    print(f"Guardando en: {out_path}")
    if args.seconds > 0:
        print(f"Duración: {args.seconds} s")
    else:
        print("Duración: hasta Ctrl+C")

    # Abrir serial
    ser = serial.Serial(args.port, args.baud, timeout=1)
    time.sleep(2.0)  # pequeño delay para que el Arduino reinicie y empiece a imprimir

    # Sincronizar con la cabecera del sketch "ax,ay,az,gx,gy,gz"
    header = None
    print("Esperando cabecera (ax,ay,az,gx,gy,gz)...")
    start_sync = time.time()
    while True:
        line = ser.readline().decode("utf-8", errors="ignore").strip()
        if line:
            # Detecta cabecera
            if line.lower().replace(" ", "") == "ax,ay,az,gx,gy,gz":
                header = ["t_ms", "ax", "ay", "az", "gx", "gy", "gz"]
                if args.label:
                    header.append("label")
                print("Cabecera detectada ✔")
                break
        if time.time() - start_sync > 10:
            print("No se detectó cabecera en 10 s. ¿Subiste el sketch que imprime CSV con cabecera?")
            print("Continuaré igualmente, usando el orden: ax,ay,az,gx,gy,gz")
            header = ["t_ms", "ax", "ay", "az", "gx", "gy", "gz"] + (["label"] if args.label else [])
            break

    # Abrir CSV de salida
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)

        t0 = time.time()
        n = 0
        try:
            while True:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if not line:
                    continue

                # Saltar líneas de cabecera repetidas
                if line.lower().replace(" ", "") == "ax,ay,az,gx,gy,gz":
                    continue

                # Espera formato: ax,ay,az,gx,gy,gz
                parts = line.split(",")
                if len(parts) != 6:
                    # si llega ruido, lo ignora
                    continue

                try:
                    ax, ay, az, gx, gy, gz = map(float, parts)
                except ValueError:
                    continue

                t_ms = int((time.time() - t0) * 1000)
                row = [t_ms, ax, ay, az, gx, gy, gz]
                if args.label:
                    row.append(args.label)
                writer.writerow(row)
                n += 1

                # corte por tiempo (si se indicó)
                if args.seconds > 0 and (time.time() - t0) >= args.seconds:
                    break
        except KeyboardInterrupt:
            print("\nInterrumpido por usuario (Ctrl+C).")
        finally:
            ser.close()
            print(f"Cerrado. Muestras capturadas: {n}")
            print(f"Archivo CSV: {out_path}")

if __name__ == "__main__":
    main()

