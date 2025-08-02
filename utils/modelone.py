from ultralytics import YOLO
from PIL import Image
import numpy as np
import torch

torch.cuda.empty_cache()
model = YOLO("yolov11.pt")  # Classification model

image_path = "chess_cells/2_0.png"
image = Image.open(image_path)
image_np = np.array(image)

# Inference
results = model.predict(image_np, imgsz=640, device=0, conf=0.1, verbose=True)
r = results[0]

# Get predicted class
probs = r.probs
if probs is not None:
    best_class_id = int(probs.top1)
    confidence = float(probs.data[best_class_id])
    class_name = model.names[best_class_id]
    print(f"Predicted Class: {class_name} (ID: {best_class_id}), Confidence: {confidence:.2f}")
else:
    print("No prediction made.")
