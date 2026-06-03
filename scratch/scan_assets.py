import re

with open("static/index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Find href, src, or other url-like attributes
links = re.findall(r'(href|src)=["\']([^"\']+)["\']', content)
for attr, val in links:
    if "static" in val or "style.css" in val or "app.js" in val or "png" in val:
        print(f"Attribute: {attr:<6} Value: {val}")
