import os
import re

static_dir = "static"
files = [f for f in os.listdir(static_dir) if f.endswith(".html")]

for fname in sorted(files):
    path = os.path.join(static_dir, fname)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # search for the nav-links block
    match = re.search(r'(<div class="nav-links">.*?</div>)', content, re.DOTALL)
    if match:
        print(f"=== {fname} ===")
        print(match.group(1))
        print("=" * 20)
    else:
        print(f"=== {fname} === NO NAV-LINKS FOUND")
