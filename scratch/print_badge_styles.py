def print_styles(filename):
    print(f"=== {filename} ===")
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    start = -1
    for i, line in enumerate(lines):
        if ".badge-verdict {" in line:
            start = i
            break
    if start != -1:
        for line in lines[start:start+25]:
            print(line.rstrip())

print_styles("static/analysis.html")
print_styles("static/dashboard.html")
