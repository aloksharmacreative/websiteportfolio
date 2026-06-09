with open('templates/home.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

def check_keyword(kw):
    print(f"\n=== MATCHES FOR '{kw}': ===")
    for idx, line in enumerate(lines, 1):
        if kw in line.lower():
            print(f"{idx}: {line.strip()[:150]}")

check_keyword("linkedin")
check_keyword("dribbble")
check_keyword("instagram")
check_keyword("twitter")
check_keyword("© 202")
