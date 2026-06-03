import os
import re

html_dir = 'static'
prompt_pattern = re.compile(r'id=["\'](db-prompt|prompt)["\']')

for filename in os.listdir(html_dir):
    if filename.endswith('.html'):
        filepath = os.path.join(html_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        matches = prompt_pattern.findall(content)
        if matches:
            print(f"{filename}: {matches}")
