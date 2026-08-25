import csv
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent.parent.parent / "logs" / "scraping_log.csv"





if __name__ == "__main__":
    print(Path(__file__).resolve())