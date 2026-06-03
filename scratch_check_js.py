import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r"c:\Users\palep\OneDrive\Desktop\Harikaaaa\static\app.js", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

def print_context(line_num, radius=10):
    start = max(0, line_num - radius)
    end = min(len(lines), line_num + radius)
    print(f"--- Context for Line {line_num} ---")
    for i in range(start, end):
        print(f"{i+1}: {lines[i].strip()}")
    print()

# Print context for key lines
print_context(442, radius=5)
print_context(823, radius=15)
print_context(1999, radius=10)
print_context(2061, radius=10)
print_context(2086, radius=10)
