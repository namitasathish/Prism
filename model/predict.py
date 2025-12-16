# model/predict.py
import joblib
import os
from config import MODEL_PATH
from utils.preprocess import clean_text

_model = None
_classes = None

def load_model():
    global _model, _classes
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Train it first.")
        _model = joblib.load(MODEL_PATH)
        # sklearn pipeline has classes_ on the classifier step
        try:
            _classes = _model.named_steps['clf'].classes_
        except Exception:
            _classes = None
    return _model

def predict(text: str):
    """
    Returns: (label:str, prob:float) where prob is the probability for predicted label
    """
    model = load_model()
    cleaned = clean_text(text)
    probs = model.predict_proba([cleaned])[0]  # array of probs
    pred_idx = probs.argmax()
    label = model.named_steps['clf'].classes_[pred_idx]
    return label, float(probs[pred_idx])
