import os
import uuid
from dotenv import load_dotenv
from flask import Flask, jsonify, request, session, send_from_directory, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
import json
from datetime import datetime

load_dotenv()

# Determine the static folder path (works both locally and in Docker)
# app.py is in backend/, so go up one level to project root, then into dist/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # project root
STATIC_FOLDER = os.path.join(PROJECT_ROOT, 'dist')

# Create Flask app WITHOUT Flask's automatic static route.
# static_folder=None disables Flask's built-in `/<path:filename>` static handler,
# which otherwise conflicts with our own catch-all SPA route below (serve_frontend)
# and swallows requests like /admin before they ever reach it.
app = Flask(__name__, static_folder=None)

# Fail fast if SECRET_KEY isn't set, rather than silently falling back to a
# hardcoded value that anyone reading the source code could use to forge sessions.
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError('SECRET_KEY environment variable is not set. Add it to your .env file.')
app.secret_key = SECRET_KEY

# Admin credentials: username is a plain env var, password is stored only as a hash.
# Generate the hash with: python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('yourpassword'))"
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD_HASH = os.environ.get('ADMIN_PASSWORD_HASH')
if not ADMIN_PASSWORD_HASH:
    raise RuntimeError('ADMIN_PASSWORD_HASH environment variable is not set. See the comment above for how to generate one.')

limiter = Limiter(app=app, key_func=get_remote_address, default_limits=[])

print(f"[DEBUG] BASE_DIR: {BASE_DIR}")
print(f"[DEBUG] STATIC_FOLDER: {STATIC_FOLDER}")
print(f"[DEBUG] Static folder exists: {os.path.exists(STATIC_FOLDER)}")
if os.path.exists(STATIC_FOLDER):
    print(f"[DEBUG] Static folder contents: {os.listdir(STATIC_FOLDER)[:5]}")

# Configure upload folder and allowed file types
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'src', 'images')
ALLOWED_EXTENSIONS = {'jpeg', 'jpg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Enable CORS - updated for production
CORS(
    app,
    resources={r"/api/*": {"origins": [
        "http://localhost:5173",      # Vite dev server
        "http://localhost:5000",      # Flask dev
        "http://localhost:3000",      # Alternative port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5000",
        "http://127.0.0.1:3000",
        os.environ.get('FRONTEND_URL', ''),  # Production frontend URL
    ]}},
    supports_credentials=True,
    allow_headers=['Content-Type', 'Authorization'],
    methods=['GET', 'POST', 'OPTIONS', 'PUT', 'DELETE']
)

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_filename_from_title(title):
    """
    Generate a safe filename from mission title
    Example: "Crew Dragon Resupply" -> "crew-dragon-resupply.jpeg"
    """
    safe_title = "".join(c if c.isalnum() or c.isspace() else "" for c in title)
    safe_title = "-".join(safe_title.split()).lower()
    return f"{safe_title}.jpeg"

def delete_old_image(mission_title):
    """Delete old image file if it exists"""
    try:
        filename = generate_filename_from_title(mission_title)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Deleted old image: {filename}")
    except Exception as e:
        print(f"Error deleting old image: {e}")

def get_json_path():
    """Get the path to the mission data JSON file"""
    return os.path.join(PROJECT_ROOT, 'src', 'data', 'spacex-mission-data.json')

def update_mission_json(mission_id, new_image_path=None, new_title=None, new_description=None, new_date=None, new_rocket_type=None, new_mission_type=None):
    """
    Update the mission's image path, title, description, date, rocket type, and/or mission type in the JSON data file
    """
    try:
        json_path = get_json_path()
        
        with open(json_path, 'r', encoding='utf-8') as f:
            missions = json.load(f)
        
        updated = False
        for mission in missions:
            if mission.get('id') == mission_id:
                if new_image_path:
                    mission['image'] = new_image_path
                if new_title:
                    mission['name'] = new_title
                if new_description:
                    mission['description'] = new_description
                if new_date:
                    mission['date'] = new_date
                if new_rocket_type:
                    mission['rocketName'] = new_rocket_type
                if new_mission_type:
                    mission['missionType'] = new_mission_type
                updated = True
                break
        
        if not updated:
            print(f"Mission with id {mission_id} not found in JSON")
            return False
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(missions, f, indent=2, ensure_ascii=False)
        
        updates = []
        if new_image_path:
            updates.append(f"image path: {new_image_path}")
        if new_title:
            updates.append(f"title: {new_title}")
        if new_description:
            updates.append(f"description: {new_description[:50]}...")
        if new_date:
            updates.append(f"date: {new_date}")
        if new_rocket_type:
            updates.append(f"rocket type: {new_rocket_type}")
        if new_mission_type:
            updates.append(f"mission type: {new_mission_type}")
        print(f"Updated mission {mission_id} with new {', '.join(updates)}")
        return True
    
    except Exception as e:
        print(f"Error updating mission JSON: {e}")
        return False

# ==================== API Routes ====================

@app.route("/api/admin/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def admin_login():
    """Admin login endpoint"""
    if request.method == "POST":
        if request.is_json:
            data = request.get_json()
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
        else:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()

        # Constant-shape check: always run check_password_hash so that
        # bad usernames don't return faster than bad passwords (timing).
        valid_username = username == ADMIN_USERNAME
        valid_password = check_password_hash(ADMIN_PASSWORD_HASH, password)

        if valid_username and valid_password:
            session['admin_logged_in'] = True
            session.permanent = True
            
            return jsonify({
                'status': 'success',
                'message': 'Login successful',
                'redirect': '/admin/dashboard'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid username or password'
            }), 401
    
    if session.get('admin_logged_in'):
        return jsonify({'status': 'success', 'message': 'Already logged in'}), 200
    
    return jsonify({'status': 'error', 'message': 'Not logged in'}), 401

@app.route("/api/admin/dashboard", methods=["GET"])
@login_required
def admin_dashboard():
    """Admin dashboard (protected route)"""
    return jsonify({
        'status': 'success',
        'message': 'Welcome to the Admin Dashboard',
        'user': 'admin'
    }), 200

@app.route("/api/admin/upload-image", methods=["POST"])
@login_required
def upload_image():
    """Handle image upload and/or mission data updates"""
    try:
        mission_id = request.form.get('missionId', '').strip()
        mission_title = request.form.get('missionTitle', '').strip()
        new_title = request.form.get('newTitle', '').strip()
        new_description = request.form.get('newDescription', '').strip()
        new_date = request.form.get('newDate', '').strip()
        new_rocket_type = request.form.get('newRocketType', '').strip()
        new_mission_type = request.form.get('newMissionType', '').strip()
        
        if not mission_id:
            return jsonify({
                'status': 'error',
                'message': 'Mission ID is required'
            }), 400
        
        new_image_path = None
        
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            
            if not allowed_file(file.filename):
                return jsonify({
                    'status': 'error',
                    'message': 'Only JPEG files are allowed'
                }), 400
            
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > MAX_FILE_SIZE:
                return jsonify({
                    'status': 'error',
                    'message': 'File size must be under 5MB'
                }), 400
            
            if mission_title:
                delete_old_image(mission_title)
            
            filename = generate_filename_from_title(new_title if new_title else mission_title)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            new_image_path = f'/src/images/{filename}'
        
        if not any([new_image_path, new_title, new_description, new_date, new_rocket_type, new_mission_type]):
            return jsonify({
                'status': 'error',
                'message': 'At least one field must be updated'
            }), 400
        
        success = update_mission_json(
            mission_id,
            new_image_path=new_image_path,
            new_title=new_title,
            new_description=new_description,
            new_date=new_date,
            new_rocket_type=new_rocket_type,
            new_mission_type=new_mission_type
        )
        
        if not success:
            return jsonify({
                'status': 'error',
                'message': 'Mission not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Mission successfully updated'
        }), 200
        
    except Exception as e:
        print(f"Error uploading image: {e}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred while updating the mission'
        }), 500

@app.route("/api/admin/create-mission", methods=["POST"])
@login_required
def create_mission():
    """Create a new mission with an uploaded image."""
    try:
        title = request.form.get('title', '').strip()
        date = request.form.get('date', '').strip()
        rocket_type = request.form.get('rocketType', '').strip()
        mission_type = request.form.get('missionType', '').strip()
        description = request.form.get('description', '').strip()

        missing_fields = []
        if not title:
            missing_fields.append('title')
        if not date:
            missing_fields.append('date')
        if not rocket_type:
            missing_fields.append('rocketType')
        if not mission_type:
            missing_fields.append('missionType')
        if not description:
            missing_fields.append('description')

        if missing_fields:
            return jsonify({
                'status': 'error',
                'message': f"Missing required field(s): {', '.join(missing_fields)}"
            }), 400

        if 'file' not in request.files or request.files['file'].filename == '':
            return jsonify({
                'status': 'error',
                'message': 'An image is required'
            }), 400

        file = request.files['file']

        if not allowed_file(file.filename):
            return jsonify({
                'status': 'error',
                'message': 'Only JPEG files are allowed'
            }), 400

        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'status': 'error',
                'message': 'File size must be under 5MB'
            }), 400

        filename = generate_filename_from_title(title)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if os.path.exists(filepath):
            return jsonify({
                'status': 'error',
                'message': 'A mission with a very similar title already has an image saved. Please use a more unique title.'
            }), 400

        file.save(filepath)
        image_path = f'/src/images/{filename}'

        new_mission = {
            'id': str(uuid.uuid4()),
            'name': title,
            'date': date,
            'description': description,
            'image': image_path,
            'rocketName': rocket_type,
            'missionType': mission_type
        }

        json_path = get_json_path()
        with open(json_path, 'r', encoding='utf-8') as f:
            missions = json.load(f)

        missions.insert(0, new_mission)

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(missions, f, indent=2, ensure_ascii=False)

        print(f"Created new mission: {title}")

        return jsonify({
            'status': 'success',
            'message': 'Mission successfully created',
            'mission': new_mission
        }), 201

    except Exception as e:
        print(f"Error creating mission: {e}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred while creating the mission'
        }), 500

@app.route("/api/admin/delete-mission", methods=["POST"])
@login_required
def delete_mission():
    """Delete a mission by ID."""
    try:
        data = request.get_json(silent=True) or {}
        mission_id = str(data.get('missionId', '')).strip()

        if not mission_id:
            return jsonify({
                'status': 'error',
                'message': 'Mission ID is required'
            }), 400

        json_path = get_json_path()
        with open(json_path, 'r', encoding='utf-8') as f:
            missions = json.load(f)

        mission_to_delete = None
        remaining_missions = []
        for mission in missions:
            if mission.get('id') == mission_id:
                mission_to_delete = mission
            else:
                remaining_missions.append(mission)

        if mission_to_delete is None:
            return jsonify({
                'status': 'error',
                'message': 'Mission not found'
            }), 404

        image_path = mission_to_delete.get('image', '')
        if image_path:
            filename = os.path.basename(image_path)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception as e:
                    print(f"Error deleting image file {filename}: {e}")

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(remaining_missions, f, indent=2, ensure_ascii=False)

        print(f"Deleted mission {mission_id}")

        return jsonify({
            'status': 'success',
            'message': 'Mission successfully deleted'
        }), 200

    except Exception as e:
        print(f"Error deleting mission: {e}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred while deleting the mission'
        }), 500

@app.route("/api/admin/logout", methods=["GET"])
def admin_logout():
    """Logout endpoint"""
    session.pop('admin_logged_in', None)
    return jsonify({
        'status': 'success',
        'message': 'Logged out successfully'
    }), 200

@app.route("/api/admin/status", methods=["GET"])
def admin_status():
    """Check authentication status"""
    if session.get('admin_logged_in'):
        return jsonify({'status': 'authenticated', 'message': 'User is logged in'}), 200
    return jsonify({'status': 'unauthenticated', 'message': 'User is not logged in'}), 401

@app.route('/static/images/<filename>')
def serve_image(filename):
    """Serve images from the upload folder"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ==================== Frontend Routes (SPA) ====================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """
    Serve Vue.js frontend files and handle SPA routing.
    All non-API routes are served index.html so Vue Router can handle them.
    """
    # If it's an API route, don't handle it here
    if path.startswith('api/'):
        return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404
    
    # Try to serve the file if it exists in the static folder
    file_path = os.path.join(STATIC_FOLDER, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(STATIC_FOLDER, path)
    
    # Otherwise, serve index.html (Vue Router will handle the route)
    index_path = os.path.join(STATIC_FOLDER, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(STATIC_FOLDER, 'index.html')
    
    # Debug: Frontend not found
    print(f"[ERROR] Frontend not found")
    print(f"[DEBUG] Static folder: {STATIC_FOLDER}")
    print(f"[DEBUG] Static folder exists: {os.path.exists(STATIC_FOLDER)}")
    if os.path.exists(STATIC_FOLDER):
        print(f"[DEBUG] Contents: {os.listdir(STATIC_FOLDER)}")
    
    return jsonify({
        'status': 'error', 
        'message': 'Frontend not found',
        'debug': {
            'static_folder': STATIC_FOLDER,
            'exists': os.path.exists(STATIC_FOLDER)
        }
    }), 404

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    # For Docker: runs on 0.0.0.0:5000
    # For development: use with Gunicorn in production
    app.run(debug=False, port=5000, host='0.0.0.0')