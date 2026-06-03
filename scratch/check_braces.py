def check_braces(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    line_num = 1
    char_num = 1
    stack = []
    
    for idx, char in enumerate(content):
        if char == '\n':
            line_num += 1
            char_num = 1
        else:
            char_num += 1
            
        if char == '{':
            stack.append((line_num, char_num, idx))
        elif char == '}':
            if not stack:
                print(f"Unmatched closing brace at line {line_num}, col {char_num}")
            else:
                stack.pop()
                
    if stack:
        print(f"Total unclosed opening braces: {len(stack)}")
        for line, col, idx in stack[:10]:
            context = content[idx:idx+40].replace('\n', ' ')
            print(f"  Unclosed brace starting at line {line}, col {col}: '{context}...'")

check_braces("static/style.css")
