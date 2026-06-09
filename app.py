from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
import smtplib
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
import database

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default-session-secret-key-12345').strip().strip('"').strip("'")

# Paths & File Upload Setup
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Mail & Admin Configuration
GMAIL_USER = os.environ.get('GMAIL_USER', 'aloksharma.creative@gmail.com').strip().strip('"').strip("'")
GMAIL_PASS = os.environ.get('GMAIL_PASS', '').strip().strip('"').strip("'")  # Set Gmail App Password here
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123').strip().strip('"').strip("'")

def send_notification_email(subject, body, recipient=GMAIL_USER):
    """Sends a notification email. Logs to console and sends via SMTP if GMAIL_PASS is configured."""
    # Always print email to console for local debugging and automated testing
    print("\n" + "="*50)
    print(f" [EMAIL SENDING LOG] ".center(50, "="))
    print(f"Subject: {subject}")
    print(f"To: {recipient}")
    print(f"Body:\n{body}")
    print("="*50 + "\n")
    
    if not GMAIL_PASS:
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, recipient, msg.as_string())
        server.quit()
        print(f"Notification email successfully sent to {recipient}!")
        return True
    except Exception as e:
        print(f"Failed to send email via SMTP: {e}")
        return False

def get_video_embed(url):
    """Parses a video URL and returns a tuple of (type, embed_or_source_url)."""
    if not url:
        return None, None
        
    url = url.strip()
    
    # Direct video links (MP4, WebM, Ogg, MOV)
    if url.lower().endswith(('.mp4', '.webm', '.ogg', '.mov')) or '/static/uploads/' in url:
        return 'direct', url
        
    # YouTube URL parsing
    if 'youtube.com' in url or 'youtu.be' in url:
        video_id = None
        if 'youtu.be' in url:
            video_id = url.split('/')[-1].split('?')[0]
        elif 'youtube.com/embed/' in url:
            video_id = url.split('/embed/')[-1].split('?')[0]
        elif 'v=' in url:
            video_id = url.split('v=')[-1].split('&')[0]
        
        if video_id:
            return 'youtube', f"https://www.youtube.com/embed/{video_id}"
            
    # Vimeo URL parsing
    if 'vimeo.com' in url:
        video_id = None
        if 'player.vimeo.com/video/' in url:
            video_id = url.split('/video/')[-1].split('?')[0]
        else:
            video_id = url.split('/')[-1].split('?')[0]
            
        if video_id:
            return 'vimeo', f"https://player.vimeo.com/video/{video_id}"
            
    return 'other', url

def save_cropped_image(data_url):
    """Decodes base64 data url and uploads it directly to Supabase Storage, with local disk fallback."""
    if not data_url or not data_url.startswith("data:image"):
        return None
    try:
        header, encoded = data_url.split(",", 1)
        data = base64.b64decode(encoded)
        import time
        filename = f"{int(time.time())}_cropped_cover.jpg"
        
        # 1. Try to upload to Supabase Storage
        public_url = database.upload_to_supabase_storage(data, filename, "image/jpeg")
        if public_url:
            return public_url
            
        # 2. Fallback to local storage if bucket upload fails
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        with open(filepath, "wb") as f:
            f.write(data)
        return f"/static/uploads/{filename}"
    except Exception as e:
        print(f"Error saving cropped image: {e}")
        return None

# Default settings values fallback
DEFAULT_SETTINGS = {
    'designer_name': 'Alok Sharma',
    'designer_role': 'UI/UX & Graphic Designer',
    'hero_headline': 'Designing Experiences. Creating Impact.',
    'hero_description': 'I create intuitive digital experiences, meaningful brands, and visually compelling designs that help businesses grow.',
    'hero_image_url': 'https://uxmagic.blob.core.windows.net/user/6a25a369277cb05ad3d0b425/project-assets/6a25f802dabb320111e4b8ed/work_pfpwide-1780873234357-bq8w5hzew.jpg',
    'about_heading': 'Hi, I\'m Alok Sharma.',
    'about_bio_p1': 'I\'m a passionate UI/UX and Graphic Designer based in Delhi, India, with over 5 years of experience crafting digital products that people love to use.',
    'about_bio_p2': 'My journey in design started with a fascination for how visual elements communicate stories. Over the years, I\'ve transitioned from purely graphic design to focusing deeply on user experience, realizing that the best designs are those that solve real problems seamlessly.',
    'about_bio_p3': 'I believe in a research-driven approach where aesthetics meet functionality. Whether I\'m designing a complex SaaS dashboard or a vibrant brand identity, my goal is always to create an emotional connection between the product and the user.',
    'about_quote': 'Good design is not just what it looks like, it\'s how it works and how it makes people feel.',
    'about_image_url': 'https://uxmagic.blob.core.windows.net/user/6a25a369277cb05ad3d0b425/project-assets/6a25f802dabb320111e4b8ed/work_pfpwide-1780873234357-bq8w5hzew.jpg',
    'stats_experience': '1+',
    'stats_projects': '10+',
    'stats_clients': '6+',
    'cta_heading': 'Have a Project in Mind?',
    'contact_email': 'aloksharma.creative@gmail.com',
    'contact_location': 'Delhi, India',
    'social_linkedin': '#',
    'social_dribbble': '#',
    'social_instagram': '#',
    'social_twitter': '#'
}

# Custom context processor to pass variables globally
@app.context_processor
def inject_global_vars():
    # Load settings from DB
    db_settings = database.get_settings_dict()
    # Merge with default fallback dictionary
    merged_settings = DEFAULT_SETTINGS.copy()
    merged_settings.update(db_settings)
    return {
        'admin_logged_in': session.get('admin_logged_in', False),
        'get_video_embed': get_video_embed,
        'settings': merged_settings
    }

# ----------------- CLIENT-FACING ROUTES -----------------

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/')
def home():
    """Serves the main landing page, listing selected projects and reviews."""
    all_projects = database.get_projects()
    case_studies = [p for p in all_projects if p.get('is_featured_case_study')]
    projects = all_projects[:6]
    reviews = database.get_reviews()
    return render_template('home.html', projects=projects, case_studies=case_studies, reviews=reviews)

@app.route('/projects')
def projects_list():
    """Serves the View All Projects page, supports filtering by category."""
    category = request.args.get('category', 'All')
    projects = database.get_projects(category=category)
    return render_template('all_projects.html', projects=projects, active_category=category)

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    """Serves the Project Case Study / Detail page."""
    project = database.get_project(project_id)
    if not project:
        flash("Project not found.", "error")
        return redirect(url_for('home'))
        
    # Deserialize media gallery URLs
    import json
    if project and project.get('media_gallery'):
        try:
            project['media_gallery_list'] = json.loads(project['media_gallery'])
        except Exception:
            project['media_gallery_list'] = []
    elif project:
        project['media_gallery_list'] = []
        
    # Fetch other projects for footer recommendations
    all_projects = database.get_projects()
    import random
    other_projects = [p for p in all_projects if p.get('id') != project_id]
    if len(other_projects) > 3:
        other_projects = random.sample(other_projects, 3)
        
    return render_template('project_detail.html', project=project, other_projects=other_projects)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Serves the contact page and processes email submissions."""
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        if not first_name or not email or not subject or not message:
            flash("Please fill in all required fields.", "error")
            return redirect(url_for('contact'))
            
        # 1. Save to Supabase database
        success, err_msg = database.insert_message(first_name, last_name, email, subject, message)
        if not success:
            flash(f"Error saving message: {err_msg}", "error")
            return redirect(url_for('contact'))
            
        # 2. Trigger notification email
        email_body = f"New message from your portfolio site:\n\nName: {first_name} {last_name}\nEmail: {email}\nSubject: {subject}\n\nMessage:\n{message}"
        send_notification_email(f"Portfolio Message: {subject}", email_body)
        
        flash("Your message was sent successfully! I will get back to you shortly.", "success")
        return redirect(url_for('contact'))
        
    return render_template('contact.html')

@app.route('/hire', methods=['GET', 'POST'])
def hire():
    """Processes project inquiries from the Hire Me page."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        company = request.form.get('company', '').strip()
        website = request.form.get('website', '').strip()
        selected_services = request.form.getlist('services')
        description = request.form.get('description', '').strip()
        budget = request.form.get('budget', '').strip()
        timeline = request.form.get('timeline', '').strip()
        
        if not name or not email or not description or not budget:
            flash("Please fill in all required fields.", "error")
            return redirect(url_for('hire'))
            
        services_str = ", ".join(selected_services)
        
        # 1. Save to Supabase database
        success, err_msg = database.insert_hire(name, email, company, website, services_str, description, budget, timeline)
        if not success:
            flash(f"Error saving inquiry: {err_msg}", "error")
            return redirect(url_for('hire'))
            
        # 2. Trigger notification email
        email_body = (
            f"New Hire Me Inquiry:\n\n"
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Company: {company}\n"
            f"Website: {website}\n"
            f"Services Needed: {services_str}\n"
            f"Budget: {budget}\n"
            f"Timeline: {timeline}\n\n"
            f"Project Details:\n{description}"
        )
        send_notification_email(f"New Project Inquiry: {name}", email_body)
        
        flash("Your project inquiry has been submitted! I look forward to working with you.", "success")
        return redirect(url_for('hire'))
        
    return render_template('hire_me.html')

@app.route('/book', methods=['GET', 'POST'])
def book():
    """Handles discovery call scheduling."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        booking_date = request.form.get('booking_date', '').strip()
        booking_time = request.form.get('booking_time', '').strip()
        
        if not name or not email or not booking_date or not booking_time:
            flash("Please provide all booking details.", "error")
            return redirect(url_for('book'))
            
        # 1. Save to Supabase database
        success, err_msg = database.insert_booking(name, email, booking_date, booking_time)
        if not success:
            flash(f"Error saving booking: {err_msg}", "error")
            return redirect(url_for('book'))
            
        # 2. Trigger notification email to designer
        email_body = f"A discovery call has been booked!\n\nName: {name}\nEmail: {email}\nDate: {booking_date}\nTime: {booking_time}"
        send_notification_email(f"Call Booked: {booking_date} @ {booking_time}", email_body)
        
        # 3. Send confirmation email to client
        client_body = f"Hi {name},\n\nThis is to confirm your Discovery Call booking with Alok Sharma.\n\nDate: {booking_date}\nTime: {booking_time}\nPlatform: Google Meet\n\nI look forward to speaking with you!"
        send_notification_email(f"Call Confirmed: Discovery Call with Alok Sharma", client_body, recipient=email)
        
        flash("Discovery call booked successfully! A confirmation email has been sent.", "success")
        return redirect(url_for('book'))
        
    return render_template('book_call.html')

# ----------------- ADMIN PORTAL ROUTES -----------------

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Handles admin workspace authentication."""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        password = request.form.get('password')
        
        # Check if database has admin_password_hash setting
        db_settings = database.get_settings_dict()
        hashed_password = db_settings.get('admin_password_hash')
        
        if hashed_password:
            # Check using secure hash
            is_valid = check_password_hash(hashed_password, password)
        else:
            # Fallback to plain text check from environment
            is_valid = (password == ADMIN_PASSWORD)
            
        if is_valid:
            session['admin_logged_in'] = True
            flash("Logged in successfully.", "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid password.", "error")
            
    return render_template('admin_login.html')

@app.route('/admin/forgot-password', methods=['GET', 'POST'])
def admin_forgot_password():
    """Handles generating and emailing password reset tokens."""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if not email:
            flash("Please enter your email address.", "error")
            return redirect(url_for('admin_forgot_password'))
            
        # Get configured admin emails
        db_settings = database.get_settings_dict()
        contact_email = db_settings.get('contact_email', '').strip().lower()
        gmail_user = GMAIL_USER.strip().lower()
        submitted_email = email.lower()
        
        is_authorized = False
        if submitted_email == gmail_user:
            is_authorized = True
        elif contact_email and submitted_email == contact_email:
            is_authorized = True
            
        if is_authorized:
            # Generate timed token
            serializer = URLSafeTimedSerializer(app.secret_key)
            token = serializer.dumps(submitted_email, salt='admin-password-reset-salt')
            
            # Generate absolute reset URL
            reset_url = url_for('admin_reset_password', token=token, _external=True)
            
            subject = "Password Reset Request - Portfolio Workspace"
            body = (
                f"Hi Admin,\n\n"
                f"We received a request to reset the password for your portfolio workspace.\n\n"
                f"Please click the link below to reset your password. This link is valid for 15 minutes:\n"
                f"{reset_url}\n\n"
                f"If you did not request a password reset, please ignore this email and your password will remain unchanged.\n\n"
                f"Best regards,\n"
                f"Portfolio System"
            )
            
            send_notification_email(subject, body, recipient=email)
            flash("A password reset link has been sent to your email address.", "success")
            return redirect(url_for('admin_login'))
        else:
            flash("This email address is not authorized.", "error")
            
    return render_template('admin_forgot_password.html')

@app.route('/admin/reset-password/<token>', methods=['GET', 'POST'])
def admin_reset_password(token):
    """Handles verifying reset tokens and saving new passwords."""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
        
    serializer = URLSafeTimedSerializer(app.secret_key)
    try:
        email = serializer.loads(token, salt='admin-password-reset-salt', max_age=900)  # 15 minutes expiration
    except Exception:
        flash("The password reset link is invalid or has expired.", "error")
        return redirect(url_for('admin_forgot_password'))
        
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template('admin_reset_password.html')
            
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template('admin_reset_password.html')
            
        hashed_password = generate_password_hash(password)
        success = database.save_setting('admin_password_hash', hashed_password)
        
        if success:
            flash("Your password has been reset successfully. Please log in.", "success")
            return redirect(url_for('admin_login'))
        else:
            flash("Failed to update password in database.", "error")
            
    return render_template('admin_reset_password.html')

@app.route('/admin/logout')
def admin_logout():
    """Logs the admin out."""
    session.pop('admin_logged_in', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('home'))

def login_required(f):
    """Decorator to require admin authentication on routes."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash("Please log in to access this page.", "error")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@login_required
def admin_dashboard():
    """Admin control panel displaying all content and stats."""
    projects = database.get_projects()
    messages = database.get_messages()
    hires = database.get_hires()
    bookings = database.get_bookings()
    reviews = database.get_reviews()
    return render_template('admin_dashboard.html', 
                           projects=projects, 
                           messages=messages, 
                           hires=hires, 
                           bookings=bookings,
                           reviews=reviews)

@app.route('/admin/project/new', methods=['GET', 'POST'])
@login_required
def project_new():
    """Handles adding a new project to the portfolio."""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        details = request.form.get('details', '').strip()
        live_url = request.form.get('live_url', '#').strip()
        github_url = request.form.get('github_url', '#').strip()
        
        # Image Upload/Crop Handling
        image_url = ''
        original_image_url = ''
        media_gallery_urls = []
        
        # Process multiple files from unified input
        files = request.files.getlist('project_media')
        import mimetypes
        for file in files:
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file_data = file.read()
                file.seek(0)
                
                mime_type, _ = mimetypes.guess_type(filename)
                if not mime_type:
                    if filename.lower().endswith(('.mp4', '.webm', '.ogg', '.mov')):
                        mime_type = "video/mp4"
                    else:
                        mime_type = "image/jpeg"
                        
                import time
                timestamp = int(time.time())
                unique_filename = f"{timestamp}_{filename}"
                
                public_url = database.upload_to_supabase_storage(file_data, unique_filename, mime_type)
                if not public_url:
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                    public_url = f"/static/uploads/{unique_filename}"
                    
                media_gallery_urls.append(public_url)
                if not original_image_url and mime_type.startswith("image/"):
                    original_image_url = public_url
                    
        # Check if cropped data is sent
        cropped_image_data = request.form.get('cropped_image_data', '').strip()
        if cropped_image_data:
            image_url = save_cropped_image(cropped_image_data)
        else:
            if original_image_url:
                image_url = original_image_url
            elif media_gallery_urls:
                image_url = media_gallery_urls[0]
                
        import json
        media_gallery_json = json.dumps(media_gallery_urls)
            
        if not title or not category:
            flash("Title and Category are required.", "error")
            return redirect(url_for('project_new'))
            
        # Case Study Extra Fields
        is_featured_case_study = request.form.get('is_featured_case_study') == 'true'
        challenge = request.form.get('challenge', '').strip()
        solution = request.form.get('solution', '').strip()
        metric1_value = request.form.get('metric1_value', '').strip()
        metric1_label = request.form.get('metric1_label', '').strip()
        metric2_value = request.form.get('metric2_value', '').strip()
        metric2_label = request.form.get('metric2_label', '').strip()
            
        success, err_msg = database.insert_project(
            title, category, image_url, description, details, live_url, github_url, None,
            challenge=challenge, solution=solution,
            metric1_value=metric1_value, metric1_label=metric1_label,
            metric2_value=metric2_value, metric2_label=metric2_label,
            is_featured_case_study=is_featured_case_study,
            original_image_url=original_image_url,
            media_gallery=media_gallery_json
        )
        if not success:
            flash(f"Upload failed: {err_msg}", "error")
            return redirect(url_for('project_new'))
            
        if "Warning:" in err_msg:
            flash(err_msg, "warning")
        else:
            flash("Project uploaded successfully!", "success")
        return redirect(url_for('admin_dashboard'))
        
    return render_template('admin_project_form.html', project=None)

@app.route('/admin/project/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def project_edit(project_id):
    """Handles updating project details."""
    project = database.get_project(project_id)
    
    if not project:
        flash("Project not found.", "error")
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        details = request.form.get('details', '').strip()
        live_url = request.form.get('live_url', '#').strip()
        github_url = request.form.get('github_url', '#').strip()
        
        # Image Upload/Crop Handling
        image_url = project.get('image_url') or ''
        original_image_url = project.get('original_image_url') or project.get('image_url') or ''
        
        # Read existing gallery URLs kept
        existing_gallery_json = request.form.get('existing_gallery_urls', '[]')
        import json
        try:
            media_gallery_urls = json.loads(existing_gallery_json)
        except Exception:
            media_gallery_urls = []
            
        # Process any newly uploaded files
        files = request.files.getlist('project_media')
        import mimetypes
        new_gallery_urls = []
        for file in files:
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file_data = file.read()
                file.seek(0)
                
                mime_type, _ = mimetypes.guess_type(filename)
                if not mime_type:
                    if filename.lower().endswith(('.mp4', '.webm', '.ogg', '.mov')):
                        mime_type = "video/mp4"
                    else:
                        mime_type = "image/jpeg"
                        
                import time
                timestamp = int(time.time())
                unique_filename = f"{timestamp}_{filename}"
                
                public_url = database.upload_to_supabase_storage(file_data, unique_filename, mime_type)
                if not public_url:
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                    public_url = f"/static/uploads/{unique_filename}"
                    
                new_gallery_urls.append(public_url)
                if not original_image_url and mime_type.startswith("image/"):
                    original_image_url = public_url
                    
        media_gallery_urls.extend(new_gallery_urls)
        
        # Check if cropped cover image was sent
        cropped_image_data = request.form.get('cropped_image_data', '').strip()
        if cropped_image_data:
            image_url = save_cropped_image(cropped_image_data)
        else:
            if not image_url:
                if original_image_url:
                    image_url = original_image_url
                elif media_gallery_urls:
                    image_url = media_gallery_urls[0]
                    
        media_gallery_json = json.dumps(media_gallery_urls)
                
        if not title or not category:
            flash("Title and Category are required.", "error")
            return redirect(url_for('project_edit', project_id=project_id))
            
        # Case Study Extra Fields
        is_featured_case_study = request.form.get('is_featured_case_study') == 'true'
        challenge = request.form.get('challenge', '').strip()
        solution = request.form.get('solution', '').strip()
        metric1_value = request.form.get('metric1_value', '').strip()
        metric1_label = request.form.get('metric1_label', '').strip()
        metric2_value = request.form.get('metric2_value', '').strip()
        metric2_label = request.form.get('metric2_label', '').strip()
            
        success, err_msg = database.update_project(
            project_id, title, category, image_url, description, details, live_url, github_url, project.get('video_url'),
            challenge=challenge, solution=solution,
            metric1_value=metric1_value, metric1_label=metric1_label,
            metric2_value=metric2_value, metric2_label=metric2_label,
            is_featured_case_study=is_featured_case_study,
            original_image_url=original_image_url,
            media_gallery=media_gallery_json
        )
        if not success:
            flash(f"Update failed: {err_msg}", "error")
            return redirect(url_for('project_edit', project_id=project_id))
            
        if "Warning:" in err_msg:
            flash(err_msg, "warning")
        else:
            flash("Project updated successfully!", "success")
        return redirect(url_for('admin_dashboard'))
        
    if project:
        import json
        try:
            project['media_gallery_list'] = json.loads(project.get('media_gallery') or '[]')
        except Exception:
            project['media_gallery_list'] = []
    return render_template('admin_project_form.html', project=project)

@app.route('/admin/project/delete/<int:project_id>', methods=['POST'])
@login_required
def project_delete(project_id):
    """Handles deleting a project."""
    success, err_msg = database.delete_project(project_id)
    if not success:
        flash(f"Delete failed: {err_msg}", "error")
    else:
        flash("Project deleted successfully.", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/projects/reorder', methods=['POST'])
@login_required
def projects_reorder():
    """Handles updating project sorting order via drag-and-drop AJAX request."""
    data = request.get_json() or {}
    project_ids = data.get('project_ids', [])
    
    if not project_ids:
        return jsonify({"success": False, "message": "No project IDs provided."}), 400
        
    success_count = 0
    errors = []
    
    # Loop and update sort_order for each project in order
    for index, project_id in enumerate(project_ids):
        success, err_msg = database.update_project_order(project_id, index)
        if success:
            success_count += 1
        else:
            errors.append(f"Project {project_id}: {err_msg}")
            
    if success_count == len(project_ids):
        return jsonify({"success": True, "message": "Project order updated successfully!"})
    elif success_count > 0:
        return jsonify({"success": True, "message": f"Updated {success_count} projects, but encountered errors: {', '.join(errors)}"}), 207
    else:
        return jsonify({"success": False, "message": f"Failed to update project order: {', '.join(errors)}"}), 500

def format_social_url(url):
    """Ensures social URLs start with http:// or https:// if they look like domain names."""
    if not url or url.strip() in ('', '#'):
        return '#'
    url = url.strip()
    if not (url.startswith('http://') or url.startswith('https://')):
        if '.' in url:
            return 'https://' + url
    return url

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    """Handles editing site-wide statistics and social links."""
    if request.method == 'POST':
        # Collect only allowable settings fields
        updated_fields = {
            'stats_experience': request.form.get('stats_experience', '').strip(),
            'stats_projects': request.form.get('stats_projects', '').strip(),
            'stats_clients': request.form.get('stats_clients', '').strip(),
            'social_linkedin': format_social_url(request.form.get('social_linkedin', '')),
            'social_dribbble': format_social_url(request.form.get('social_dribbble', '')),
            'social_instagram': format_social_url(request.form.get('social_instagram', '')),
            'social_twitter': format_social_url(request.form.get('social_twitter', '')),
        }
        
        # Validation
        if not updated_fields['stats_experience'] or not updated_fields['stats_projects'] or not updated_fields['stats_clients']:
            flash("All statistics counters are required.", "error")
            return redirect(url_for('admin_settings'))
            
        success, err_msg = database.update_settings(updated_fields)
        if not success:
            flash(f"Settings update failed: {err_msg}", "error")
            return redirect(url_for('admin_settings'))
            
        flash("Site settings updated successfully!", "success")
        return redirect(url_for('admin_dashboard'))
        
    return render_template('admin_settings.html')

@app.errorhandler(Exception)
def handle_exception(e):
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException):
        return e
    import traceback
    tb = traceback.format_exc()
    return f"<h2>500 Internal Server Error (Traceback)</h2><pre>{tb}</pre>", 500

@app.errorhandler(413)
def request_entity_too_large(error):
    flash("The uploaded file is too large! Maximum allowed size is 16MB. Please compress the image or use a URL.", "error")
    return redirect(request.referrer or url_for('admin_dashboard'))

@app.route('/submit-review', methods=['POST'])
def submit_review():
    """Handles new client review submissions."""
    name = request.form.get('name', '').strip()
    role_or_company = request.form.get('role_or_company', '').strip()
    content = request.form.get('content', '').strip()
    rating = request.form.get('rating', '5')
    
    if not name or not content:
        flash("Name and Review content are required.", "error")
        return redirect(url_for('home', _anchor='reviews'))
        
    try:
        rating_int = int(rating)
        if rating_int < 1 or rating_int > 5:
            rating_int = 5
    except ValueError:
        rating_int = 5
        
    success, err_msg = database.insert_review(name, role_or_company, content, rating_int)
    if not success:
        flash(f"Error saving review: {err_msg}", "error")
    else:
        flash("Thank you for your feedback! Your review has been published.", "success")
        
    return redirect(url_for('home', _anchor='reviews'))

@app.route('/admin/review/delete/<int:review_id>', methods=['POST'])
@login_required
def review_delete(review_id):
    """Handles deleting a client review from the admin dashboard."""
    success, err_msg = database.delete_review(review_id)
    if not success:
        flash(f"Delete failed: {err_msg}", "error")
    else:
        flash("Review deleted successfully.", "success")
    return redirect(url_for('admin_dashboard'))

# ----------------- SERVER RUN -----------------

if __name__ == '__main__':
    app.run(debug=True, port=5000)
