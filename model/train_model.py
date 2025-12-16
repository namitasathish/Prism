# model/train_model.py
import sys, os

# Add parent directory (project root: prism/) to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import joblib

from config import DATA_PATH, MODEL_PATH
from utils.preprocess import clean_text


def load_data(path=DATA_PATH):
    df = pd.read_csv(path)
    # expect columns: text,label
    df = df.dropna(subset=["text", "label"])
    df["text"] = df["text"].astype(str).apply(clean_text)
    return df


def train_and_save():
    df = load_data()
    X = df["text"].tolist()
    y = df["label"].tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )

    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
        ("clf", LogisticRegression(max_iter=1000))
    ])

    print("Training model...")
    pipe.fit(X_train, y_train)
    preds = pipe.predict(X_test)

    print("Accuracy:", accuracy_score(y_test, preds))
    print("Classification report:")
    print(classification_report(y_test, preds))

    # ensure models directory exists
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(pipe, MODEL_PATH)
    print(f"Saved model pipeline to {MODEL_PATH}")


if __name__ == "__main__":
    train_and_save()
