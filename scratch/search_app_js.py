with open("static/app.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

search_terms = ["verdict", "risk", "trust"]
for i, line in enumerate(lines, 1):
    for term in search_terms:
        if term in line.lower():
            print(f"L{i}: {line.strip()[:140]}")
            break
