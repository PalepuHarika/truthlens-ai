with open("static/style.css", "r", encoding="utf-8") as f:
    css_content = f.read()

for line in css_content.splitlines():
    if "badge" in line or "verdict" in line or "risk" in line:
        if any(cls in line for cls in ["trust", "moderate", "high", "severe"]):
            print(line.strip())
