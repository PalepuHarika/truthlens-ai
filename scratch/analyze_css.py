import sys

def analyze_css(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    line_num = 1
    col_num = 1
    in_comment = False
    brace_stack = []
    
    i = 0
    n = len(content)
    while i < n:
        char = content[i]
        
        # Track line and column numbers
        if char == '\n':
            line_num += 1
            col_num = 1
        else:
            col_num += 1
            
        # Handle comments
        if not in_comment:
            if i + 1 < n and content[i] == '/' and content[i+1] == '*':
                in_comment = True
                i += 2
                col_num += 1
                continue
        else:
            if i + 1 < n and content[i] == '*' and content[i+1] == '/':
                in_comment = False
                i += 2
                col_num += 1
                continue
            i += 1
            continue
            
        # Handle string literals (optional but good for robustness)
        if char in ('\"', '\''):
            quote = char
            start_line, start_col = line_num, col_num - 1
            i += 1
            col_num += 1
            while i < n and content[i] != quote:
                if content[i] == '\\':
                    i += 2
                    col_num += 2
                elif content[i] == '\n':
                    line_num += 1
                    col_num = 1
                    i += 1
                else:
                    i += 1
                    col_num += 1
            if i >= n:
                print(f"Warning: Unclosed string starting at line {start_line}, col {start_col}")
            i += 1
            col_num += 1
            continue
            
        # Track braces
        if char == '{':
            brace_stack.append((line_num, col_num - 1))
        elif char == '}':
            if not brace_stack:
                print(f"ERROR: Extra closing brace at line {line_num}, col {col_num - 1}")
            else:
                brace_stack.pop()
                
        i += 1
        
    if brace_stack:
        print(f"ERROR: Unclosed open braces remaining:")
        for bline, bcol in brace_stack:
            print(f"  Open brace at line {bline}, col {bcol}")
    else:
        print("Success: Braces are perfectly balanced structurally!")

if __name__ == '__main__':
    analyze_css('static/style.css')
