# classifier.py
import csv
import numpy as np, PIL.Image as Image
from tflite_runtime.interpreter import Interpreter
class SpeciesClassifier:
    def __init__(self, model_path, csv_path):
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.labels = load_labels_from_csv(csv_path)
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def classify(self, image_path, top_k=1):
        # ... preprocess & run as before ...
        output = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
        top_indices = output.argsort()[-top_k:][::-1]
        return [(self.labels.get(i, f"Unknown-{i}"), float(output[i])) for i in top_indices]


    def load_labels_from_csv(csv_path: str):
        """
        Returns a dict mapping leaf_class_id (int) -> species name (str).
        Only rows with a leaf_class_id and name will be included.
        """
        labels = {}
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("leaf_class_id") and row.get("name"):
                    try:
                        leaf_id = int(row["leaf_class_id"])
                        labels[leaf_id] = row["name"]
                    except ValueError:
                        continue
        return labels
