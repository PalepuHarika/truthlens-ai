import os
import re

for file in ["static/dashboard.html", "static/analysis.html", "static/index.html"]:
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"=== {file} ===")
        for line in content.splitlines():
            if "badge-verdict" in line or "id=" in line and ("verdict" in line or "risk" in line):
                print(line.strip())
