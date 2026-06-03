import os
import json

history_path = os.path.expandvars('%APPDATA%/Code/User/History')
found = []

for root, dirs, files in os.walk(history_path):
    if 'entries.json' in files:
        entries_file = os.path.join(root, 'entries.json')
        try:
            with open(entries_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            resource = data.get('resource', '')
            if 'harikaaaa' in resource.lower() and 'html' in resource.lower():
                print(f"Resource: {resource}")
                entries = data.get('entries', [])
                for entry in entries:
                    entry_id = entry.get('id')
                    history_file = os.path.join(root, entry_id)
                    size = os.path.getsize(history_file) if os.path.exists(history_file) else 0
                    print(f"  Entry: {entry_id} Size: {size}")
                    found.append((resource, history_file, size))
        except Exception as e:
            pass

print(f"\nTotal entries found: {len(found)}")
