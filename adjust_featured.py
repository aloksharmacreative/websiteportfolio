import os
from bs4 import BeautifulSoup

path = r"C:\Users\ak955\.gemini\antigravity\scratch\designer-portfolio\templates\home.html"

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()
    
soup = BeautifulSoup(html, 'html.parser')
modified = False

for h3 in soup.find_all('h3'):
    text = h3.get_text(strip=True)
    if 'SocialEat' in text:
        # This is the SocialEat Mobile Experience
        # Sibling or ancestor link:
        parent_card = h3.find_parent('div', class_='flex-col') or h3.parent.parent
        if parent_card:
            for a in parent_card.find_all('a'):
                if 'Case Study' in a.get_text():
                    a['href'] = '/project/2'
                    modified = True
                    print("Updated SocialEat case study button link to /project/2")
    elif 'Furniture' in text:
        # This is the Modern Furniture E-commerce
        parent_card = h3.find_parent('div', class_='flex-col') or h3.parent.parent
        if parent_card:
            for a in parent_card.find_all('a'):
                if 'Case Study' in a.get_text():
                    a['href'] = '/project/1'
                    modified = True
                    print("Updated Furniture case study button link to /project/1")

if modified:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print("home.html featured case study buttons updated successfully.")
else:
    print("No featured case study buttons modified.")
