import os
from pathlib import Path
from PIL import Image

def create_multi_object_image():
    brain_dir = Path(r"C:\Users\subha\.gemini\antigravity\brain\4e2241bf-aba3-49be-b535-6cfb7ec1f861")
    
    img_cucumber = Image.open(brain_dir / "cucumber_1773414355643.png").resize((320, 320))
    img_urchin = Image.open(brain_dir / "urchin_1773414395017.png").resize((320, 320))
    img_shell = Image.open(brain_dir / "shell_1773414639843.png").resize((320, 320))
    img_negative = Image.open(brain_dir / "negative_fish_1773414672616.png").resize((320, 320))
    
    # Create 640x640 canvas
    canvas = Image.new("RGB", (640, 640))
    
    # Paste images
    canvas.paste(img_cucumber, (0, 0))         # Top-Left
    canvas.paste(img_urchin, (320, 0))         # Top-Right
    canvas.paste(img_shell, (0, 320))          # Bottom-Left
    canvas.paste(img_negative, (320, 320))     # Bottom-Right
    
    out_path = brain_dir / "multi_treasure.png"
    canvas.save(out_path)
    print(f"Created multi-object image: {out_path}")

if __name__ == "__main__":
    create_multi_object_image()
