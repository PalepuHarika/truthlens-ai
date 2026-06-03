with open("static/style.css", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx in range(4549, min(4575, len(lines))):
    cleaned = lines[idx].strip().encode('ascii', 'replace').decode('ascii')
    print(f"{idx+1}: {cleaned}")
