with open("static/style.css", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx in range(2775, min(2900, len(lines))):
    cleaned = lines[idx].strip().encode('ascii', 'replace').decode('ascii')
    print(f"{idx+1}: {cleaned}")
