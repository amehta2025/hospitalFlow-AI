import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import random


def generate_training_data(n_samples: int = 1000) -> tuple:
    X = []
    y = []

    for _ in range(n_samples):
        scenario = random.choice(["normal", "normal", "surge", "icu_full", "lab_delay"])

        if scenario == "normal":
            ed_wait = random.uniform(10, 55)
            icu_wait = random.uniform(10, 45)
            lab_wait = random.uniform(20, 55)
            discharge_wait = random.uniform(20, 45)
            transport_wait = random.uniform(5, 25)
            high_severity_pct = random.uniform(5, 30)
            hour = random.randint(0, 23)
            label = 0

        elif scenario == "surge":
            ed_wait = random.uniform(70, 140)
            icu_wait = random.uniform(50, 100)
            lab_wait = random.uniform(60, 120)
            discharge_wait = random.uniform(50, 100)
            transport_wait = random.uniform(20, 50)
            high_severity_pct = random.uniform(40, 75)
            hour = random.randint(10, 22)
            label = 1

        elif scenario == "icu_full":
            ed_wait = random.uniform(60, 120)
            icu_wait = random.uniform(80, 150)
            lab_wait = random.uniform(30, 70)
            discharge_wait = random.uniform(60, 110)
            transport_wait = random.uniform(15, 40)
            high_severity_pct = random.uniform(35, 65)
            hour = random.randint(8, 22)
            label = 1

        elif scenario == "lab_delay":
            ed_wait = random.uniform(40, 90)
            icu_wait = random.uniform(20, 60)
            lab_wait = random.uniform(90, 160)
            discharge_wait = random.uniform(30, 70)
            transport_wait = random.uniform(10, 30)
            high_severity_pct = random.uniform(25, 55)
            hour = random.randint(6, 20)
            label = 1 if lab_wait > 110 else 0

        X.append([
            ed_wait, icu_wait, lab_wait,
            discharge_wait, transport_wait,
            high_severity_pct, hour
        ])
        y.append(label)

    return np.array(X), np.array(y)


print("Training ED risk prediction model...")
X_train, y_train = generate_training_data(n_samples=2000)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_scaled, y_train)
print(f"Model trained. Crisis rate in training data: {y_train.mean():.1%}")

FEATURE_NAMES = [
    "ed_avg_wait_minutes",
    "icu_avg_wait_minutes",
    "lab_avg_wait_minutes",
    "discharge_avg_wait_minutes",
    "transport_avg_wait_minutes",
    "recent_high_severity_pct",
    "hour_of_day",
]


def predict_risk(metrics: dict) -> dict:
    from datetime import datetime
    hour = datetime.utcnow().hour

    features = np.array([[
        metrics.get("ed_avg_wait_minutes", 0),
        metrics.get("icu_avg_wait_minutes", 0),
        metrics.get("lab_avg_wait_minutes", 0),
        metrics.get("discharge_avg_wait_minutes", 0),
        metrics.get("transport_avg_wait_minutes", 0),
        metrics.get("recent_high_severity_pct", 0),
        hour,
    ]])

    features_scaled = scaler.transform(features)
    risk_score = model.predict_proba(features_scaled)[0][1]
    prediction = "high" if risk_score > 0.6 else "medium" if risk_score > 0.3 else "low"

    importances = model.feature_importances_
    feature_values = features[0]
    top_factors = []

    sorted_idx = np.argsort(importances)[::-1]
    for idx in sorted_idx[:3]:
        top_factors.append({
            "factor": FEATURE_NAMES[idx],
            "importance": round(float(importances[idx]), 3),
            "current_value": round(float(feature_values[idx]), 1),
        })

    return {
        "risk_score": round(float(risk_score), 3),
        "risk_level": prediction,
        "prediction": f"{'High' if prediction == 'high' else 'Medium' if prediction == 'medium' else 'Low'} risk of ED boarding crisis",
        "top_factors": top_factors,
    }