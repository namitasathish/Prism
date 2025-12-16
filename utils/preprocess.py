# utils/preprocess.py
import re

def clean_text(text: str) -> str:
    if text is None:
        return ""
    t = text.lower()
    # remove urls
    t = re.sub(r"http\S+|www\S+|https\S+", "", t)
    # remove mentions and emojis (simple)
    t = re.sub(r"<@!?\d+>", "", t)
    # remove non-alphanumeric (keep spaces)
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    # collapse whitespace
    t = re.sub(r"\s+", " ", t).strip()
    return t
