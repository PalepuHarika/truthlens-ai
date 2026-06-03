with open("static/style.css", "r", encoding="utf-8") as f:
    content = f.read()

for class_name in ["high-trust", "moderate-risk", "high-risk", "severe-risk"]:
    print(f"=== Matches for {class_name} in style.css ===")
    for line_no, line in enumerate(content.splitlines(), 1):
        if class_name in line:
            print(f"L{line_no}: {line.strip()}")
