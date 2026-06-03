def search_in_file(path, keywords):
    print(f"=== File: {path} ===")
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for idx, line in enumerate(f):
            if any(k in line for k in keywords):
                print(f"{idx+1}: {line.strip()}")

search_in_file(r"c:\Users\palep\OneDrive\Desktop\Harikaaaa\src\evaluator.py", ["verdict", "risk", "trust", "score"])
