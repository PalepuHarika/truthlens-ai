with open('static/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    line_num = i + 1
    if any(keyword in line for keyword in ['view-home', 'view-analysis', 'view-dashboard', 'active-view', 'view-chat', 'view-settings', 'view-features', 'view-contact', 'view-login']):
        print(f"Line {line_num}: {line.strip()}")
