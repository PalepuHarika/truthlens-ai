import urllib.request
import urllib.error

url = "http://127.0.0.1:8000/"
try:
    print(f"Sending GET request to {url}...")
    with urllib.request.urlopen(url, timeout=5) as response:
        html = response.read()
        print(f"Status Code: {response.status}")
        print(f"Content Length: {len(html)} bytes")
        print("First 200 chars of response:")
        print(html[:200].decode('utf-8'))
        print("Server check passed!")
except urllib.error.URLError as e:
    print(f"Server check failed: {e}")
except Exception as e:
    print(f"Error checking server: {e}")
