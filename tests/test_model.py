# tests/test_model.py
from model.predict import predict
def test_predict_basic():
    label, prob = predict("You are such a loser and worthless")
    assert label in ["bullying","spam","scam","normal"]
    assert 0.0 <= prob <= 1.0
