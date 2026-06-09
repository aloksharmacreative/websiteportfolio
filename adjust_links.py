import os
from bs4 import BeautifulSoup

path = r"C:\Users\ak955\.\gemini\antigravity\scratch\designer-portfolio\templates\home.html"
if not os.path.exists(path):
    path = r"C:\Users\ak955\gemini\antigravity\scratch\designer-portfolio\templates\home.html"
    if not os.path.exists(path):
        path = r"C:\Users\ak955\.gemini\antigravity\scratch\designer-portfolio\templates\home.html"

print("Reading from:", path)
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()
    
soup = BeautifulSoup(html, 'html.parser')

# 1. Update navigation links in header (and globally except inside the #contact section)
# We find the header element to be safe
header = soup.find('header')
if header:
    for a in header.find_all('a'):
        text = a.get_text(strip=True).lower()
        if text == 'contact':
            a['href'] = '/#contact'
            print("Updated header navbar Contact link to /#contact")

# Also check for any general nav tag
nav = soup.find('nav')
if nav:
    for a in nav.find_all('a'):
        text = a.get_text(strip=True).lower()
        if text == 'contact':
            a['href'] = '/#contact'
            print("Updated nav Contact link to /#contact")

# 2. Find the #contact section at the bottom
contact_section = soup.find(id='contact')
if contact_section:
    # Sibling buttons are inside this section
    for a in contact_section.find_all('a'):
        text = a.get_text(strip=True).lower()
        if 'send' in text or 'email' in text:
            a['href'] = '/contact'
            print("Updated Send Email button inside #contact section to /contact")
        elif 'book' in text:
            a['href'] = '/book'
            print("Ensured Book a Call button points to /book")
else:
    print("Contact section with id='contact' not found!")
    # Fallback search for a link with mailto:
    for a in soup.find_all('a'):
        href = a.get('href', '')
        if 'mailto:' in href or 'hello@aloksharma' in href:
            a['href'] = '/contact'
            print("Fallback: Updated mailto link to /contact")

# Write changes back
with open(path, 'w', encoding='utf-8') as f:
    f.write(str(soup))
print("Finished modifying home.html navigation.")
