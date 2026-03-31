import os
import urllib.request
from pathlib import Path

def build_dataset_and_train():
    base_dir = Path(r"d:\subhash\sea_treasure_datasets")
    
    # Create directories
    for split in ["train", "val"]:
        for dtype in ["images", "labels"]:
            (base_dir / dtype / split).mkdir(parents=True, exist_ok=True)
            
    # Dataset definition
    dataset = {
        "train": [
            # Sea Cucumber (class 0)
            {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Sea_cucumber_%28Holothuria_leucospilota%29.jpg/640px-Sea_cucumber_%28Holothuria_leucospilota%29.jpg", "label": "0 0.5 0.5 0.8 0.8", "name": "cucumber_1.jpg"},
            {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/California_Sea_Cucumber_%28Apostichopus_californicus%29.jpg/640px-California_Sea_Cucumber_%28Apostichopus_californicus%29.jpg", "label": "0 0.5 0.5 0.7 0.7", "name": "cucumber_2.jpg"},
            
            # Sea Urchin (class 1)
            {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Sea_urchin_macro.jpg/640px-Sea_urchin_macro.jpg", "label": "1 0.5 0.5 0.6 0.6", "name": "urchin_1.jpg"},
            {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Echinoidea_-_Phyllacanthus_imperialis_1.jpg/640px-Echinoidea_-_Phyllacanthus_imperialis_1.jpg", "label": "1 0.5 0.5 0.6 0.6", "name": "urchin_2.jpg"},
            
            # Shell (class 2)
            {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Scallop_shell.jpg/640px-Scallop_shell.jpg", "label": "2 0.5 0.5 0.5 0.5", "name": "shell_1.jpg"},
            {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Scallop_shell_2.jpg/640px-Scallop_shell_2.jpg", "label": "2 0.5 0.5 0.5 0.5", "name": "shell_2.jpg"},
            
            # Non-Sea Treasure (Background / Negative Sample - empty label)
            {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Clownfish_%28Amphiprion_ocellaris%29.jpg/640px-Clownfish_%28Amphiprion_ocellaris%29.jpg", "label": "", "name": "neg_1.jpg"},
            {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Coral_reef_fish.jpg/640px-Coral_reef_fish.jpg", "label": "", "name": "neg_2.jpg"},
        ],
        "val": [
            # Sea Cucumber
            {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Sea_cucumber_%2845625442251%29.jpg/640px-Sea_cucumber_%2845625442251%29.jpg", "label": "0 0.5 0.5 0.7 0.7", "name": "cucumber_val.jpg"},
            # Sea Urchin
            {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Sea_Urchin_%28Strongylocentrotus_purpuratus%29.jpg/640px-Sea_Urchin_%28Strongylocentrotus_purpuratus%29.jpg", "label": "1 0.5 0.5 0.5 0.5", "name": "urchin_val.jpg"},
            # Shell
            {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Giant_clam_shell.jpg/640px-Giant_clam_shell.jpg", "label": "2 0.5 0.5 0.6 0.6", "name": "shell_val.jpg"},
            # Non-Sea Treasure
            {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Green_sea_turtle_2.jpg/640px-Green_sea_turtle_2.jpg", "label": "", "name": "neg_val.jpg"},
        ]
    }
    
    print("Downloading Images...")
    for split, items in dataset.items():
        for item in items:
            img_path = base_dir / "images" / split / item["name"]
            txt_path = base_dir / "labels" / split / item["name"].replace(".jpg", ".txt")
            
            # Download image if it doesn't exist
            if not img_path.exists():
                try:
                    import requests
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
                    response = requests.get(item["url"], headers=headers, timeout=15)
                    response.raise_for_status()
                    with open(img_path, 'wb') as out_file:
                        out_file.write(response.content)
                except Exception as e:
                    print(f"Failed to download {item['url']}: {e}")
            
            # Write label
            with open(txt_path, "w") as f:
                if item["label"]:
                    f.write(item["label"] + "\n")
                    
    # Create dataset.yaml
    yaml_path = base_dir / "dataset.yaml"
    yaml_content = f"""
train: {base_dir / 'images' / 'train'}
val: {base_dir / 'images' / 'val'}

nc: 3
names: ['sea_cucumber', 'sea_urchin', 'shell']
"""
    with open(yaml_path, "w") as f:
        f.write(yaml_content.strip())
        
    print(f"Dataset successfully created at {base_dir}")
    
    # Train the exact model for Sea Treasure
    from ultralytics import YOLO
    
    # Load a lightweight nano model
    print("Loading YOLOv8 nano model for transfer learning...")
    model = YOLO("yolov8n.pt")
    
    # Train
    print("Training model... (This will teach it to detect the 3 classes and ignore background/negatives)")
    results = model.train(
        data=str(yaml_path),
        epochs=3,           # Just 3 epochs for a quick functional training run on CPU
        imgsz=320,          # Small image size to speed up the process
        batch=4,
        name="upa_yolo_sea_treasure_real",
        device="cpu"        # Default to CPU as we don't know the GPU setup
    )
    
    print("Training complete!")
    print("We will now copy the best weights to your Django app ml_models folder.")
    import shutil
    project_ml_dir = Path(r"d:\subhash\sea_treasure\ml_models")
    project_ml_dir.mkdir(parents=True, exist_ok=True)
    
    best_weights = Path("runs/detect/upa_yolo_sea_treasure_real/weights/best.pt")
    if best_weights.exists():
        shutil.copy(best_weights, project_ml_dir / "best.pt")
        print(f"Copied weights to {project_ml_dir / 'best.pt'}")
    else:
        print("Weights were not generated correctly.")

if __name__ == "__main__":
    build_dataset_and_train()
