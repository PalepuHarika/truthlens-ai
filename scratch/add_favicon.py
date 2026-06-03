import os

static_dir = 'static'
tag = '    <link rel="icon" type="image/png" href="/static/favicon.png">\n'

for f in os.listdir(static_dir):
    if f.endswith('.html'):
        path = os.path.join(static_dir, f)
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if 'favicon.png' not in content:
            if '</head>' in content:
                new_content = content.replace('</head>', tag + '</head>')
            elif '</HEAD>' in content:
                new_content = content.replace('</HEAD>', tag + '</HEAD>')
            else:
                print(f"Warning: head tag not found in {f}")
                continue
            
            with open(path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            print(f"Added favicon to {f}")
