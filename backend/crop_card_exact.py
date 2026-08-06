from PIL import Image

src_path = r"C:\Users\jeeta\.gemini\antigravity-ide\brain\221c9106-c9b3-4d4c-9635-dcaf43480e67\media__1786049383588.png"
dest_path = r"c:\Users\jeeta\Documents\IPD2\oops\assets\images\logos\ally_logo.png"
app_logo_path = r"c:\Users\jeeta\Documents\IPD2\oops\assets\images\logos\app_logo.png"

img = Image.open(src_path).convert("RGB")
width, height = img.size

# Scan from left along y=512 for the blue shadow peak
left_edge = 175
right_edge = 848
top_edge = 140
bottom_edge = 908

# Fine tune left edge (blue shadow peak where B > R+10 and R < 240)
for x in range(120, 200):
    r, g, b = img.getpixel((x, 512))
    if b > r + 15 and r < 240:
        left_edge = x
        break

# Fine tune right edge
for x in range(900, 800, -1):
    r, g, b = img.getpixel((x, 512))
    if b > r + 15 and r < 240:
        right_edge = x
        break

# Fine tune top edge (at x=512)
for y in range(100, 180):
    r, g, b = img.getpixel((512, y))
    if b > r + 15 and r < 240:
        top_edge = y
        break

# Fine tune bottom edge (at x=512)
for y in range(960, 860, -1):
    r, g, b = img.getpixel((512, y))
    if b > r + 15 and r < 240:
        bottom_edge = y
        break

print(f"Detected card box: left={left_edge}, top={top_edge}, right={right_edge}, bottom={bottom_edge}")

# Crop inside the shadow box to get ONLY the clean white card!
# Shift 4-6 pixels inward to exclude shadow entirely
card_left = left_edge + 8
card_top = top_edge + 8
card_right = right_edge - 8
card_bottom = bottom_edge - 8

print(f"Clean white card box: ({card_left}, {card_top}, {card_right}, {card_bottom})")

orig = Image.open(src_path)
cropped = orig.crop((card_left, card_top, card_right, card_bottom))
cropped.save(dest_path, "PNG")
cropped.save(app_logo_path, "PNG")

print(f"Cropped card size: {cropped.size[0]}x{cropped.size[1]}")
