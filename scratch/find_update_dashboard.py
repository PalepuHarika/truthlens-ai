with open("static/app.js", "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find("function updateDashboardUI()")
if idx != -1:
    print(content[idx:idx+2500])
else:
    print("Not found")
