def main():
    try:
        with open(r"c:\Users\palep\OneDrive\Desktop\Harikaaaa\static\style.css", "r", encoding="utf-8") as f:
            css = f.read()
    except Exception as e:
        print(f"Error: {e}")
        return

    import re
    rules = re.findall(r'([^{]+)\s*\{([^}]+)\}', css)
    
    # We want navbar styles
    for selector, content in rules[:300]: # Look at first 300 rules
        selector = selector.strip()
        if '.navbar' in selector or 'nav' in selector:
            print(f"{selector} {{\n{content.strip()}\n}}\n")

if __name__ == '__main__':
    main()
