import csv
from datetime import datetime
from pathlib import Path
import random
import time

LOG_FILE = Path(__file__).resolve().parent.parent.parent / "logs" / "scraping_log.csv"


def log_request(request_type, url, outcome, status_code="", note=""):

    file_exists = LOG_FILE.exists() and LOG_FILE.stat().st_size > 0

    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["timestamp", "request_type", "url", "status_code", "outcome", "note"])

        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            request_type,
            url,
            status_code,
            outcome,
            note,
        ])

def polite_delay(min_seconds=5, max_seconds=11):

    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)
    return delay


if __name__ == "__main__":
    print(Path(__file__).resolve())
    log_request("search", "https://amazon.com/s?k=test", "success", 200, "test entry")
    waited = polite_delay()
    print(f"Waited {waited:.2f} seconds")