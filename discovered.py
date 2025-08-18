# discovered.py
import json, time, shutil
from pathlib import Path

ROOT = Path(__file__).parent
DB_PATH = ROOT / "data" / "discovered.json"
DISC_DIR = ROOT / "discovered"

def _slug(name: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in name).strip("_")

def load_db() -> dict:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        return json.loads(DB_PATH.read_text(encoding="utf-8"))
    return {}  # {name: {"images":[...], "count": int, "first_seen": ts, "last_seen": ts}}

def save_db(db: dict) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    DB_PATH.write_text(json.dumps(db, indent=2, ensure_ascii=False), encoding="utf-8")

def discovered_names(db: dict) -> set[str]:
    return set(db.keys())

def add_discovery(name: str, src_image_path: str, prob: float) -> str:
    """
    Copies the image into ./discovered/<slug>/<timestamp>.jpg and updates DB.
    Returns the repo-relative saved path string.
    """
    db = load_db()
    slug = _slug(name)
    DISC_DIR.mkdir(parents=True, exist_ok=True)
    species_dir = DISC_DIR / slug
    species_dir.mkdir(parents=True, exist_ok=True)

    ts = time.strftime("%Y%m%d_%H%M%S")
    dst = species_dir / f"{ts}.jpg"
    shutil.copy2(src_image_path, dst)

    rec = db.get(name, {"images": [], "count": 0, "first_seen": ts, "last_seen": ts})
    rec["images"].append(str(dst.relative_to(ROOT)))
    rec["count"] += 1
    rec["last_seen"] = ts
    db[name] = rec
    save_db(db)
    return str(dst)
