import re

with open('static/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern 1: document.getElementById('...').property (direct access)
direct_pattern = re.compile(r'document\.getElementById\([\'"][a-zA-Z0-9_-]+[\'"]\)\.(value|textContent|innerHTML|checked|required|style|classList)')

# Pattern 2: document.getElementById('...')?.property (optional chaining, which is safe)
# Pattern 3: assignment of getElementById to a variable and subsequent property access
# Let's find all lines containing getElementById or querySelector and print the lines so we can audit them.
lines = content.split('\n')
for idx, line in enumerate(lines):
    line_num = idx + 1
    # Check for direct access on getElementById or querySelector (without optional chaining)
    if 'document.getElementById(' in line or 'document.querySelector(' in line:
        if '.' in line.split('document.getElementById(')[-1] or '.' in line.split('document.querySelector(')[-1]:
            # if it has ?. or is just addEventListener or checking existence, skip it
            if '?.' not in line and 'addEventListener' not in line:
                print(f"Line {line_num}: {line.strip()}")
