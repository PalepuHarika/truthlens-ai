import re

with open("static/style.css", "r", encoding="utf-8") as f:
    content = f.read()

for m in re.finditer(r'\.navbar', content):
    line_num = content[:m.start()].count("\n") + 1
    print(f"Found .navbar at line {line_num}")
