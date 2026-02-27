import serial
import csv
import os

CSV_FILE = "gesture_dataset3.csv"
FRAMES = 120

ser = serial.Serial("/dev/rfcomm0", 115200, timeout=1)

file_exists = os.path.isfile(CSV_FILE)

with open(CSV_FILE, mode="a", newline="") as f:
    writer = csv.writer(f)

    if not file_exists:
        writer.writerow([
            "flex1","flex2","flex3","flex4","flex5",
            "ax","ay","az","gx","gy","gz","label"
        ])

    while True:
        label = input("Enter label (or EXIT): ").upper()
        if label == "EXIT":
            break

        count = 0
        print("Recording", label)

        while count < FRAMES:
            line = ser.readline().decode(errors="ignore").strip()
            if not line:
                continue

            values = line.split(",")
            if len(values) != 11:
                continue

            writer.writerow(values + [label])
            f.flush()

            count += 1

        print(label, "saved\n")
