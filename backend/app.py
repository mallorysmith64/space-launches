import os
from flask import Flask, jsonify, request, session, redirect, url_for, send_from_directory
from flask_cors import CORS
from functools import wraps
from werkzeug.utils import secure_filename
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', '1331928c7a8e12abf1899118ad6e5fd885a27f9c66439bbb030a2792ee4900d3')

# Configure upload folder and allowed file types
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'src', 'images')
ALLOWED_EXTENSIONS = {'jpeg', 'jpg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Enable CORS with proper configuration for Vue dev server
CORS(
    app,
    resources={r"/api/admin*": {"origins": ["http://localhost:5173", "http://localhost:5000", "http://localhost:3000"]}},
    supports_credentials=True,
    allow_headers=['Content-Type', 'Authorization'],
    methods=['GET', 'POST', 'OPTIONS']
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
    # Remove special characters and convert to lowercase
    safe_title = "".join(c if c.isalnum() or c.isspace() else "" for c in title)
    # Replace spaces with hyphens and remove multiple hyphens
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
    return os.path.join(os.path.dirname(__file__), 'src', 'data', 'spacex-mission-data.json')

def update_mission_json(mission_id, new_image_path):
    """
    Update the mission's image path in the JSON data file
    
    Args:
        mission_id: The mission ID to find and update
        new_image_path: The new image path to set
    
    Returns:
        True if successful, False otherwise
    """
    try:
        json_path = get_json_path()
        
        # Read the JSON file
        with open(json_path, 'r', encoding='utf-8') as f:
            missions = json.load(f)
        
        # Find and update the mission
        updated = False
        for mission in missions:
            if mission.get('id') == mission_id:
                mission['image'] = new_image_path
                updated = True
                break
        
        if not updated:
            print(f"Mission with id {mission_id} not found in JSON")
            return False
        
        # Write back to JSON file
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(missions, f, indent=2, ensure_ascii=False)
        
        print(f"Updated mission {mission_id} with new image path: {new_image_path}")
        return True
    
    except Exception as e:
        print(f"Error updating mission JSON: {e}")
        return False

@app.route("/")
def hello_world():
    return jsonify({'message': 'Hello, World!'})

# Serve static images
@app.route('/static/images/<filename>')
def serve_image(filename):
    """Serve images from the upload folder"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/api/admin/login", methods=["GET", "POST"])
def admin_login():
    """Admin login endpoint"""
    if request.method == "POST":
        # Handle both JSON and form-encoded requests
        if request.is_json:
            data = request.get_json()
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
        else:
            # Fallback to form data
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
        
        # Simple authentication (REPLACE with real authentication in production)
        if username == 'admin' and password == 'password':
            session['admin_logged_in'] = True
            session.permanent = True
            
            # Always return JSON for consistency with fetch requests
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
    
    # GET request - just return success if already logged in
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
    """
    Handle image upload for missions
    
    Expected form data:
    - file: image file (JPEG only)
    - missionId: mission ID
    - missionTitle: mission title (used to generate filename)
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'Cannot upload image'
            }), 400
        
        file = request.files['file']
        mission_title = request.form.get('missionTitle', '')
        
        # Check if file is empty
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'Cannot upload image'
            }), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'status': 'error',
                'message': 'Cannot upload image'
            }), 400
        
        # Check file size (Flask won't let it exceed MAX_CONTENT_LENGTH)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'status': 'error',
                'message': 'Cannot upload image'
            }), 400
        
        # Delete old image if exists
        if mission_title:
            delete_old_image(mission_title)
        
        # Generate safe filename from mission title
        filename = generate_filename_from_title(mission_title)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file
        file.save(filepath)
        
        # Return the relative path for the frontend to use
        image_path = f'/static/images/{filename}'
        
        # Update the mission JSON with the new image path
        mission_id = request.form.get('missionId', '')
        if mission_id:
            json_updated = update_mission_json(mission_id, image_path)
            if not json_updated:
                print(f"Warning: JSON update failed for mission {mission_id}, but image was saved")
        
        return jsonify({
            'status': 'success',
            'message': 'Image successfully updated',
            'imagePath': image_path,
            'filename': filename
        }), 200
    
    except Exception as e:
        print(f"Error uploading image: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Cannot upload image'
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

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    # Only use debug mode in development
    app.run(debug=True, port=5000, host='127.0.0.1')