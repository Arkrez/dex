# classifier.py
import numpy as np
from PIL import Image
import subprocess
from pathlib import Path
import json
import json, os, sys, tempfile, subprocess

#from tensorflow.keras.preprocessing import image

# Load model (after extracting model.tar.gz somewhere, e.g. ~/Downloads/model)
#model = tf.keras.models.load_model("/Users/arkrez/Downloads/model")

# Path to your images
#img_dir = pathlib.Path("assets")

#for img_path in img_dir.glob("*.jpg"):
#    img = image.load_img(img_path, target_size=(224, 224))  # adjust size to match model input
#    x = image.img_to_array(img)
#    x = np.expand_dims(x, axis=0) / 255.0
#
#    preds = model.predict(x)
#    print(img_path.name, preds.argmax())



class SpeciesClassifier:        
    def classify_v2(self, image_path):
        BASE = Path(__file__).resolve().parent
        OUT_PATH = str(BASE / "assets" / "out.json")
        subprocess.run([            
            sys.executable,
            "-m", 
            "speciesnet.scripts.run_model",
            "--filepaths", 
            image_path,
            "--predictions_json", 
            OUT_PATH
        ])
        with open(OUT_PATH, 'r') as file:
            data = json.load(file)
        arr = data["predictions"][0]["prediction"].split(';')
        res = [arr[-1], data["predictions"][0]["prediction_score"]]
        print(res)
        return res

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
