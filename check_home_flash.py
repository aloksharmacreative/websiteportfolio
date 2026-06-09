with open('templates/home.html', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        if 'get_flashed_messages' in line:
            print(f"Line {idx}: {line.strip()}")
