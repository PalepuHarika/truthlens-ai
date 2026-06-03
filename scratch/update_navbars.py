import os
import re

static_dir = "static"
files = [f for f in os.listdir(static_dir) if f.endswith(".html")]

# Define active mapping
active_mapping = {
    "index.html": "home",
    "dashboard.html": "dashboard",
    "chat.html": "chat",
    "analysis.html": "analysis",
    "features.html": "features",
    "features_crosscheck.html": "features",
    "features_grounding.html": "features",
    "features_heatmap.html": "features",
    "features_nli.html": "features",
    "contact.html": "contact",
    "settings.html": "settings",
    "login.html": "login",
    "about.html": "none"  # about is not in the default navbar
}

# The standard new navbar links list template
def get_new_nav(active_view):
    nav_links = [
        ('home', '/', 'Home'),
        ('dashboard', '/dashboard', 'Dashboard'),
        ('chat', '/chat', 'Chat'),
        ('analysis', '/analysis', 'Analysis'),
        ('features', '/features', 'Features'),
        ('contact', '/contact', 'Contact'),
        ('settings', '/settings', 'Settings'),
        ('login', '/login', 'Login')
    ]
    
    lines = []
    lines.append('        <div class="nav-links">')
    for view, path, label in nav_links:
        is_active = (view == active_view)
        cls = "nav-link active" if is_active else "nav-link"
        extra = ' id="nav-login-btn"' if view == 'login' else ''
        lines.append(f'            <a href="{path}" class="{cls}" data-view="{view}"{extra}>{label}</a>')
    lines.append('        </div>')
    return '\n'.join(lines)

old_nav_pattern = r'(\s*)<div class="nav-links">.*?</div>'

for fname in sorted(files):
    if fname in ["index.html", "analysis.html", "features.html"]:
        # Let's check them anyway, but they might already be in correct format.
        # We can re-apply the correct format to keep them perfectly in sync.
        pass
        
    path = os.path.join(static_dir, fname)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    active_view = active_mapping.get(fname, "none")
    new_nav = get_new_nav(active_view)
    
    # Let's find the existing nav-links div
    # To handle line endings properly, let's normalize CRLF to LF in content temporarily or work with regex
    # We can match <div class="nav-links">...</div> using re.DOTALL and replace it.
    match = re.search(r'(<div class="nav-links">.*?</div>)', content, re.DOTALL)
    if match:
        old_nav_str = match.group(1)
        # Check if the block needs updating or is already updated.
        # We'll replace it with the new navbar structure matching current page's active tab.
        # Preserve indentation
        lines_before = content[:match.start()].split('\n')
        indent = ""
        if lines_before:
            last_line = lines_before[-1]
            indent = last_line[:len(last_line) - len(last_line.lstrip())]
            
        # Re-build new_nav with correct indentation
        new_nav_lines = []
        for line in new_nav.split('\n'):
            # The get_new_nav helper already has some spacing, let's adjust it
            stripped = line.strip()
            if "nav-links" in stripped:
                new_nav_lines.append(indent + stripped)
            else:
                new_nav_lines.append(indent + "    " + stripped)
        
        indented_new_nav = '\n'.join(new_nav_lines)
        
        # Match line endings of original content
        if '\r\n' in content:
            indented_new_nav = indented_new_nav.replace('\n', '\r\n')
            
        new_content = content[:match.start()] + indented_new_nav + content[match.end():]
        
        with open(path, "w", encoding="utf-8") as f_out:
            f_out.write(new_content)
        print(f"Updated navbar in {fname} (active={active_view})")
    else:
        print(f"Could not find navbar in {fname}")
