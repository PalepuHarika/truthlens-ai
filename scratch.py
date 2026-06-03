try:
    from duckduckgo_search import DDGS
    print("duckduckgo_search imported successfully")
except ImportError:
    print("duckduckgo_search import failed")
    try:
        from ddgs import DDGS
        print("ddgs imported successfully")
    except ImportError:
        print("ddgs import failed")

import sys
print("Python version:", sys.version)

try:
    with DDGS() as ddgs:
        print("DDGS initialized")
        res = list(ddgs.text("IPL 2026 winner", max_results=5))
        print("Results len:", len(res))
        for r in res:
            print(r)
except Exception as e:
    print("Error during DDGS search:", e)
