with open("static/app.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("=== LINES 80-120 ===")
for idx in range(79, min(120, len(lines))):
    print(f"{idx+1}: {lines[idx].strip()}")
