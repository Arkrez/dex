# classifier.py
import csv
import numpy as np
from PIL import Image
import tflite_runtime.interpreter as tflite

def load_labels_from_csv(csv_path: str):
    labels = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("leaf_class_id") and row.get("name"):
                try:
                    labels[int(row["leaf_class_id"])] = row["name"]
                except ValueError:
                    pass
    return labels

class SpeciesClassifier:
    def __init__(self, model_path, csv_path):
        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.labels = load_labels_from_csv(csv_path)
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()


    def classify(self, image_path, top_k=1):
        # Load and resize image to match model input
        input_shape = self.input_details[0]['shape']
        height, width = input_shape[1], input_shape[2]
        img = Image.open(image_path).convert("RGB").resize((width, height))
        input_data = np.expand_dims(img, axis=0).astype(self.input_details[0]['dtype'])

        # Feed the tensor
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)

        # Run inference
        self.interpreter.invoke()
        output = self.interpreter.get_tensor(self.output_details[0]['index'])[0]

        # Pick top_k results
        top_idx = output.argsort()[-top_k:][::-1]
        return [(self.labels.get(i, f"Unknown-{i}"), float(output[i])) for i in top_idx]
