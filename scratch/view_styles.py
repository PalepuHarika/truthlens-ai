with open("static/style.css", "r", encoding="utf-8") as f:
    content = f.read()

import re

def extract_rule(css, selector):
    # simple extraction of rules matching selector
    matches = re.finditer(re.escape(selector) + r'\s*\{([^}]+)\}', css)
    results = []
    for m in matches:
        results.append(m.group(0))
    return results

selectors = [".hero-section", ".hero", ".feature-row", ".stats-grid", ".stats", ".workflow-flow-vertical", ".navbar"]
for s in selectors:
    print(f"=== Rules for {s} ===")
    rules = extract_rule(content, s)
    for r in rules:
        print(r)
        print("-" * 20)
