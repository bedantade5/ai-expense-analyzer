import os
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

MODEL_DIR = "models"
CLASSIFIER_PATH = os.path.join(MODEL_DIR, "classifier.joblib")
ANOMALY_PATH = os.path.join(MODEL_DIR, "anomaly_detector.joblib")
TRAINING_DATA_PATH = "training_data.csv"

os.makedirs(MODEL_DIR, exist_ok=True)


def _load_training_data() -> pd.DataFrame:
    if not os.path.exists(TRAINING_DATA_PATH):
        raise FileNotFoundError(
            f"'{TRAINING_DATA_PATH}' not found. Run generate_dummy_data.py first."
        )
    df = pd.read_csv(TRAINING_DATA_PATH)
    required = {"Merchant", "Amount", "Category"}
    if not required.issubset(df.columns):
        raise ValueError(f"Training CSV must contain columns: {required}")
    return df


def train_classifier(df: pd.DataFrame = None) -> Pipeline:
    if df is None:
        df = _load_training_data()

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(2, 4),
            max_features=5000,
            sublinear_tf=True,
        )),
        ("clf", LogisticRegression(
            max_iter=1000,
            C=5.0,
            solver="lbfgs",
            multi_class="multinomial",
        )),
    ])

    pipeline.fit(df["Merchant"].str.lower(), df["Category"])
    joblib.dump(pipeline, CLASSIFIER_PATH)
    print(f"[✓] Classifier trained and saved → {CLASSIFIER_PATH}")
    return pipeline


def train_anomaly_detector(df: pd.DataFrame = None) -> IsolationForest:
    if df is None:
        df = _load_training_data()

    amounts = df["Amount"].values.reshape(-1, 1)
    detector = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=42,
    )
    detector.fit(amounts)
    joblib.dump(detector, ANOMALY_PATH)
    print(f"[✓] Anomaly detector trained and saved → {ANOMALY_PATH}")
    return detector


def load_classifier() -> Pipeline:
    if not os.path.exists(CLASSIFIER_PATH):
        print("[!] Classifier not found — training now...")
        return train_classifier()
    return joblib.load(CLASSIFIER_PATH)


def load_anomaly_detector() -> IsolationForest:
    if not os.path.exists(ANOMALY_PATH):
        print("[!] Anomaly detector not found — training now...")
        return train_anomaly_detector()
    return joblib.load(ANOMALY_PATH)


_classifier = None
_anomaly_detector = None


def _get_models():
    global _classifier, _anomaly_detector
    if _classifier is None:
        _classifier = load_classifier()
    if _anomaly_detector is None:
        _anomaly_detector = load_anomaly_detector()
    return _classifier, _anomaly_detector


def predict(merchant: str, amount: float) -> dict:
    classifier, anomaly_detector = _get_models()

    category = classifier.predict([merchant.lower()])[0]
    proba = classifier.predict_proba([merchant.lower()]).max()

    score = anomaly_detector.decision_function([[amount]])[0]
    is_anomaly = bool(anomaly_detector.predict([[amount]])[0] == -1)

    return {
        "category": category,
        "confidence": round(float(proba), 4),
        "is_anomaly": is_anomaly,
        "anomaly_score": round(float(score), 4),
    }


def predict_batch(merchants: list[str], amounts: list[float]) -> list[dict]:
    classifier, anomaly_detector = _get_models()

    merchants_lower = [m.lower() for m in merchants]
    categories = classifier.predict(merchants_lower)
    probas = classifier.predict_proba(merchants_lower).max(axis=1)

    amount_arr = np.array(amounts).reshape(-1, 1)
    anomaly_preds = anomaly_detector.predict(amount_arr)
    anomaly_scores = anomaly_detector.decision_function(amount_arr)

    results = []
    for i in range(len(merchants)):
        results.append({
            "category": categories[i],
            "confidence": round(float(probas[i]), 4),
            "is_anomaly": bool(anomaly_preds[i] == -1),
            "anomaly_score": round(float(anomaly_scores[i]), 4),
        })
    return results


def train_all():
    df = _load_training_data()
    train_classifier(df)
    train_anomaly_detector(df)
    print("[✓] All models trained successfully.")


if __name__ == "__main__":
    train_all()
    result = predict("Swiggy", 350.0)
    print(f"\nTest prediction → Swiggy ₹350: {result}")
    result2 = predict("Louis Vuitton", 95000.0)
    print(f"Test prediction → Louis Vuitton ₹95000: {result2}")
