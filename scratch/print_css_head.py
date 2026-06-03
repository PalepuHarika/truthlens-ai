with open("static/style.css", "r", encoding="utf-8") as f:
    for idx in range(100):
        print(f.readline().strip())
