import urllib.request
import urllib.error

routes_to_test = [
    ("/", "home"),
    ("/dashboard", "dashboard"),
    ("/chat", "chat"),
    ("/features", "features"),
    ("/features/nli", "features"),
    ("/settings", "settings"),
    ("/login", "login")
]

all_passed = True
for route, expected_active in routes_to_test:
    url = f"http://127.0.0.1:8000{route}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode('utf-8')
            print(f"Route {route} -> Status: {response.status}")
            
            # Check for expected active link
            # In the navbar, the active class should be applied to the correct view.
            # e.g., for dashboard: class="nav-link active" data-view="dashboard"
            if expected_active != "none":
                search_str = f'data-view="{expected_active}"'
                active_str = f'class="nav-link active" data-view="{expected_active}"'
                
                if search_str in html:
                    if active_str in html:
                        print(f"  [OK] Highlighted tab correctly: '{expected_active}'")
                    else:
                        print(f"  [ERROR] Tab '{expected_active}' exists but is NOT active.")
                        all_passed = False
                else:
                    print(f"  [WARNING] Tab '{expected_active}' not found in page HTML.")
            else:
                print("  [OK] No active tab expected")
    except urllib.error.HTTPError as e:
        print(f"Route {route} -> HTTP Error: {e.code} {e.reason}")
        all_passed = False
    except Exception as e:
        print(f"Route {route} -> Failed: {e}")
        all_passed = False

if all_passed:
    print("\nAll endpoints checked successfully. Multi-page routing is working flawlessly!")
else:
    print("\nSome checks failed.")
