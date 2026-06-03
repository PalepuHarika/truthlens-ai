import os
import re

for file in os.listdir("static"):
    if file.endswith(".html"):
        path = os.path.join("static", file)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        matches = [line.strip() for line in content.splitlines() if "verdict" in line.lower() or "trust" in line.lower()]
        if matches:
            print(f"=== {path} ===")
            for m in matches[:10]:
                print("  ", m[:100])
