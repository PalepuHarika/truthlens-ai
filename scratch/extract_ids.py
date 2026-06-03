import re

with open("static/app.js", "r", encoding="utf-8") as f:
    content = f.read()

# Find all getElementById calls
id_matches = re.findall(r'getElementById\([\'"]([a-zA-Z0-9_-]+)[\'"]\)', content)
# Find all querySelector/querySelectorAll calls with ID or class selectors
qs_matches = re.findall(r'querySelector(?:All)?\([\'"]([.#][a-zA-Z0-9_-]+)[\'"]\)', content)

# Print unique matches
print("=== getElementById Matches ===")
for m in sorted(list(set(id_matches))):
    print(m)

print("\n=== querySelector Matches ===")
for m in sorted(list(set(qs_matches))):
    print(m)
