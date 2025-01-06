# utils/last_updated.py

from datetime import datetime, timedelta

def last_updated():
    current_time = datetime.now()
    est_time = current_time - timedelta(hours=5)  # Convert to EST
    return est_time.strftime('%Y-%m-%d')