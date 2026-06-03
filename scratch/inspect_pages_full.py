from bs4 import BeautifulSoup

def inspect_html(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    
    # Let's extract titles, headers, form IDs, input IDs, buttons
    print(f"=== File: {filepath} ===")
    
    # Title in head
    print(f"Page Title: {soup.title.string if soup.title else 'None'}")
    
    # h1, h2, h3
    headers = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])]
    print("Headers:", headers[:15])
    
    # Forms
    forms = [f.get('id') for f in soup.find_all('form')]
    print("Forms:", forms)
    
    # Major buttons
    buttons = [b.get('id') or b.get_text(strip=True) for b in soup.find_all('button')]
    print("Buttons:", buttons[:15])
    
    # Search for specific view elements
    active_view = soup.find(class_=re.compile(r'view'))
    if active_view:
        print(f"Main View ID: {active_view.get('id')}")
        
    print("\n" + "="*40 + "\n")

import re
inspect_html("static/dashboard.html")
inspect_html("static/analysis.html")
