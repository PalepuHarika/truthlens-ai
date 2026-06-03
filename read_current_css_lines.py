def main():
    try:
        with open(r"c:\Users\palep\OneDrive\Desktop\Harikaaaa\static\style.css", "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error: {e}")
        return

    start = 70
    end = 100
    for idx in range(start - 1, min(end, len(lines))):
        line = lines[idx].strip()
        print(f"{idx+1}: {line}")

if __name__ == '__main__':
    main()
