import time
import serial
import joblib
import numpy as np
import pandas as pd
from collections import deque

import board
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# ===============================
# CONFIGURATION
# ===============================
PORT = "/dev/rfcomm0"
BAUD = 115200

MODEL_FILE = "gesture_model25.pkl"
SCALER_FILE = "scaler25.pkl"

WINDOW_SIZE = 5
CONFIDENCE_THRESHOLD = 0.55

FEATURES = [
    "flex1", "flex2", "flex3", "flex4", "flex5",
    "ax", "ay", "az",
    "gx", "gy", "gz"
]

# ===============================
# OLED SETUP
# ===============================
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)
oled.fill(0)
oled.show()

image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)

try:
    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20
    )
except:
    font = ImageFont.load_default()

def oled_text(text):
    draw.rectangle((0, 0, oled.width, oled.height), fill=0)
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(((oled.width - w)//2, (oled.height - h)//2),
              text, font=font, fill=255)
    oled.image(image)
    oled.show()

# ===============================
# LOAD MODEL
# ===============================
model = joblib.load(MODEL_FILE)
scaler = joblib.load(SCALER_FILE)

buffer = deque(maxlen=WINDOW_SIZE)
last_prediction = None

# ===============================
# AUTO CONNECT FUNCTION
# ===============================
def connect_serial():
    oled_text("CONNECTING")
    while True:
        try:
            ser = serial.Serial(PORT, BAUD, timeout=0.5)
            time.sleep(1)
            oled_text("CONNECTED")
            return ser
        except serial.SerialException:
            time.sleep(1)

# ===============================
# MAIN LOOP
# ===============================
ser = connect_serial()

while True:
    try:
        try:
            line = ser.readline().decode(errors="ignore").strip()
        except serial.SerialException:
            try:
                ser.close()
            except:
                pass
            buffer.clear()
            last_prediction = None
            oled_text("DISCONNECTED")
            time.sleep(1)
            ser = connect_serial()
            continue

        if not line:
            continue

        values = line.split(",")
        if len(values) != 11:
            continue

        frame = pd.DataFrame([values], columns=FEATURES, dtype=float)
        frame_scaled = scaler.transform(frame)

        probs = model.predict_proba(frame_scaled)[0]
        confidence = np.max(probs)

        if confidence < CONFIDENCE_THRESHOLD:
            continue

        prediction = model.classes_[np.argmax(probs)]
        buffer.append(prediction)

        final_prediction = max(set(buffer), key=buffer.count)

        if final_prediction != last_prediction:
            oled_text(final_prediction)
            last_prediction = final_prediction

    except KeyboardInterrupt:
        oled.fill(0)
        oled.show()
        try:
            ser.close()
        except:
            pass
        break
