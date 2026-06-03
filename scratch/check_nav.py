with open("static/app.js", "r", encoding="utf-8") as f:
    for line_num, line in enumerate(f, 1):
        if "nav-login-btn" in line:
            print(f"{line_num}: {line.strip()}")
