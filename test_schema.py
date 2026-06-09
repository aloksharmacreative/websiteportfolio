import requests
import database

url = f"{database.SUPABASE_URL}/rest/v1/projects"
params = {"select": "*", "limit": "1"}
res = requests.get(url, headers=database.get_headers(), params=params)
if res.status_code == 200:
    data = res.json()
    if data:
        print("Columns returned from database:", list(data[0].keys()))
        if "media_gallery" in data[0]:
            print("media_gallery column exists in projects table!")
        else:
            print("media_gallery column does NOT exist in projects table.")
else:
    print("Failed to fetch projects schema:", res.status_code, res.text)
