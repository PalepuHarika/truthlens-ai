def main():
    try:
        with open(r"c:\Users\palep\OneDrive\Desktop\Harikaaaa\static\style.css", "r", encoding="utf-8") as f:
            css = f.read()
    except Exception as e:
        print(f"Error: {e}")
        return

    import re
    rules = re.findall(r'([^{]+)\s*\{([^}]+)\}', css)
    
    # We want content-container styles
    for selector, content in rules[:300]:
        selector = selector.strip()
        if 'content-container' in selector or 'container' in selector:
            print(f"{selector} {{\n{content.strip()}\n}}\n")

if __name__ == '__main__':
    main()
