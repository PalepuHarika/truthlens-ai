with open(r"c:\Users\palep\OneDrive\Desktop\Harikaaaa\static\style.css", "r", encoding="utf-8") as f:
    lines = f.readlines()

targets = [186, 2860, 2912, 3279, 3360, 3480, 3805]
for t in targets:
    start = max(0, t - 4)
    end = min(len(lines), t + 3)
    print(f"--- Line {t} ---")
    for i in range(start, end):
        print(f"Line {i+1}: {lines[i]}", end="")
