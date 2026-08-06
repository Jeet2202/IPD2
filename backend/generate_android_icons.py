import os
from PIL import Image

src_logo = r"c:\Users\jeeta\Documents\IPD2\oops\assets\images\logos\ally_logo.png"
res_dir = r"c:\Users\jeeta\Documents\IPD2\oops\android\app\src\main\res"

sizes = {
    "mipmap-mdpi": (48, 48),
    "mipmap-hdpi": (72, 72),
    "mipmap-xhdpi": (96, 96),
    "mipmap-xxhdpi": (144, 144),
    "mipmap-xxxhdpi": (192, 192),
}

img = Image.open(src_logo).convert("RGBA")

for folder, (w, h) in sizes.items():
    target_dir = os.path.join(res_dir, folder)
    os.makedirs(target_dir, exist_ok=True)
    
    target_file = os.path.join(target_dir, "ic_launcher.png")
    
    resized = img.resize((w, h), Image.Resampling.LANCZOS)
    resized.save(target_file, "PNG")
    print(f"Saved {w}x{h} icon to: {target_file}")

print("Successfully updated all Android launcher icons!")
