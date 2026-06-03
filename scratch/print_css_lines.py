with open('static/style.css', 'r', encoding='utf-8') as f:
    content = f.read()

import re
blocks = re.findall(r'([^\}\{]+)\{([^\}]+)\}', content, re.DOTALL)
for selector, styles in blocks:
    if 'body >' in selector or 'body div' in selector or selector.strip() == 'div':
        out = f"Selector: {selector.strip()}\n"
        for line in styles.strip().split('\n'):
            out += f"  {line.strip()}\n"
        out += "-" * 50
        print(out.encode('cp1252', errors='replace').decode('cp1252'))
