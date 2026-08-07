import os
import glob
from PIL import Image

src_path = r"C:\Users\jeeta\.gemini\antigravity-ide\brain\06ca6ae8-cb76-43a3-87f4-4ef6d9af6047\media__1786112727734.png"
base_dir = r"c:\Users\jeeta\Documents\IPD2"

# 1. Load source image
orig = Image.open(src_path).convert("RGBA")
width, height = orig.size

# Find bounding box of non-white content
img_rgb = orig.convert("RGB")
pixels = img_rgb.load()

left, top, right, bottom = width, height, 0, 0
for y in range(height):
    for x in range(width):
        r, g, b = pixels[x, y]
        if r < 245 or g < 245 or b < 245:
            if x < left: left = x
            if x > right: right = x
            if y < top: top = y
            if y > bottom: bottom = y

# Add padding
padding = 20
left = max(0, left - padding)
top = max(0, top - padding)
right = min(width, right + padding)
bottom = min(height, bottom + padding)

cropped = orig.crop((left, top, right, bottom))
print(f"Cropped logo size: {cropped.size}")

# Target directories
logos_dir = os.path.join(base_dir, "oops", "assets", "images", "logos")
os.makedirs(logos_dir, exist_ok=True)

# 2. Save main logo assets
logo_names = [
    "ally_logo.png",
    "app_logo.png",
    "logo_full.png",
    "logo_icon.png",
    "logo_white.png",
]

for name in logo_names:
    path = os.path.join(logos_dir, name)
    cropped.save(path, "PNG")
    print(f"Saved {path}")

# 3. Update Android mipmap launcher icons
android_res = os.path.join(base_dir, "oops", "android", "app", "src", "main", "res")
android_sizes = {
    "mipmap-mdpi": (48, 48),
    "mipmap-hdpi": (72, 72),
    "mipmap-xhdpi": (96, 96),
    "mipmap-xxhdpi": (144, 144),
    "mipmap-xxxhdpi": (192, 192),
}

for folder, (w, h) in android_sizes.items():
    target_dir = os.path.join(android_res, folder)
    os.makedirs(target_dir, exist_ok=True)
    target_file = os.path.join(target_dir, "ic_launcher.png")
    resized = cropped.resize((w, h), Image.Resampling.LANCZOS)
    resized.save(target_file, "PNG")
    print(f"Saved Android icon {w}x{h} -> {target_file}")

# 4. Update iOS launcher icons
ios_appicon_dir = os.path.join(base_dir, "oops", "ios", "Runner", "Assets.xcassets", "AppIcon.appiconset")
ios_sizes = {
    "Icon-App-20x20@1x.png": (20, 20),
    "Icon-App-20x20@2x.png": (40, 40),
    "Icon-App-20x20@3x.png": (60, 60),
    "Icon-App-29x29@1x.png": (29, 29),
    "Icon-App-29x29@2x.png": (58, 58),
    "Icon-App-29x29@3x.png": (87, 87),
    "Icon-App-40x40@1x.png": (40, 40),
    "Icon-App-40x40@2x.png": (80, 80),
    "Icon-App-40x40@3x.png": (120, 120),
    "Icon-App-60x60@2x.png": (120, 120),
    "Icon-App-60x60@3x.png": (180, 180),
    "Icon-App-76x76@1x.png": (76, 76),
    "Icon-App-76x76@2x.png": (152, 152),
    "Icon-App-83.5x83.5@2x.png": (167, 167),
    "Icon-App-1024x1024@1x.png": (1024, 1024),
}

if os.path.exists(ios_appicon_dir):
    for filename, (w, h) in ios_sizes.items():
        target_file = os.path.join(ios_appicon_dir, filename)
        resized = cropped.resize((w, h), Image.Resampling.LANCZOS)
        resized.save(target_file, "PNG")
        print(f"Saved iOS icon {w}x{h} -> {target_file}")

# 5. Update iOS LaunchImage icons
ios_launch_dir = os.path.join(base_dir, "oops", "ios", "Runner", "Assets.xcassets", "LaunchImage.imageset")
if os.path.exists(ios_launch_dir):
    launch_files = ["LaunchImage.png", "LaunchImage@2x.png", "LaunchImage@3x.png"]
    for lfile in launch_files:
        target_file = os.path.join(ios_launch_dir, lfile)
        cropped.save(target_file, "PNG")
        print(f"Saved iOS launch image -> {target_file}")

print("All logos and app icons replaced successfully!")
