from bs4 import BeautifulSoup
import os

path = r"C:\Users\ak955\.gemini\antigravity\scratch\designer-portfolio\templates\home.html"

with open(path, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

for h3 in soup.find_all('h3'):
    if 'SocialEat' in h3.text or 'Modern Furniture' in h3.text:
        print("=== Found H3:", h3.text)
        # Traverse up to see parent card elements
        curr = h3
        for i in range(4):
            curr = curr.parent
            if curr:
                # Print class and tags
                print(f"  Parent level {i+1}: <{curr.name} class='{curr.get('class')}'>")
                links = [(a.text.strip(), a.get('href')) for a in curr.find_all('a')]
                if links:
                    print("    Links inside:", links)
