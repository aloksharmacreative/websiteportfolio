import os
import re
from bs4 import BeautifulSoup

def convert_home():
    path = r"C:\Users\ak955\.gemini\antigravity\scratch\designer-portfolio\templates\home.html"
    if not os.path.exists(path):
        print("home.html not found.")
        return
        
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Update Navigation and Action Links globally
    for a in soup.find_all('a'):
        text = a.get_text(strip=True).lower()
        href = a.get('href', '')
        
        if 'hire' in text:
            a['href'] = '/hire'
        elif 'connect' in text:
            a['href'] = '/contact'
        elif 'book' in text:
            a['href'] = '/book'
        elif 'view' in text and 'work' in text:
            a['href'] = '/projects'
        elif text == 'work':
            a['href'] = '/projects'
        elif text == 'contact':
            a['href'] = '/contact'
        elif text == 'selected work':
            a['href'] = '/projects'
            
    # 2. Add Flash Messaging at the top of the body
    body = soup.body
    if body:
        # We can insert the flash block at the beginning of the container
        container = body.find('div', class_='min-h-screen')
        if container:
            # Create a simple flash block string
            flash_str = """
            {% with messages = get_flashed_messages(with_categories=true) %}
              {% if messages %}
                <div class="fixed top-6 left-1/2 -translate-x-1/2 z-50 w-full max-w-md px-4">
                  {% for category, msg in messages %}
                    <div class="p-5 rounded-2xl border shadow-2xl text-sm font-bold {% if category == 'success' %}bg-green-50 text-green-800 border-green-200{% else %}bg-red-50 text-red-800 border-red-200{% endif %}" onclick="this.remove()">
                      {{ msg }}
                    </div>
                  {% endfor %}
                </div>
              {% endif %}
            {% endwith %}
            """
            flash_soup = BeautifulSoup(flash_str, 'html.parser')
            # Insert after the header
            header = container.find('header')
            if header:
                header.insert_after(flash_soup)
                
    # 3. Inject Admin Link in Navbar if logged in
    nav = soup.find('nav')
    if nav:
        admin_link_str = """
        {% if session.get('admin_logged_in') %}
          <a href="/admin" class="text-red-600 font-bold hover:text-red-800 transition-colors">Dashboard</a>
          <a href="/admin/logout" class="hover:text-foreground transition-colors">Logout</a>
        {% endif %}
        """
        admin_link_soup = BeautifulSoup(admin_link_str, 'html.parser')
        nav.append(admin_link_soup)

    # 4. Replace Selected Projects Grid
    # We find the heading "Selected Projects" and then look for its sibling grid
    selected_heading = None
    for h2 in soup.find_all('h2'):
        if 'Selected Projects' in h2.get_text():
            selected_heading = h2
            break
            
    if selected_heading:
        # Sibling grid is usually the next sibling container holding the projects
        # Let's search for the projects grid which contains multiple project items
        # Sibling grid
        grid = selected_heading.find_next('div', class_='grid')
        if grid:
            # We replace its entire contents with our dynamic Jinja2 loop
            project_loop_str = """
            {% for p in projects %}
            <div class="group flex flex-col gap-6 cursor-pointer" onclick="location.href='/project/{{ p.id }}'">
              <div class="relative overflow-hidden rounded-3xl aspect-[4/3] bg-muted">
                <img src="{{ p.image_url }}" alt="{{ p.title }}" class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105">
                <div class="absolute inset-0 bg-secondary/80 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
                  <span class="w-16 h-16 bg-primary text-primary-foreground rounded-full flex items-center justify-center transform scale-0 group-hover:scale-100 transition-transform duration-500 delay-100">
                    <iconify-icon icon="lucide:arrow-up-right" class="text-2xl"></iconify-icon>
                  </span>
                </div>
              </div>
              <div>
                <span class="text-primary text-sm font-medium tracking-wider uppercase mb-2 block">{{ p.category }}</span>
                <h3 class="text-2xl font-heading font-bold mb-2 text-foreground group-hover:text-primary transition-colors">{{ p.title }}</h3>
                <p class="text-muted-foreground text-sm">{{ p.description }}</p>
              </div>
            </div>
            {% endfor %}
            """
            grid.clear()
            grid.append(BeautifulSoup(project_loop_str, 'html.parser'))
            print("Successfully replaced projects grid in home.html.")
            
    # Write back
    with open(path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
        
def convert_all_projects():
    path = r"C:\Users\ak955\.gemini\antigravity\scratch\designer-portfolio\templates\all_projects.html"
    if not os.path.exists(path):
        print("all_projects.html not found.")
        return
        
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Update Navigation and Action Links
    for a in soup.find_all('a'):
        text = a.get_text(strip=True).lower()
        if 'hire' in text:
            a['href'] = '/hire'
        elif 'connect' in text:
            a['href'] = '/contact'
        elif 'book' in text:
            a['href'] = '/book'
        elif text == 'work':
            a['href'] = '/projects'
        elif text == 'contact':
            a['href'] = '/contact'
        elif text == 'selected work':
            a['href'] = '/'
            
    # 2. Inject Admin Link in Navbar
    nav = soup.find('nav')
    if nav:
        admin_link_str = """
        {% if session.get('admin_logged_in') %}
          <a href="/admin" class="text-red-600 font-bold hover:text-red-800 transition-colors">Dashboard</a>
          <a href="/admin/logout" class="hover:text-foreground transition-colors">Logout</a>
        {% endif %}
        """
        nav.append(BeautifulSoup(admin_link_str, 'html.parser'))

    # 3. Update Category Filter Buttons
    # The active filter tab should have class "bg-primary text-primary-foreground shadow-lg shadow-primary/25"
    # Sibling tabs should have class "bg-background border border-border text-foreground hover:border-foreground"
    filter_container = soup.find('div', class_='flex-wrap')
    if filter_container:
        filter_str = """
        <a href="/projects?category=All" class="px-6 py-3 rounded-full font-medium text-sm transition-colors {% if active_category == 'All' %}bg-primary text-primary-foreground shadow-lg shadow-primary/25{% else %}bg-background border border-border text-foreground hover:border-foreground{% endif %}">All Work</a>
        <a href="/projects?category=UI/UX Design" class="px-6 py-3 rounded-full font-medium text-sm transition-colors {% if active_category == 'UI/UX Design' %}bg-primary text-primary-foreground shadow-lg shadow-primary/25{% else %}bg-background border border-border text-foreground hover:border-foreground{% endif %}">UI/UX Design</a>
        <a href="/projects?category=Web Design" class="px-6 py-3 rounded-full font-medium text-sm transition-colors {% if active_category == 'Web Design' %}bg-primary text-primary-foreground shadow-lg shadow-primary/25{% else %}bg-background border border-border text-foreground hover:border-foreground{% endif %}">Web Design</a>
        <a href="/projects?category=Mobile Apps" class="px-6 py-3 rounded-full font-medium text-sm transition-colors {% if active_category == 'Mobile Apps' %}bg-primary text-primary-foreground shadow-lg shadow-primary/25{% else %}bg-background border border-border text-foreground hover:border-foreground{% endif %}">Mobile Apps</a>
        <a href="/projects?category=Branding" class="px-6 py-3 rounded-full font-medium text-sm transition-colors {% if active_category == 'Branding' %}bg-primary text-primary-foreground shadow-lg shadow-primary/25{% else %}bg-background border border-border text-foreground hover:border-foreground{% endif %}">Branding</a>
        """
        filter_container.clear()
        filter_container.append(BeautifulSoup(filter_str, 'html.parser'))

    # 4. Replace Projects Grid with dynamic loop
    grid = soup.find('div', class_='grid')
    if grid:
        project_loop_str = """
        {% for p in projects %}
        <div class="group flex flex-col gap-6 cursor-pointer" onclick="location.href='/project/{{ p.id }}'">
          <div class="relative overflow-hidden rounded-3xl aspect-[4/3] bg-muted">
            <img src="{{ p.image_url }}" alt="{{ p.title }}" class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105">
            <div class="absolute inset-0 bg-secondary/80 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
              <span class="w-16 h-16 bg-primary text-primary-foreground rounded-full flex items-center justify-center transform scale-0 group-hover:scale-100 transition-transform duration-500 delay-100">
                <iconify-icon icon="lucide:arrow-up-right" class="text-2xl"></iconify-icon>
              </span>
            </div>
          </div>
          <div>
            <span class="text-primary text-sm font-medium tracking-wider uppercase mb-2 block">{{ p.category }}</span>
            <h3 class="text-2xl font-heading font-bold mb-2 text-foreground group-hover:text-primary transition-colors">{{ p.title }}</h3>
            <p class="text-muted-foreground text-sm">{{ p.description }}</p>
          </div>
        </div>
        {% endfor %}
        """
        grid.clear()
        grid.append(BeautifulSoup(project_loop_str, 'html.parser'))
        print("Successfully replaced projects grid in all_projects.html.")
        
    # Write back
    with open(path, 'w', encoding='utf-8') as f:
        f.write(str(soup))

if __name__ == '__main__':
    convert_home()
    convert_all_projects()
