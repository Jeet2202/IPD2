import os
import glob
import shutil

brain_dir = r"C:\Users\jeeta\.gemini\antigravity-ide\brain\221c9106-c9b3-4d4c-9635-dcaf43480e67"
found = []
for ext in ["*.png", "*.jpg", "*.jpeg", "*.webp"]:
    for f in glob.glob(os.path.join(brain_dir, ext)):
        mtime = os.path.getmtime(f)
        found.append((mtime, f))

found.sort(reverse=True)
print("Latest images found:")
for mtime, f in found[:5]:
    print(f"{f}")

if found:
    latest_img = found[0][1]
    dest_dir = r"c:\Users\jeeta\Documents\IPD2\oops\assets\images\logos"
    os.makedirs(dest_dir, exist_ok=True)
    dest_ally = os.path.join(dest_dir, "ally_logo.png")
    dest_app = os.path.join(dest_dir, "app_logo.png")
    
    shutil.copy(latest_img, dest_ally)
    shutil.copy(latest_img, dest_app)
    print(f"Copied {latest_img} -> {dest_ally} and {dest_app}")
