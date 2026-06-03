import os
import sys

search_terms = ["verdict", "risk", "getverdict"]
exclude_dirs = [".git", "venv", "__pycache__", "scratch", ".gemini"]

matches = []
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    for file in files:
        if file.endswith((".py", ".html", ".js", ".css")):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line_no, line in enumerate(f, 1):
                        for term in search_terms:
                            if term in line.lower():
                                matches.append((path, line_no, line.strip()))
                                break
            except Exception as e:
                pass

print(f"Found {len(matches)} matches:")
for path, line_no, content in matches:
    safe_content = content.encode('ascii', errors='replace').decode('ascii')
    print(f"{path}:{line_no}: {safe_content[:120]}")
