import re

def get_view_content(filepath, view_id):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    # Search for the view container
    pattern = rf'(<div id="{view_id}"[^>]*>.*?</div>\s*<!-- ═════)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1)
    # fallback to just finding <div id="view_id" ...> to the end
    match_fallback = re.search(rf'(<div id="{view_id}"[^>]*>.*)', content, re.DOTALL)
    if match_fallback:
        # truncate for display
        return match_fallback.group(1)[:2000]
    return "Not found"

dash_content = get_view_content("static/dashboard.html", "view-dashboard")
analysis_content = get_view_content("static/analysis.html", "view-analysis")

print("=== DASHBOARD VIEW STRUCTURE (FIRST 500 CHARS) ===")
print(dash_content[:500])
print("\n" + "="*40 + "\n")
print("=== ANALYSIS VIEW STRUCTURE (FIRST 500 CHARS) ===")
print(analysis_content[:500])
