import os
from bs4 import BeautifulSoup

templates_dir = r"C:\Users\ak955\.gemini\antigravity\scratch\designer-portfolio\templates"

for filename in os.listdir(templates_dir):
    if not filename.endswith('.html'):
        continue
        
    path = os.path.join(templates_dir, filename)
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    modified = False
    
    # 1. Update Header Logo
    # Find any div with text-2xl that contains "Alok" and "Sharma"
    for div in soup.find_all(['div', 'a'], class_='text-2xl'):
        text = div.get_text()
        if 'Alok' in text and 'Sharma' in text:
            # Change name to 'a'
            div.name = 'a'
            div['href'] = '/'
            # Remove any trailing dot in the span
            span = div.find('span', class_='text-primary')
            if span:
                span.string = 'Sharma'
                modified = True
                print(f"[{filename}] Updated header logo to clickable link without dot")

    # 2. Update Footer Logo
    # Find any div with text-3xl that contains "Alok" and "Sharma"
    for div in soup.find_all(['div', 'a'], class_='text-3xl'):
        text = div.get_text()
        if 'Alok' in text and 'Sharma' in text:
            div.name = 'a'
            div['href'] = '/'
            span = div.find('span', class_='text-primary')
            if span:
                span.string = 'Sharma'
                modified = True
                print(f"[{filename}] Updated footer logo to clickable link without dot")

    if modified:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(str(soup))

print("Logo adjustments completed for all templates.")
