import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# ===============================
# LOAD CLEAN DATASET
# ===============================
df = pd.read_csv("gesture_dataset_cleaned.csv")

# ===============================
# SPLIT FEATURES AND LABEL
# ===============================
X = df.drop("label", axis=1)
y = df["label"]

# ===============================
# SCALE FEATURES
# ===============================
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ===============================
# TRAIN / TEST SPLIT (STRATIFIED)
# ===============================
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ===============================
# MODEL DEFINITION
# ===============================
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

# ===============================
# TRAIN
# ===============================
model.fit(X_train, y_train)

# ===============================
# EVALUATE
# ===============================
y_pred = model.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

# ===============================
# SAVE MODEL & SCALER
# ===============================
joblib.dump(model, "gesture_model25.pkl")
joblib.dump(scaler, "scaler25.pkl")

print("\nModel and scaler saved.")
