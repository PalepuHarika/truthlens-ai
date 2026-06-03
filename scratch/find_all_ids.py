import os
import re

id_pattern = re.compile(r'id=["\']([^"\']+)["\']')

def find_ids(path):
    print(f"=== IDs in {path} ===")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    ids = id_pattern.findall(content)
    for i in sorted(set(ids)):
        print("  ", i)

find_ids("static/analysis.html")
find_ids("static/dashboard.html")
