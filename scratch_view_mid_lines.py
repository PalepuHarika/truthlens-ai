with open(r"c:\Users\palep\OneDrive\Desktop\Harikaaaa\static\style.css", "r", encoding="utf-8") as f:
    lines = f.readlines()

start = 2700
end = 2752
for idx in range(max(0, start-1), min(len(lines), end)):
    print(f"Line {idx+1}: {lines[idx]}", end="")
