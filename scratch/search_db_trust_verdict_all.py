import os

matches = []
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith((".html", ".css", ".js", ".py")):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if "db-trust-verdict" in content:
                matches.append(path)

print("Found db-trust-verdict in:", matches)
