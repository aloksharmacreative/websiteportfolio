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
    
    # 1. Update header Contact link in all_projects.html
    if fn == 'all_projects.html':
        header = soup.find('header')
        if header:
            for a in header.find_all('a'):
                text = a.get_text(strip=True).lower()
                if text == 'contact':
                    a['href'] = '/#contact'
                    modified = True
                    print(f"[{fn}] Updated header Contact link to /#contact")

    # 2. Update footer Contact link to /#contact in all templates
    footer = soup.find('footer')
    if footer:
        for a in footer.find_all('a'):
            text = a.get_text(strip=True).lower()
            if text == 'contact':
                a['href'] = '/#contact'
                modified = True
                print(f"[{fn}] Updated footer Contact link to /#contact")
                
        # 3. Unlink Privacy Policy and Terms of Service in the footer
        # Find all <a> tags inside footer that contain "privacy" or "terms"
        for a in footer.find_all('a'):
            a_text = a.get_text(strip=True).lower()
            if 'privacy' in a_text or 'terms' in a_text:
                # Replace with span
                span = soup.new_tag('span')
                span.string = a.get_text(strip=True)
                # Keep color style without hover pointer or transitions
                span['class'] = 'text-secondary-foreground/40'
                a.replace_with(span)
                modified = True
                print(f"[{fn}] Unlinked: {a_text}")
                
    if modified:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(str(soup))

print("Link adjustments successfully completed.")
