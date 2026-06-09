import os
from bs4 import BeautifulSoup

templates_dir = r"C:\Users\ak955\.gemini\antigravity\scratch\designer-portfolio\templates"

for fn in os.listdir(templates_dir):
    if not fn.endswith('.html'):
        continue
    path = os.path.join(templates_dir, fn)
    with open(path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    contact_links = []
    for a in soup.find_all('a'):
        text = a.get_text(strip=True).lower()
        href = a.get('href', '')
        if 'contact' in text or 'contact' in href:
            location = 'body'
            if a.find_parent('header'):
                location = 'header'
            elif a.find_parent('footer'):
                location = 'footer'
            contact_links.append((a.get_text(strip=True), href, location))
            
    pp = [(a.get_text(strip=True), a.get('href')) for a in soup.find_all('a') if 'privacy' in a.get_text(strip=True).lower()]
    tos = [(a.get_text(strip=True), a.get('href')) for a in soup.find_all('a') if 'terms' in a.get_text(strip=True).lower()]
    
    if contact_links or pp or tos:
        print(f"=== {fn} ===")
        print("  Contact links:", contact_links)
        print("  Privacy Policy:", pp)
        print("  Terms of Service:", tos)
