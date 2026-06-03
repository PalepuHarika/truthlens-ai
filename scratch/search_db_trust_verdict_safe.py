import os

exclude_dirs = [".git", "venv", "__pycache__", "scratch", ".gemini"]
matches = []

for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    for file in files:
        if file.endswith((".html", ".css", ".js", ".py")):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                if "db-trust-verdict" in content:
                    matches.append(path)
            except Exception as e:
                pass

print("Found db-trust-verdict in:", matches)
