import re

with open("static/style.css", "r", encoding="utf-8") as f:
    content = f.read()

for m in re.finditer(r'\.feature-card', content):
    line_num = content[:m.start()].count("\n") + 1
    print(f"Found .feature-card at line {line_num}")

for m in re.finditer(r'\.workflow-', content):
    line_num = content[:m.start()].count("\n") + 1
    print(f"Found .workflow- at line {line_num}")
