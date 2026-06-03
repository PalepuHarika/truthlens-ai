with open('static/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    line_num = i + 1
    if '.addEventListener' in line:
        print(f"Line {line_num}: {line.strip()}")
