import os
import re

static_dir = "static"
count = 0
for filename in os.listdir(static_dir):
    if filename.endswith(".html"):
        path = os.path.join(static_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Replace script tag
        new_content = re.sub(
            r'src=["\']/?static/app\.js(?:\?v=\d+)?["\']',
            'src="/static/app.js?v=11"',
            content
        )
        
        if new_content != content:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Updated {filename}")
            count += 1

print(f"Total updated files: {count}")
