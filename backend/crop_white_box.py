from PIL import Image

src_path = r"C:\Users\jeeta\.gemini\antigravity-ide\brain\221c9106-c9b3-4d4c-9635-dcaf43480e67\media__1786049383588.png"
dest_path = r"c:\Users\jeeta\Documents\IPD2\oops\assets\images\logos\ally_logo.png"
app_logo_path = r"c:\Users\jeeta\Documents\IPD2\oops\assets\images\logos\app_logo.png"

img = Image.open(src_path).convert("RGB")
width, height = img.size
print(f"Image size: {width}x{height}")

# Inspect horizontal and vertical profile of pixels along center line
# The main white box is bright white (R>250, G>250, B>250)
# Outside the card is light grey/shadow (R<250 or G<250 or B<250)

# Let's inspect along center row (y = height // 2)
y_mid = height // 2
x_white_starts = None
x_white_ends = None

for x in range(width):
    r, g, b = img.getpixel((x, y_mid))
    if r > 248 and g > 248 and b > 248:
        if x_white_starts is None:
            x_white_starts = x
        x_white_ends = x

# Let's inspect along center column (x = width // 2)
x_mid = width // 2
y_white_starts = None
y_white_ends = None

for y in range(height):
    r, g, b = img.getpixel((x_mid, y))
    if r > 248 and g > 248 and b > 248:
        if y_white_starts is None:
            y_white_starts = y
        y_white_ends = y

print(f"White card X range: {x_white_starts} to {x_white_ends}")
print(f"White card Y range: {y_white_starts} to {y_white_ends}")

# The card has rounded corners, so the bounding box of the card is:
card_left = x_white_starts
card_top = y_white_starts
card_right = x_white_ends
card_bottom = y_white_ends

# Crop exact card
orig = Image.open(src_path)
cropped = orig.crop((card_left, card_top, card_right, card_bottom))
cropped.save(dest_path, "PNG")
cropped.save(app_logo_path, "PNG")

print(f"Cropped card size: {cropped.size}")
