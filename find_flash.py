import glob

for f in glob.glob('templates/*.html'):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
        if 'get_flashed_messages' in content:
            print(f"File {f} contains get_flashed_messages")
