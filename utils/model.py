from ultralytics import YOLO
import os
from PIL import Image
import torch

# ---------- Free GPU memory ----------
torch.cuda.empty_cache()

# ---------- Load YOLO model ----------
model_path = "yolov11.pt"  # Replace if needed
model = YOLO(model_path)
model.fuse()  # Optional speed-up

# ---------- Load images ----------
def load_images(folder_path, max_images=640):
    image_data = []
    filenames = sorted(os.listdir(folder_path))[:max_images]
    for filename in filenames:
        path = os.path.join(folder_path, filename)
        if path.lower().endswith(('.png', '.jpg', '.jpeg')):
            img = Image.open(path).convert("RGB")
            image_data.append((img, filename))
    return image_data

folder = "./chess_cells"
image_data = load_images(folder)

# ---------- Run inference ----------
for image, name in image_data:
    try:
        results = model.predict(image, imgsz=320, device=0, verbose=False)

        if not results or results[0].boxes is None:
            print(f"Image: {name} -> No detections")
            continue

        print(f"Image: {name}")
        for box in results[0].boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].tolist()
            print(f"  Class: {cls}, Conf: {conf:.2f}, Box: {xyxy}")

        torch.cuda.empty_cache()

    except Exception as e:
        print(f"Failed on {name}: {e}")
