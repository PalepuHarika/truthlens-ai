import re

with open("static/style.css", "r", encoding="utf-8") as f:
    content = f.read()

# Strip comments first
def strip_comments(text):
    # Match /* ... */
    return re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

clean_content = strip_comments(content)

# Track braces
stack = []
lines = content.splitlines()

# We can scan character by character but keep track of line numbers and character index.
line_no = 1
col_no = 1

# Let's search inside the clean content, but it's easier to scan the original file, handling comments and strings properly.
in_comment = False
in_string = False
string_char = None

for i, char in enumerate(content):
    if char == '\n':
        line_no += 1
        col_no = 1
        continue
    
    # Handle comments
    if not in_string and not in_comment:
        if content[i:i+2] == '/*':
            in_comment = True
            continue
    if in_comment:
        if content[i-1:i+1] == '*/':
            in_comment = False
        col_no += 1
        continue

    # Handle strings
    if not in_comment:
        if char in ('"', "'"):
            if not in_string:
                in_string = True
                string_char = char
            elif string_char == char:
                in_string = False
                string_char = None
            col_no += 1
            continue
    if in_string:
        col_no += 1
        continue

    # Count braces
    if char == '{':
        stack.append((line_no, col_no, i))
    elif char == '}':
        if len(stack) == 0:
            print(f"Extra closing brace '}}' at line {line_no}, col {col_no}")
        else:
            stack.pop()
    
    col_no += 1

while len(stack) > 0:
    line, col, pos = stack.pop()
    print(f"Unmatched opening brace '{{' at line {line}, col {col}")
