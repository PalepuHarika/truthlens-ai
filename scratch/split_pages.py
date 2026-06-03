import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Load index.html
index_path = os.path.join(STATIC_DIR, "index.html")
with open(index_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Define boundaries
# The header goes from start to the first view
# We can look for the first view marker: "<!-- ═══════════ HOME VIEW ═══════════ -->"
header_end_idx = html_content.find("<!-- ═══════════ HOME VIEW ═══════════ -->")
if header_end_idx == -1:
    header_end_idx = html_content.find('<div id="view-home"')

header = html_content[:header_end_idx]

# The footer starts with the tooltip or footer element
footer_start_idx = html_content.find("<!-- Interactive Hover Tooltip -->")
if footer_start_idx == -1:
    footer_start_idx = html_content.find('<div id="truthlens-tooltip"')
if footer_start_idx == -1:
    footer_start_idx = html_content.find('<footer class="main-footer">')

footer = html_content[footer_start_idx:]

# Let's clean the header and footer resource paths (change to absolute paths under /static)
def make_absolute(content):
    content = content.replace('href="style.css?v=10"', 'href="/static/style.css?v=10"')
    content = content.replace('src="app.js"', 'src="/static/app.js"')
    content = content.replace('src="truthlens_hero_mockup.png"', 'src="/static/truthlens_hero_mockup.png"')
    content = content.replace('src="brain.png?v=2"', 'src="/static/brain.png?v=2"')
    content = content.replace('src="brain.png"', 'src="/static/brain.png"')
    content = content.replace('src="awaiting.png"', 'src="/static/awaiting.png"')
    content = content.replace('href="favicon.png"', 'href="/static/favicon.png"')
    return content

header = make_absolute(header)
footer = make_absolute(footer)

# Extract individual views using regex or string splitting
views = {}

# We have these views:
# view-home, view-features, view-dashboard, view-analysis, view-chat, view-about, view-settings, view-login, view-feat-nli, view-feat-grounding, view-feat-crosscheck, view-feat-heatmap, view-resources
view_ids = [
    "view-home", "view-features", "view-dashboard", "view-analysis", "view-chat", "view-settings", "view-login",
    "view-feat-nli", "view-feat-grounding", "view-feat-crosscheck", "view-feat-heatmap", "view-resources", "view-contact"
]

# Wait, view-about has two occurrences. Let's find both.
# Let's extract each view div by finding the <div id="view-X"...> and its closing </div>
# Since they are top-level and don't nest views, we can split them or find matching closing div.
# Let's write a robust parser to find the outer HTML of <div id="view-X">
for vid in view_ids:
    start_tag = f'id="{vid}"'
    start_pos = html_content.find(start_tag)
    if start_pos == -1:
        # try without quotes
        start_tag = f'id={vid}'
        start_pos = html_content.find(start_tag)
    
    if start_pos != -1:
        # Find the starting '<div' before this id
        div_start = html_content.rfind("<div", 0, start_pos)
        
        # Now find the matching closing '</div>'.
        # Since views can contain other nested divs, we count open/close tags.
        count = 1
        pos = div_start + 4
        while count > 0 and pos < len(html_content):
            next_open = html_content.find("<div", pos)
            next_close = html_content.find("</div>", pos)
            
            if next_close == -1:
                break
            
            if next_open != -1 and next_open < next_close:
                count += 1
                pos = next_open + 4
            else:
                count -= 1
                pos = next_close + 6
        
        views[vid] = html_content[div_start:pos]

# Special handling for view-about (extract both and combine them)
about_views = []
pos = 0
while True:
    idx = html_content.find('id="view-about"', pos)
    if idx == -1:
        break
    div_start = html_content.rfind("<div", 0, idx)
    count = 1
    p = div_start + 4
    while count > 0 and p < len(html_content):
        next_open = html_content.find("<div", p)
        next_close = html_content.find("</div>", p)
        if next_close == -1:
            break
        if next_open != -1 and next_open < next_close:
            count += 1
            p = next_open + 4
        else:
            count -= 1
            p = next_close + 6
    about_views.append(html_content[div_start:p])
    pos = p

views["view-about"] = "\n<!-- About Section Combined -->\n".join(about_views)

# Write separate HTML files
page_mapping = {
    "index.html": ("view-home", "/"),
    "dashboard.html": ("view-dashboard", "/dashboard"),
    "chat.html": ("view-chat", "/chat"),
    "analysis.html": ("view-analysis", "/analysis"),
    "features.html": ("view-features", "/features"),
    "contact.html": ("view-contact", "/contact"),
    "settings.html": ("view-settings", "/settings"),
    "login.html": ("view-login", "/login"),
    "about.html": ("view-about", "/about"),
    "features_nli.html": ("view-feat-nli", "/features/nli"),
    "features_grounding.html": ("view-feat-grounding", "/features/grounding"),
    "features_crosscheck.html": ("view-feat-crosscheck", "/features/crosscheck"),
    "features_heatmap.html": ("view-feat-heatmap", "/features/heatmap"),
}

for filename, (view_id, path) in page_mapping.items():
    view_content = views.get(view_id, "")
    if not view_content:
        print(f"Warning: view content for {view_id} not found!")
        continue
    
    # In each file, make sure the view container has 'active-view'
    if 'active-view' not in view_content:
        # Find the opening div of the view and append 'active-view' to class
        view_content = re.sub(
            r'(class=["\'][^"\']*)view([^"\']*["\'])',
            r'\1view active-view\2',
            view_content,
            count=1
        )
    
    # Build active navbar links
    current_header = header
    
    # First, make all links inactive
    current_header = current_header.replace('class="nav-link active"', 'class="nav-link"')
    
    # Then make the current one active
    if path == "/":
        current_header = current_header.replace('href="/" class="nav-link"', 'href="/" class="nav-link active"')
    else:
        current_header = current_header.replace(f'href="{path}" class="nav-link"', f'href="{path}" class="nav-link active"')
    
    # Make all view content asset paths absolute
    view_content = make_absolute(view_content)
    
    full_page = current_header + "\n" + view_content + "\n" + footer
    
    # Write to file
    out_path = os.path.join(STATIC_DIR, filename)
    with open(out_path, "w", encoding="utf-8") as out_f:
        out_f.write(full_page)
    print(f"Wrote {filename} successfully.")
