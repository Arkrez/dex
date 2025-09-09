# classifier.py
import json, os, sys, subprocess, time
from pathlib import Path

class SpeciesClassifier:
    def classify_v2(self, image_path: str):
        BASE = Path(__file__).resolve().parent
        assets = BASE / "assets"
        assets.mkdir(parents=True, exist_ok=True)
        out_path = assets / f"speciesnet_{time.strftime('%Y%m%d_%H%M%S')}.json"

        # ensure the path does NOT exist so SpeciesNet won't try to load partials
        try:
            out_path.unlink()
        except FileNotFoundError:
            pass

        env = os.environ.copy()
        env.setdefault("OMP_NUM_THREADS", "1")
        env.setdefault("OPENBLAS_NUM_THREADS", "1")
        env.setdefault("TF_NUM_INTEROP_THREADS", "1")
        env.setdefault("TF_NUM_INTRAOP_THREADS", "1")
        env.setdefault("MALLOC_ARENA_MAX", "2")

        cmd = [sys.executable, "-m", "speciesnet.scripts.run_model",
               "--filepaths", image_path,
               "--predictions_json", str(out_path)]

        r = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True)

        with open(out_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        pred = data["predictions"][0]
        return [pred["prediction"].split(";")[-1], float(pred["prediction_score"])]
