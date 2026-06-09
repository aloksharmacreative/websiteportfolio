import re

with open('templates/home.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's find spans or divs with numbers/stats
stats_candidates = re.findall(r'(\d+[\+\%][^\n<]*)', text)
print("Stats Candidates:")
for s in stats_candidates:
    print("-", s.strip())

# Find any email addresses in the file
emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
print("Emails found:", list(set(emails)))
