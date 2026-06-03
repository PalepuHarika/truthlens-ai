with open("static/app.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("=== LINES 60-80 ===")
for idx in range(59, min(80, len(lines))):
    print(f"{idx+1}: {lines[idx].strip()}")

print("\n=== LINES 140-165 ===")
for idx in range(139, min(165, len(lines))):
    print(f"{idx+1}: {lines[idx].strip()}")
