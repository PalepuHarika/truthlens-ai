with open('static/style.css', 'r', encoding='utf-8') as f:
    lines = f.readlines()

queries = ['.navbar', '.feat-hero', '.view', 'content-container', 'padding-top']

for q in queries:
    print(f"=== Matches for '{q}' ===")
    for idx, line in enumerate(lines):
        if q in line:
            # Print index (1-based) and surrounding lines if possible or just the line
            start = max(0, idx - 2)
            end = min(len(lines), idx + 5)
            print(f"Line {idx+1}:")
            for i in range(start, end):
                marker = "->" if i == idx else "  "
                print(f"{marker} {i+1}: {lines[i].rstrip()}")
            print("-" * 40)
