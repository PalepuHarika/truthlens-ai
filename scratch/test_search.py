import urllib.request
import urllib.parse
import re
import html

def ddg_search(query, max_results=10):
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            content = response.read().decode('utf-8')
            
        # Extract snippets using regex
        # The snippets are typically in tags like:
        # <a class="result__snippet" href="...">Snippet text here</a>
        # Or <td class="result-snippet">Snippet text</td> depending on the exact page.
        # Let's find result__snippet
        snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', content, re.DOTALL)
        
        # Also let's extract titles and urls to map them to sources
        titles = re.findall(r'<a class="result__url"[^>]*>(.*?)</a>', content, re.DOTALL)
        # Often the title is in result__snippet or result__title
        titles_alt = re.findall(r'<a class="result__a"[^>]*>(.*?)</a>', content, re.DOTALL)
        
        results = []
        for i in range(min(max_results, len(snippets))):
            snippet_text = re.sub(r'<[^>]+>', '', snippets[i]) # remove HTML tags
            snippet_text = html.unescape(snippet_text).strip()
            
            title_text = ""
            if i < len(titles_alt):
                title_text = re.sub(r'<[^>]+>', '', titles_alt[i])
                title_text = html.unescape(title_text).strip()
            else:
                title_text = "Web Search Result"
                
            results.append({
                "title": title_text,
                "body": snippet_text,
                "snippet": snippet_text
            })
        return results
    except Exception as e:
        print(f"Error in direct ddg search: {e}")
        return []

if __name__ == "__main__":
    url = f"https://html.duckduckgo.com/html/?q=Narendra+Modi"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    with urllib.request.urlopen(req, timeout=8) as response:
        content = response.read().decode('utf-8')
    
    titles = re.findall(r'<h2 class="result__title"[^>]*>.*?<a[^>]*>(.*?)</a>', content, re.DOTALL)
    print("Found titles with h2 regex:", len(titles))
    for i, t in enumerate(titles[:5]):
        print(f"Title {i+1}: {re.sub(r'<[^>]+>', '', t).strip()}")
