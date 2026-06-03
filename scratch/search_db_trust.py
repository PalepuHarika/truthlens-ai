import os

for file in os.listdir("static"):
    if file.endswith(".html"):
        path = os.path.join("static", file)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if "db-trust-verdict" in content or "db-trust-fill" in content:
            print(f"Found in {path}")
