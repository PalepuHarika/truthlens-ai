with open(r"c:\Users\palep\OneDrive\Desktop\Harikaaaa\static\style.css", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "hero-badge" in line:
        start = max(0, idx - 2)
        end = min(len(lines), idx + 8)
        print(f"--- Line {idx+1} ---")
        for i in range(start, end):
            print(f"Line {i+1}: {lines[i]}", end="")
