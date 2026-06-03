with open("static/style.css", "r", encoding="utf-8") as f:
    style_css = f.read()

with open("static/dashboard.html", "r", encoding="utf-8") as f:
    dash_html = f.read()

print("--- style.css classes matching risk/badge/verdict/trust ---")
for line in style_css.splitlines():
    if "verdict" in line or "risk" in line or "badge" in line:
        if any(w in line for w in ["trust", "moderate", "high", "severe", "danger", "warning"]):
            print(line.strip())

print("\n--- dashboard.html CSS styles ---")
inside_style = False
for line in dash_html.splitlines():
    if "<style>" in line:
        inside_style = True
    elif "</style>" in line:
        inside_style = False
    if inside_style:
        if any(w in line for w in ["verdict", "risk-level", "badge-verdict"]):
            print(line.strip())
