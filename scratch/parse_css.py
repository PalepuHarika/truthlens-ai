import re

def parse_css_hierarchy(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove comments to simplify parsing
    content_clean = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # We will track braces
    stack = []
    current_selector = []
    line_num = 1
    
    lines = content.split('\n')
    
    # Simple tokenization by {, } and text
    tokens = re.split(r'([{}])', content_clean)
    
    pos = 0
    for token in tokens:
        if token == '{':
            # find selector before {
            # Let's get the text before this token
            selector = tokens[pos-1].strip()
            # clean up selector (e.g. remove property values if any)
            selector_clean = selector.split(';')[-1].strip().split('\n')[-1].strip()
            stack.append(selector_clean)
        elif token == '}':
            if stack:
                closed = stack.pop()
                if len(stack) > 0:
                    # Nested CSS rule!
                    print(f"NESTED RULE DETECTED: '{closed}' is nested inside '{stack[-1]}'")
            else:
                print("Extra closing brace found!")
        pos += 1

parse_css_hierarchy("static/style.css")
