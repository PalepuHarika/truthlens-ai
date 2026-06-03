import os

for root, dirs, files in os.walk("static"):
    for file in files:
        if file.endswith((".html", ".css", ".js")):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if "tmp-verdict" in content:
                print(f"Found in {path}")
                for line in content.splitlines():
                    if "tmp-verdict" in line:
                        print("  ", line.strip())
