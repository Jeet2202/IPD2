from PIL import Image

src_path = r"C:\Users\jeeta\.gemini\antigravity-ide\brain\221c9106-c9b3-4d4c-9635-dcaf43480e67\media__1786049383588.png"
img = Image.open(src_path).convert("RGB")

print("Horizontal scan at y=512:")
for x in range(0, 1024, 32):
    print(f"x={x}: {img.getpixel((x, 512))}")

print("\nVertical scan at x=512:")
for y in range(0, 1024, 32):
    print(f"y={y}: {img.getpixel((512, y))}")
