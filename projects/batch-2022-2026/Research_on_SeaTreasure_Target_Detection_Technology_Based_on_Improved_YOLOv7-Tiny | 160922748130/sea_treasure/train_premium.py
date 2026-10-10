import os
import random
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
import shutil
from ultralytics import YOLO
import time

# --- Configuration ---
PROJECT_ROOT = Path(r"d:\subhash\sea_treasure")
DATASET_DIR = Path(r"d:\subhash\sea_treasure_dataset_v3")
OLD_BRAIN = Path(r"C:\Users\subha\.gemini\antigravity\brain\4e2241bf-aba3-49be-b535-6cfb7ec1f861")
NEW_BRAIN = Path(r"C:\Users\subha\.gemini\antigravity\brain\8b1b33bd-49f4-44cd-a401-31b2ef787ff5")

def advanced_augment(img, label_lines):
    # Random Rotate (small angle)
    if random.random() < 0.5:
        angle = random.uniform(-15, 15)
        img = img.rotate(angle, expand=False, fillcolor=(0,0,0))
    
    # Flip Horizontal
    if random.random() < 0.5:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        new_lines = []
        for line in label_lines:
            c, x, y, w, h = map(float, line.split())
            new_lines.append(f"{int(c)} {1.0-x:.4f} {y:.4f} {w:.4f} {h:.4f}")
        label_lines = new_lines

    # Jitter
    enhancers = [ImageEnhance.Brightness, ImageEnhance.Contrast, ImageEnhance.Color]
    for enhancer_cls in enhancers:
        img = enhancer_cls(img).enhance(random.uniform(0.7, 1.3))
    
    # Random Blur
    if random.random() < 0.2:
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.5)))

    return img, label_lines

def build_and_train():
    if DATASET_DIR.exists():
        shutil.rmtree(DATASET_DIR)
    
    for split in ["train", "val"]:
        for dtype in ["images", "labels"]:
            (DATASET_DIR / dtype / split).mkdir(parents=True, exist_ok=True)

    # Base assets
    base_assets = [
        {"class": 0, "name": "cucumber_v1", "path": OLD_BRAIN / "cucumber_1773414355643.png"},
        {"class": 0, "name": "cucumber_v2", "path": NEW_BRAIN / "sea_cucumber_2_1773471360743.png"},
        {"class": 1, "name": "urchin_v1",   "path": OLD_BRAIN / "urchin_1773414395017.png"},
        {"class": 1, "name": "urchin_v2",   "path": NEW_BRAIN / "sea_urchin_2_1773471389304.png"},
        {"class": 2, "name": "shell",       "path": OLD_BRAIN / "shell_1773414639843.png"},
        {"class": 3, "name": "fish_ignore", "path": OLD_BRAIN / "negative_fish_1773414672616.png"}, 
    ]

    print("Building Premium 'Human-Logic' Dataset v3...")
    for asset in base_assets:
        p = Path(asset["path"])
        if not p.exists():
            print(f"Skipping {asset['name']} (not found)")
            continue
        
        base_img = Image.open(p).convert("RGB")
        label = f"{asset['class']} 0.5 0.5 0.7 0.7"
        
        # 100 images per asset for extreme accuracy
        for i in range(100):
            split = "train" if i < 80 else "val"
            aug_img, lines = advanced_augment(base_img.copy(), [label])
            
            name = f"human_brain_{asset['name']}_{i}"
            aug_img.save(DATASET_DIR / "images" / split / f"{name}.png")
            with open(DATASET_DIR / "labels" / split / f"{name}.txt", "w") as f:
                f.write("\n".join(lines) + "\n")

    # Yaml
    yaml_path = DATASET_DIR / "data.yaml"
    with open(yaml_path, "w") as f:
        f.write(f"path: {DATASET_DIR}\ntrain: images/train\nval: images/val\nnc: 4\nnames: ['sea_cucumber', 'sea_urchin', 'shell', 'fish_ignore']\n")

    print("Starting Premium Training (10 epochs)...")
    model = YOLO("yolov8n.pt")
    model.train(
        data=str(yaml_path),
        epochs=10,
        imgsz=320,
        batch=16,
        project=str(PROJECT_ROOT),
        name="runs/premium_train_v3",
        device="cpu",
        exist_ok=True
    )

    # Deploy
    best = PROJECT_ROOT / "runs/premium_train_v3/weights/best.pt"
    dest = PROJECT_ROOT / "ml_models/best.pt"
    if best.exists():
        shutil.copy(best, dest)
        print(f"DEPLOYED PREMIUM MODEL TO {dest}")

if __name__ == "__main__":
    build_and_train()
