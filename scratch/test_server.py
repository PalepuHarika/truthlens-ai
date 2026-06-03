import urllib.request
import urllib.error

urls = [
    "http://127.0.0.1:8000/",
    "http://127.0.0.1:8000/style.css",
    "http://127.0.0.1:8000/app.js",
    "http://127.0.0.1:8000/truthlens_hero_mockup.png",
    "http://127.0.0.1:8000/brain.png"
]

for url in urls:
    try:
        response = urllib.request.urlopen(url)
        print(f"URL: {url:<50} Status: {response.status}")
    except urllib.error.HTTPError as e:
        print(f"URL: {url:<50} Status: ERROR ({e.code})")
    except Exception as e:
        print(f"URL: {url:<50} Status: FAILED ({str(e)})")
