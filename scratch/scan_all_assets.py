with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

import re
matches_html = re.findall(r'["\'][^"\']*static/[^"\']*["\']', html)
print("=== HTML static matches ===")
for m in matches_html:
    print(m)

with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

matches_js = re.findall(r'["\'][^"\']*static/[^"\']*["\']', js)
print("=== JS static matches ===")
for m in matches_js:
    print(m)
