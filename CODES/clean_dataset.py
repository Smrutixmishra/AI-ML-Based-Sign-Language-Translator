import pandas as pd

# ===============================
# LOAD RAW DATASET
# ===============================
df = pd.read_csv("gesture_dataset3.csv")
print("Original shape:", df.shape)

# ===============================
# DROP MISSING VALUES
# ===============================
df = df.dropna()

# ===============================
# REMOVE DUPLICATE ROWS
# ===============================
df = df.drop_duplicates()

# ===============================
# FILTER FLEX SENSOR RANGE (ESP32 ADC: 12-bit)
# ===============================
for i in range(1, 6):
    df = df[(df[f"flex{i}"] >= 0) & (df[f"flex{i}"] <= 4095)]

# ===============================
# FILTER ACCELEROMETER RANGE (±2g)
# ===============================
df = df[
    (df["ax"].between(-2, 2)) &
    (df["ay"].between(-2, 2)) &
    (df["az"].between(-2, 2))
]

# ===============================
# FILTER GYROSCOPE RANGE (deg/sec)
# ===============================
df = df[
    (df["gx"].between(-500, 500)) &
    (df["gy"].between(-500, 500)) &
    (df["gz"].between(-500, 500))
]

# ===============================
# NORMALIZE LABELS
# ===============================
df["label"] = df["label"].astype(str).str.upper().str.strip()

# ===============================
# SENSOR COLUMNS (EXPLICIT)
# ===============================
sensor_cols = [
    "flex1", "flex2", "flex3", "flex4", "flex5",
    "ax", "ay", "az",
    "gx", "gy", "gz"
]

# ===============================
# SMOOTH SENSOR DATA (ROLLING MEAN)
# ===============================
df[sensor_cols] = df.groupby("label")[sensor_cols].transform(
    lambda x: x.rolling(window=5, min_periods=1).mean()
)

# ===============================
# BALANCE DATASET
# ===============================
min_samples = df["label"].value_counts().min()
df = df.groupby("label").sample(min_samples, random_state=42)

# ===============================
# FINAL CHECK
# ===============================
print("Final shape:", df.shape)
print("\nSamples per label:")
print(df["label"].value_counts())

# ===============================
# SAVE CLEAN DATASET
# ===============================
df.to_csv("gesture_dataset_cleaned.csv", index=False)
print("\nCleaned dataset saved successfully.")