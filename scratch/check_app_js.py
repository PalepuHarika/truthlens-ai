import re

with open("static/app.js", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.splitlines()

# Search pattern for document.getElementById / document.querySelector / etc.
pattern = r"document\.(getElementById|querySelector)\(['\"][a-zA-Z0-9_\#\.\s\[\]=-]+['\"]\)\s*\.[a-zA-Z]"

print("Searching for direct unchecked DOM queries:")
matches = []
for idx, line in enumerate(lines):
    match = re.search(pattern, line)
    if match:
        # Check if it's guarded by an if statement on the same line (crude check)
        if "if (" in line and "document." in line.split("if (")[1].split(")")[0]:
            continue
        matches.append((idx + 1, line.strip()))

if matches:
    print(f"Found {len(matches)} potential unsafe accesses:")
    for num, line in matches:
        print(f"Line {num}: {line}")
else:
    print("No unsafe direct accesses found.")
