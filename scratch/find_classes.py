import re

with open("static/style.css", "r", encoding="utf-8") as f:
    content = f.read()

# Let's search for some of the classes we found in app.js
important_classes = [
    r'\.ht-claim', r'\.ht-verified', r'\.ht-contradicted',
    r'\.hl-dot', r'\.claims-list', r'\.heatmap-text',
    r'\.comparison-grid', r'\.comp-col', r'\.corrected',
    r'\.chat-shell', r'\.chat-main', r'\.chat-messages',
    r'\.chat-input-bar', r'\.settings-card', r'\.panel-card',
    r'\.llm-comparison-grid', r'\.disagreement-list',
    r'\.evidence-list', r'\.analytics-stats', r'\.activity-log'
]

for cls in important_classes:
    matches = list(re.finditer(cls, content))
    if matches:
        print(f"Found class {cls}: {len(matches)} times")
        # Print the first line number it appears
        line_num = content[:matches[0].start()].count("\n") + 1
        print(f"  First appearance at line {line_num}")
