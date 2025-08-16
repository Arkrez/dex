# classifier.py
import numpy as np, PIL.Image as Image
from tflite_runtime.interpreter import Interpreter

class SpeciesClassifier:
    def __init__(self, model_path, labels_path):
        self.labels = [l.strip() for l in open(labels_path, 'r', encoding='utf-8')]
        self.interp = Interpreter(model_path=model_path, num_threads=4)
        self.interp.allocate_tensors()
        self.in_det = self.interp.get_input_details()[0]
        self.out_det = self.interp.get_output_details()[0]
        _, self.h, self.w, _ = self.in_det['shape']

    def classify(self, img_path, top_k=3):
        img = Image.open(img_path).convert('RGB').resize((self.w, self.h))
        x = np.asarray(img, dtype=np.float32) / 255.0
        x = np.expand_dims(x, 0)
        self.interp.set_tensor(self.in_det['index'], x)
        self.interp.invoke()
        probs = self.interp.get_tensor(self.out_det['index'])[0]
        idxs = probs.argsort()[-top_k:][::-1]
        return [(self.labels[i], float(probs[i])) for i in idxs]
