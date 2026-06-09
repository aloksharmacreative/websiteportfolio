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
    
    # 1. Update <body> tag to have class="overflow-x-hidden"
    body = soup.body
    if body:
        # Check if class exists, if not, add it
        classes = body.get('class', [])
        if 'overflow-x-hidden' not in classes:
            classes.append('overflow-x-hidden')
            body['class'] = classes
            modified = True
            print(f"[{fn}] Added overflow-x-hidden to <body> tag")

    # 2. Find the outer wrapper div and remove overflow-x-hidden
    # The outer wrapper is usually the first div inside body with class containing min-h-screen
    if body:
        outer_div = body.find('div')
        if outer_div and 'min-h-screen' in outer_div.get('class', []):
            div_classes = outer_div.get('class', [])
            if 'overflow-x-hidden' in div_classes:
                div_classes.remove('overflow-x-hidden')
                outer_div['class'] = div_classes
                modified = True
                print(f"[{fn}] Removed overflow-x-hidden from outer wrapper <div>")
                
    if modified:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(str(soup))

print("Sticky layout fixes completed.")
