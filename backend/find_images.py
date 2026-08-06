import os
import glob

search_dirs = [
    r"C:\Users\jeeta\.gemini\antigravity-ide",
    r"C:\Users\jeeta\AppData\Local\Temp",
]

found = []
for d in search_dirs:
    for ext in ["*.png", "*.jpg", "*.jpeg", "*.webp"]:
        for f in glob.glob(os.path.join(d, "**", ext), recursive=True):
            try:
                mtime = os.path.getmtime(f)
                found.append((mtime, f))
            except Exception:
                pass

found.sort(reverse=True)
print("Most recent images:")
for mtime, f in found[:10]:
    print(f"{f}")
