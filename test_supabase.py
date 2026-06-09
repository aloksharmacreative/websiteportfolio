import requests

SUPABASE_URL = "https://kqpbejqntgbwxsbsuxfk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtxcGJlanFudGdid3hzYnN1eGZrIiwicm9sZES6ImFub24iLCJpYXQiOjE3ODA5Mjk0NTYsImV4cCI6MjA5NjUwNTQ1Nn0.J0ZRKAY6HIA1SP5I1T83QGDGTEv2fVwI3Cqepq4A8S4"

# Let's fix the typo in user key if there is one, wait, the user pasted it.
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtxcGJlanFudGdid3hzYnN1eGZrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA5Mjk0NTYsImV4cCI6MjA5NjUwNTQ1Nn0.J0ZRKAY6HIA1SP5I1T83QGDGTEv2fVwI3Cqepq4A8S4"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

print("Checking Supabase connection and tables with correct syntax...")

tables = ['projects', 'messages', 'hires', 'bookings', 'settings', 'reviews']
for table in tables:
    url = f"{SUPABASE_URL}/rest/v1/{table}?select=*&limit=1"
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            print(f"  [SUCCESS] Table '{table}' exists! Data: {res.json()}")
        elif res.status_code == 404:
            print(f"  [MISSING] Table '{table}' does NOT exist (404).")
        else:
            print(f"  [ERROR] Table '{table}' returned status {res.status_code}: {res.text[:200]}")
    except Exception as e:
        print(f"  [FAIL] Failed to connect for '{table}': {e}")
