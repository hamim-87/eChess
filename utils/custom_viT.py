import os
from PIL import Image
import torch
from torchvision import transforms
import timm

# Parameters
folder_path = "chess_cells"
model_name = "vit_tiny_patch16_224"
num_classes = 3
image_size = 224
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

# Define transform (same as training)
transform = transforms.Compose([
    transforms.Resize((image_size, image_size)),
    transforms.ToTensor(),
])

# Load model
model = timm.create_model(model_name, pretrained=False, num_classes=num_classes)
model.load_state_dict(torch.load("best.pt", map_location=device))
model.to(device)
model.eval()
print("✅ Loaded model from best.pt")

# Simulate class names (you can load from your original dataset if needed)
class_names = ['class_1', 'class_2', 'class_3']

# Load and preprocess images
images = []
image_paths = []

for fname in os.listdir(folder_path):
    if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
        path = os.path.join(folder_path, fname)
        img = Image.open(path).convert("RGB")
        img = transform(img)
        images.append(img)
        image_paths.append(fname)

# If no images found
if not images:
    print("❌ No images found in folder:", folder_path)
    exit()

# Create batch
batch = torch.stack(images).to(device)

# Inference
with torch.no_grad():
    outputs = model(batch)
    _, preds = torch.max(outputs, 1)

# Print predictions
print("\n📌 Predictions:")
for i in range(len(preds)):
    print(f"{image_paths[i]} → {class_names[preds[i].item()]}")