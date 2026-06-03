import os

file_path = "src/main.py"
with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find the start of the SQLite section
db_start_idx = -1
for i, line in enumerate(lines):
    if "# ── Secure SQLite User Store ────────────────────────────────────────────────" in line:
        db_start_idx = i
        break

# Extract up to the /api/me endpoint
db_end_idx = -1
for i in range(db_start_idx, len(lines)):
    if "@app.get(\"/api/me\")" in lines[i]:
        db_end_idx = i
        break

if db_start_idx != -1 and db_end_idx != -1:
    db_block = lines[db_start_idx:db_end_idx]
    
    # Remove the block from original lines
    new_lines = lines[:db_start_idx] + lines[db_end_idx:]
    
    # Find insertion point (after app.add_middleware block)
    insert_idx = -1
    for i, line in enumerate(new_lines):
        if "app.add_middleware" in line:
            # skip the middleware block
            for j in range(i, len(new_lines)):
                if ")" in new_lines[j]:
                    insert_idx = j + 2
                    break
            break
            
    if insert_idx != -1:
        new_lines = new_lines[:insert_idx] + ["\n"] + db_block + ["\n"] + new_lines[insert_idx:]
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print("Successfully moved DB block.")
    else:
        print("Could not find insertion point.")
else:
    print("Could not find DB block boundaries.")
