import json
import os
from datetime import datetime

REPORT_PATH = os.path.join(os.path.dirname(__file__), '..', 'report.html')
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'report_data.json')

def add_to_report(message, author, channel, prediction, confidence):
    """Save each flagged message entry and update the report data."""
    new_entry = {
        "message": message,
        "author": author,
        "channel": channel,
        "prediction": prediction,
        "confidence": confidence,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Load existing report data if present
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []

    data.append(new_entry)

    # Save updated data
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
