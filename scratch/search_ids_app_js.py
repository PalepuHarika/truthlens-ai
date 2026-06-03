with open("static/app.js", "r", encoding="utf-8") as f:
    content = f.read()

ids_to_search = ["db-overall-risk", "db-risk-sub", "db-trust-verdict", "risk-display", "db-trust-fill", "db-trust-score"]

for id_name in ids_to_search:
    print(f"=== Matches for {id_name} ===")
    for line_no, line in enumerate(content.splitlines(), 1):
        if id_name in line:
            print(f"L{line_no}: {line.strip()}")
