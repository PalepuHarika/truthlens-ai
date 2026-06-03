import re

with open("C:/Users/palep/.gemini/antigravity/brain/7071621a-b572-4c04-801f-106ef3529735/scratch/index_backup.html", "r", encoding="utf-8") as f:
    html = f.read()

# Let's search for class="workflow" or similar
matches = [m.start() for m in re.finditer(r'class="workflow"', html)]
for idx, start in enumerate(matches):
    print(f"Match {idx+1}:")
    print(html[max(0, start-100):min(len(html), start+800)])
    print("="*60)
