import os
import re

base_dir = r"C:\Users\ak955\.gemini\antigravity\scratch\designer-portfolio"
html_path = os.path.join(base_dir, "templates", "home.html")
out_path = os.path.join(base_dir, "search_results.txt")

with open(html_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

output = []
for idx, line in enumerate(lines, 1):
    if 'projects' in line.lower() or 'project' in line.lower():
        output.append(f"{idx}: {line.strip()}")

with open(out_path, 'w', encoding='utf-8') as f:
    if not output:
        f.write("No matches found.")
    else:
        f.write('\n'.join(output))
print(f"Done searching. Matches: {len(output)}")
