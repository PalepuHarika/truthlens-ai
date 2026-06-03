terms = ["Mathematical Certainty", "state-of-the-art", "State-of-the-art", "Learn More"]
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

for t in terms:
    count = html.count(t)
    print(f"Found {count} occurrences of '{t}'")
