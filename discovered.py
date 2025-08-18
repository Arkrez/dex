# discovered.py
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "discovered.json"

def load():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        return set(json.loads(DB_PATH.read_text(encoding="utf-8")))
    return set()

def save(items):
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    DB_PATH.write_text(json.dumps(sorted(items)), encoding="utf-8")
