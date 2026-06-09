import os
import requests
from dotenv import load_dotenv

# Load env variables for standalone script imports
load_dotenv()

SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://kqpbejqntgbwxsbsuxfk.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtxcGJlanFudGdid3hzYnN1eGZrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA5Mjk0NTYsImV4cCI6MjA5NjUwNTQ1Nn0.J0ZRKAY6HIA1SP5I1T83QGDGTEv2fVwI3Cqepq4A8S4')

def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def upload_to_supabase_storage(file_data, filename, mime_type, bucket="portfolio"):
    """
    Uploads raw binary data to a Supabase Storage bucket.
    Returns the public URL of the uploaded file if successful, otherwise None.
    """
    import urllib.parse
    safe_filename = urllib.parse.quote(filename.replace(" ", "_"))
    
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{safe_filename}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": mime_type
    }
    try:
        res = requests.post(url, headers=headers, data=file_data)
        if res.status_code == 200:
            return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{safe_filename}"
        print(f"Supabase Storage Upload Error: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"Failed to upload to Supabase Storage: {e}")
    return None

class SupabaseRow(dict):
    """A dictionary wrapper to mock sqlite3.Row index-based and key-based access."""
    def __getattr__(self, name):
        return self.get(name)
        
    def __getitem__(self, item):
        # Override to format dates or handle fallbacks
        val = self.get(item)
        if item == 'date_created' and val and 'T' in val:
            return val.split('T')[0]
        return val

# ----------------- PROJECTS TABLE OPERATIONS -----------------

def get_projects(category=None, limit=None):
    """Fetches all projects or filters by category."""
    url = f"{SUPABASE_URL}/rest/v1/projects"
    params = {
        "select": "*",
        "order": "sort_order.asc,id.desc"
    }
    if category and category != 'All':
        params["category"] = f"eq.{category}"
    if limit:
        params["limit"] = str(limit)
        
    try:
        res = requests.get(url, headers=get_headers(), params=params)
        if res.status_code == 200:
            return [SupabaseRow(item) for item in res.json()]
            
        # Fallback if sort_order column hasn't been created yet in the DB
        if res.status_code == 400 and ("sort_order" in res.text or "not found" in res.text or "exist" in res.text):
            params["order"] = "id.desc"
            res_retry = requests.get(url, headers=get_headers(), params=params)
            if res_retry.status_code == 200:
                return [SupabaseRow(item) for item in res_retry.json()]
                
        print(f"Supabase get_projects error: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"Failed to fetch projects from Supabase: {e}")
    return []

def get_project(project_id):
    """Fetches a single project by ID."""
    url = f"{SUPABASE_URL}/rest/v1/projects"
    params = {
        "select": "*",
        "id": f"eq.{project_id}"
    }
    try:
        res = requests.get(url, headers=get_headers(), params=params)
        if res.status_code == 200 and res.json():
            return SupabaseRow(res.json()[0])
        print(f"Supabase get_project error: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"Failed to fetch project {project_id} from Supabase: {e}")
    return None

def clean_payload_and_retry(url, payload, method, params=None):
    """Retries a POST or PATCH request after stripping columns that do not exist in the Supabase schema."""
    import re
    headers = get_headers()
    current_payload = payload.copy()
    
    for attempt in range(15):  # Allow up to 15 retries to strip all missing columns one by one
        try:
            if method == 'post':
                res = requests.post(url, json=current_payload, headers=headers)
            else:
                res = requests.patch(url, json=current_payload, headers=headers, params=params)
                
            if res.status_code in (200, 201, 204):
                if len(current_payload) < len(payload):
                    removed = set(payload.keys()) - set(current_payload.keys())
                    return True, f"Warning: Saved successfully, but the following columns were missing in your Supabase schema and were skipped: {', '.join(removed)}. Please run the SQL schema update script."
                return True, "Success"
                
            if res.status_code == 404:
                return False, "Table 'projects' does not exist in Supabase (404). Please execute the setup SQL script in your Supabase Dashboard SQL Editor first."
                
            # Parse Supabase error for missing columns.
            # PostgREST returns 400 Bad Request if a column is missing.
            if res.status_code == 400:
                # e.g., "Could not find the 'video_url' column of 'projects' in the schema cache"
                match = re.search(r"find the '([^']+)' column", res.text)
                if not match:
                    # e.g., "column 'video_url' of relation 'projects' does not exist"
                    match = re.search(r"column ['\"]([^'\"]+)['\"] of relation", res.text)
                if not match:
                    # e.g., "column 'video_url' does not exist"
                    match = re.search(r"column ['\"]([^'\"]+)['\"] does not exist", res.text)
                
                if match:
                    missing_col = match.group(1)
                    if missing_col in current_payload:
                        del current_payload[missing_col]
                        continue
            
            # If we get here and it's not a missing column error or we can't parse it, return the error
            return False, f"Supabase error {res.status_code}: {res.text}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
            
    return False, "Too many missing columns, giving up."

def insert_project(title, category, image_url, description, details, live_url, github_url, video_url=None,
                   challenge=None, solution=None, metric1_value=None, metric1_label=None,
                   metric2_value=None, metric2_label=None, is_featured_case_study=False,
                   original_image_url=None, media_gallery=None):
    """Uploads a new project details to Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/projects"
    payload = {
        "title": title,
        "category": category,
        "image_url": image_url,
        "original_image_url": original_image_url,
        "media_gallery": media_gallery,
        "description": description,
        "details": details,
        "live_url": live_url,
        "github_url": github_url,
        "video_url": video_url,
        "challenge": challenge,
        "solution": solution,
        "metric1_value": metric1_value,
        "metric1_label": metric1_label,
        "metric2_value": metric2_value,
        "metric2_label": metric2_label,
        "is_featured_case_study": bool(is_featured_case_study)
    }
    return clean_payload_and_retry(url, payload, 'post')

def update_project(project_id, title, category, image_url, description, details, live_url, github_url, video_url=None,
                   challenge=None, solution=None, metric1_value=None, metric1_label=None,
                   metric2_value=None, metric2_label=None, is_featured_case_study=False,
                   original_image_url=None, media_gallery=None):
    """Edits an existing project details in Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/projects"
    params = {
        "id": f"eq.{project_id}"
    }
    payload = {
        "title": title,
        "category": category,
        "image_url": image_url,
        "original_image_url": original_image_url,
        "media_gallery": media_gallery,
        "description": description,
        "details": details,
        "live_url": live_url,
        "github_url": github_url,
        "video_url": video_url,
        "challenge": challenge,
        "solution": solution,
        "metric1_value": metric1_value,
        "metric1_label": metric1_label,
        "metric2_value": metric2_value,
        "metric2_label": metric2_label,
        "is_featured_case_study": bool(is_featured_case_study)
    }
    return clean_payload_and_retry(url, payload, 'patch', params=params)

def update_project_order(project_id, sort_order):
    """Updates only the sort_order of a project."""
    url = f"{SUPABASE_URL}/rest/v1/projects"
    params = {
        "id": f"eq.{project_id}"
    }
    payload = {
        "sort_order": int(sort_order)
    }
    try:
        res = requests.patch(url, json=payload, headers=get_headers(), params=params)
        if res.status_code in (200, 201, 204):
            return True, "Success"
        return False, f"Supabase error {res.status_code}: {res.text}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def delete_project(project_id):
    """Removes a project from Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/projects"
    params = {
        "id": f"eq.{project_id}"
    }
    try:
        res = requests.delete(url, headers=get_headers(), params=params)
        if res.status_code in (200, 201, 204):
            return True, "Success"
        if res.status_code == 404:
            return False, "Table 'projects' does not exist in Supabase (404). Please execute the setup SQL script in your Supabase Dashboard SQL Editor first."
        return False, f"Supabase error {res.status_code}: {res.text}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

# ----------------- MESSAGES TABLE OPERATIONS -----------------

def get_messages():
    """Fetches all general contact messages."""
    url = f"{SUPABASE_URL}/rest/v1/messages?select=*&order=id.desc"
    try:
        res = requests.get(url, headers=get_headers())
        if res.status_code == 200:
            return [SupabaseRow(item) for item in res.json()]
    except Exception as e:
        print(f"Failed to fetch messages: {e}")
    return []

def insert_message(first_name, last_name, email, subject, message):
    """Persists a new contact message."""
    url = f"{SUPABASE_URL}/rest/v1/messages"
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "subject": subject,
        "message": message
    }
    try:
        res = requests.post(url, json=payload, headers=get_headers())
        if res.status_code in (200, 201):
            return True, "Success"
        if res.status_code == 404:
            return False, "Table 'messages' does not exist in Supabase (404). Please execute the setup SQL script in your Supabase Dashboard SQL Editor first."
        return False, f"Supabase error {res.status_code}: {res.text}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

# ----------------- HIRES TABLE OPERATIONS -----------------

def get_hires():
    """Fetches all project hire inquiries."""
    url = f"{SUPABASE_URL}/rest/v1/hires?select=*&order=id.desc"
    try:
        res = requests.get(url, headers=get_headers())
        if res.status_code == 200:
            return [SupabaseRow(item) for item in res.json()]
    except Exception as e:
        print(f"Failed to fetch hires: {e}")
    return []

def insert_hire(name, email, company, website, services, description, budget, timeline):
    """Persists a new hire project inquiry."""
    url = f"{SUPABASE_URL}/rest/v1/hires"
    payload = {
        "name": name,
        "email": email,
        "company": company,
        "website": website,
        "services": services,
        "description": description,
        "budget": budget,
        "timeline": timeline
    }
    try:
        res = requests.post(url, json=payload, headers=get_headers())
        if res.status_code in (200, 201):
            return True, "Success"
        if res.status_code == 404:
            return False, "Table 'hires' does not exist in Supabase (404). Please execute the setup SQL script in your Supabase Dashboard SQL Editor first."
        return False, f"Supabase error {res.status_code}: {res.text}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

# ----------------- BOOKINGS TABLE OPERATIONS -----------------

def get_bookings():
    """Fetches all call discovery bookings."""
    url = f"{SUPABASE_URL}/rest/v1/bookings?select=*&order=id.desc"
    try:
        res = requests.get(url, headers=get_headers())
        if res.status_code == 200:
            return [SupabaseRow(item) for item in res.json()]
    except Exception as e:
        print(f"Failed to fetch bookings: {e}")
    return []

def insert_booking(name, email, booking_date, booking_time):
    """Saves a scheduled discovery call."""
    url = f"{SUPABASE_URL}/rest/v1/bookings"
    payload = {
        "name": name,
        "email": email,
        "booking_date": booking_date,
        "booking_time": booking_time
    }
    try:
        res = requests.post(url, json=payload, headers=get_headers())
        if res.status_code in (200, 201):
            return True, "Success"
        if res.status_code == 404:
            return False, "Table 'bookings' does not exist in Supabase (404). Please execute the setup SQL script in your Supabase Dashboard SQL Editor first."
        return False, f"Supabase error {res.status_code}: {res.text}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

# ----------------- SETTINGS TABLE OPERATIONS -----------------

def get_settings_dict():
    """Fetches all site settings as a key-value dictionary."""
    url = f"{SUPABASE_URL}/rest/v1/settings"
    params = {"select": "key,value"}
    try:
        res = requests.get(url, headers=get_headers(), params=params)
        if res.status_code == 200:
            return {item['key']: item['value'] for item in res.json()}
        print(f"Supabase get_settings error: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"Failed to fetch settings from Supabase: {e}")
    
    # Return empty dict, fallback will be used
    return {}

def update_setting(key, value):
    """Updates or inserts a single setting key-value pair."""
    settings = get_settings_dict()
    url = f"{SUPABASE_URL}/rest/v1/settings"
    if key in settings:
        params = {"key": f"eq.{key}"}
        payload = {"value": value}
        try:
            res = requests.patch(url, json=payload, headers=get_headers(), params=params)
            return res.status_code in (200, 201, 204)
        except Exception as e:
            print(f"Error updating setting {key}: {e}")
            return False
    else:
        payload = {"key": key, "value": value}
        try:
            res = requests.post(url, json=payload, headers=get_headers())
            return res.status_code in (200, 201, 204)
        except Exception as e:
            print(f"Error inserting setting {key}: {e}")
            return False

def save_setting(key, value):
    """Saves a setting, inserting it if it does not exist, or updating it if it does."""
    return update_setting(key, value)

def update_settings(settings_dict):
    """Updates multiple site settings in Supabase."""
    success = True
    errs = []
    for k, v in settings_dict.items():
        ok = update_setting(k, v)
        if not ok:
            success = False
            errs.append(k)
    if success:
        return True, "Success"
    return False, f"Failed to update fields: {', '.join(errs)}"

# ----------------- REVIEWS TABLE OPERATIONS -----------------

def get_reviews():
    """Fetches all client reviews from Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/reviews?select=*&order=id.desc"
    try:
        res = requests.get(url, headers=get_headers())
        if res.status_code == 200:
            return [SupabaseRow(item) for item in res.json()]
        print(f"Supabase get_reviews error: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"Failed to fetch reviews: {e}")
    return []

def insert_review(name, role_or_company, content, rating):
    """Persists a new client review."""
    url = f"{SUPABASE_URL}/rest/v1/reviews"
    payload = {
        "name": name,
        "role_or_company": role_or_company,
        "content": content,
        "rating": int(rating)
    }
    try:
        res = requests.post(url, json=payload, headers=get_headers())
        if res.status_code in (200, 201):
            return True, "Success"
        if res.status_code == 404:
            return False, "Table 'reviews' does not exist in Supabase (404). Please execute the setup SQL script in your Supabase Dashboard SQL Editor first."
        return False, f"Supabase error {res.status_code}: {res.text}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def delete_review(review_id):
    """Deletes a review by ID."""
    url = f"{SUPABASE_URL}/rest/v1/reviews"
    params = {
        "id": f"eq.{review_id}"
    }
    try:
        res = requests.delete(url, headers=get_headers(), params=params)
        if res.status_code in (200, 201, 204):
            return True, "Success"
        if res.status_code == 404:
            return False, "Table 'reviews' does not exist in Supabase (404). Please execute the setup SQL script in your Supabase Dashboard SQL Editor first."
        return False, f"Supabase error {res.status_code}: {res.text}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"
