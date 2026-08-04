import os
import re

directories_to_scan = ["backend", "ai-service", "oops", "."]
exclude_dirs = {".git", ".venv", "venv", "node_modules", "build", ".dart_tool", ".idea", "__pycache__", "windows", "macos", "linux"}

replacements = {
    "KaamSetu": "Ally",
    "kaamsetu": "ally",
    "KAAMSETU": "ALLY",
}

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        return False
        
    original_content = content
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    if content != original_content:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {filepath}")
            return True
        except Exception as e:
            print(f"Error writing to {filepath}: {e}")
    return False

def scan_and_replace(base_path):
    count = 0
    for root, dirs, files in os.walk(base_path):
        # Modify dirs in-place to skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            # Skip some binary or auto-generated files if they match extensions
            if file.endswith(('.png', '.jpg', '.jpeg', '.gif', '.ico', '.pyc', '.so', '.dll', '.exe', '.pkl', '.bin')):
                continue
                
            filepath = os.path.join(root, file)
            # Skip the script itself
            if os.path.basename(filepath) == "rename.py":
                continue
                
            if replace_in_file(filepath):
                count += 1
    return count

if __name__ == "__main__":
    total_updated = 0
    base_dir = r"c:\Users\jeeta\Documents\IPD2"
    for d in directories_to_scan:
        path = os.path.join(base_dir, d) if d != "." else base_dir
        if d == "." : 
            # only root files
            for file in os.listdir(base_dir):
                filepath = os.path.join(base_dir, file)
                if os.path.isfile(filepath) and file != "rename.py":
                    if replace_in_file(filepath):
                        total_updated += 1
        else:
            if os.path.exists(path):
                total_updated += scan_and_replace(path)
                
    print(f"\nMigration complete. Total files updated: {total_updated}")
