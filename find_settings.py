import os

base_dir = r"C:\Users\ak955\.gemini\antigravity\scratch\designer-portfolio"
templates_dir = os.path.join(base_dir, "templates")

matches = []
for f in os.listdir(templates_dir):
    if f.endswith(".html"):
        path = os.path.join(templates_dir, f)
        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()
        for idx, line in enumerate(lines, 1):
            if "settings" in line:
                matches.append(f"{f}:{idx}: {line.strip()}")

out_path = os.path.join(base_dir, "settings_search.txt")
with open(out_path, "w", encoding="utf-8") as out:
    out.write("\n".join(matches))
print(f"Finished. Found {len(matches)} matches.")
