import os
import re

html_dir = 'static'
view_pattern = re.compile(r'id=["\'](view-[a-zA-Z0-9_-]+)["\']')

for filename in os.listdir(html_dir):
    if filename.endswith('.html'):
        filepath = os.path.join(html_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        matches = view_pattern.findall(content)
        if matches:
            print(f"{filename}: {matches}")
