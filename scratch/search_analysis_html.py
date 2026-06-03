with open("static/analysis.html", "r", encoding="utf-8") as f:
    content = f.read()

for line_no, line in enumerate(content.splitlines(), 1):
    if any(k in line.lower() for k in ["overall-risk", "risk-sub", "trust-verdict", "risk-display"]):
        print(f"L{line_no}: {line.strip()}")
