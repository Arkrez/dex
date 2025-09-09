# classifier.py
import json, os, sys, tempfile, subprocess
from pathlib import Path

class SpeciesClassifier:
    def classify_v2(self, image_path: str):
        BASE = Path(__file__).resolve().parent
        BASE.joinpath("assets").mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(prefix="speciesnet_", suffix=".json", dir=BASE/"assets", delete=False) as tmp:
            out_path = tmp.name

        env = os.environ.copy()
        env.setdefault("OMP_NUM_THREADS", "1")
        env.setdefault("OPENBLAS_NUM_THREADS", "1")
        env.setdefault("TF_NUM_INTEROP_THREADS", "1")
        env.setdefault("TF_NUM_INTRAOP_THREADS", "1")
        env.setdefault("MALLOC_ARENA_MAX", "2")

        cmd = [
            sys.executable, "-m", "speciesnet.scripts.run_model",
            "--filepaths", image_path,
            "--predictions_json", out_path,
        ]
        try:
            r = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True, timeout=120)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"speciesnet failed (exit {e.returncode}).\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}") from e
        except subprocess.TimeoutExpired as e:
            raise RuntimeError(f"speciesnet timed out after {e.timeout}s.\n(partial STDOUT/ERR captured)") from e

        if r.returncode < 0:
            raise RuntimeError(f"speciesnet crashed with signal {abs(r.returncode)}.\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}")

        if not Path(out_path).exists() or Path(out_path).stat().st_size == 0:
            raise RuntimeError(f"speciesnet produced no output at {out_path}.\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}")

        with open(out_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        pred = data["predictions"][0]
        label = pred["prediction"].split(";")[-1]
        score = float(pred["prediction_score"])
        return [label, score]
