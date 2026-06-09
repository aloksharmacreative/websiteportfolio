import os
from bs4 import BeautifulSoup

templates_dir = r"C:\Users\ak955\.gemini\antigravity\scratch\designer-portfolio\templates"

for fn in os.listdir(templates_dir):
    if not fn.endswith('.html'):
        continue
    path = os.path.join(templates_dir, fn)
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    modified = False
    
    # Update header Contact link in all_projects.html
    header = soup.find('header')
    if header:
        for a in header.find_all('a'):
            text = a.get_text(strip=True).lower()
            if text == 'work':
                a['href'] = '/#work'
                modified = True
                print(f"[{fn}] Updated header Work link to /#work")
                
    # Check general nav tags in case header markup varies
    nav = soup.find('nav')
    if nav:
        for a in nav.find_all('a'):
            text = a.get_text(strip=True).lower()
            if text == 'work':
                a['href'] = '/#work'
                modified = True
                print(f"[{fn}] Updated nav Work link to /#work")
                
    if modified:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(str(soup))

print("Work navigation link updates completed.")
