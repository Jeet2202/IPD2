import os
from PIL import Image

src_path = r"C:\Users\jeeta\.gemini\antigravity-ide\brain\221c9106-c9b3-4d4c-9635-dcaf43480e67\media__1786049383588.png"
dest_path = r"c:\Users\jeeta\Documents\IPD2\oops\assets\images\logos\ally_logo.png"
app_logo_path = r"c:\Users\jeeta\Documents\IPD2\oops\assets\images\logos\app_logo.png"

img = Image.open(src_path).convert("RGB")
width, height = img.size

# Find bounding box of non-white pixels
left = width
top = height
right = 0
bottom = 0

pixels = img.load()
for y in range(height):
    for x in range(width):
        r, g, b = pixels[x, y]
        # if not white background (below 240)
        if r < 240 or g < 240 or b < 240:
            if x < left: left = x
            if x > right: right = x
            if y < top: top = y
            if y > bottom: bottom = y

padding = 10
left = max(0, left - padding)
top = max(0, top - padding)
right = min(width, right + padding)
bottom = min(height, bottom + padding)

print(f"Detected content box: ({left}, {top}, {right}, {bottom})")

orig = Image.open(src_path)
cropped = orig.crop((left, top, right, bottom))
cropped.save(dest_path, "PNG")
cropped.save(app_logo_path, "PNG")

print(f"Successfully saved cropped logo ({cropped.size[0]}x{cropped.size[1]}) to {dest_path}")
