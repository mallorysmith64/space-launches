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
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'src', 'images')
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
    return os.path.join(os.path.dirname(__file__), '..', 'src', 'data', 'spacex-mission-data.json')

def update_mission_json(mission_id, new_image_path=None, new_title=None, new_description=None, new_date=None, new_rocket_type=None, new_mission_type=None):
    """
    Update the mission's image path, title, description, date, rocket type, and/or mission type in the JSON data file
    
    Args:
        mission_id: The mission ID to find and update
        new_image_path: The new image path to set (optional)
        new_title: The new mission title to set (optional)
        new_description: The new mission description to set (optional)
        new_date: The new mission date to set (optional)
        new_rocket_type: The new rocket type to set (optional)
        new_mission_type: The new mission type to set (optional)
    
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
        
        # Write back to JSON file
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
    Handle image upload and/or mission data updates
    
    Expected form data:
    - file: image file (JPEG only, optional)
    - missionId: mission ID (required)
    - missionTitle: original mission title (used to generate old filename for deletion)
    - newTitle: new mission title (optional)
    - newDescription: new mission description (optional)
    - newDate: new mission date (optional)
    - newRocketType: new rocket type (optional)
    - newMissionType: new mission type (optional)
    
    At least one of 'file', 'newTitle', 'newDescription', 'newDate', 'newRocketType', or 'newMissionType' must be provided.
    """
    try:
        mission_id = request.form.get('missionId', '').strip()
        mission_title = request.form.get('missionTitle', '').strip()
        new_title = request.form.get('newTitle', '').strip()
        new_description = request.form.get('newDescription', '').strip()
        new_date = request.form.get('newDate', '').strip()
        new_rocket_type = request.form.get('newRocketType', '').strip()
        new_mission_type = request.form.get('newMissionType', '').strip()
        
        # Validate that we have a mission ID
        if not mission_id:
            return jsonify({
                'status': 'error',
                'message': 'Mission ID is required'
            }), 400
        
        # Check if at least one update is being made
        has_file = 'file' in request.files and request.files['file'].filename != ''
        has_new_title = bool(new_title)
        has_new_description = bool(new_description)
        has_new_date = bool(new_date)
        has_new_rocket_type = bool(new_rocket_type)
        has_new_mission_type = bool(new_mission_type)
        
        if not has_file and not has_new_title and not has_new_description and not has_new_date and not has_new_rocket_type and not has_new_mission_type:
            return jsonify({
                'status': 'error',
                'message': 'At least one update (image, title, description, date, rocket type, or mission type) must be provided'
            }), 400
        
        image_path = None
        
        # Handle image upload if provided
        if has_file:
            file = request.files['file']
            
            # Validate file type
            if not allowed_file(file.filename):
                return jsonify({
                    'status': 'error',
                    'message': 'Only JPEG files are allowed'
                }), 400
            
            # Check file size (Flask won't let it exceed MAX_CONTENT_LENGTH)
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > MAX_FILE_SIZE:
                return jsonify({
                    'status': 'error',
                    'message': 'File size must be under 5MB'
                }), 400
            
            # Delete old image if exists
            if mission_title:
                delete_old_image(mission_title)
            
            # Use new title for filename if provided, otherwise use original title
            filename_title = new_title if new_title and new_title.strip() else mission_title
            
            # Generate safe filename from mission title
            filename = generate_filename_from_title(filename_title)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save the file
            file.save(filepath)
            
            # Return the relative path for the frontend to use (matches the
            # /src/images/... convention already used by every mission entry)
            image_path = f'/src/images/{filename}'
        
        # Update the mission JSON with the new values
        json_updated = update_mission_json(
            mission_id, 
            new_image_path=image_path if image_path else None, 
            new_title=new_title if new_title else None,
            new_description=new_description if new_description else None,
            new_date=new_date if new_date else None,
            new_rocket_type=new_rocket_type if new_rocket_type else None,
            new_mission_type=new_mission_type if new_mission_type else None
        )
        
        if not json_updated:
            print(f"Warning: JSON update failed for mission {mission_id}")
            # Still return success if file was saved, but let frontend know JSON update failed
            if has_file:
                return jsonify({
                    'status': 'warning',
                    'message': 'Image saved but database update failed',
                    'imagePath': image_path,
                    'filename': filename if has_file else None
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to update mission'
                }), 500
        
        return jsonify({
            'status': 'success',
            'message': 'Mission successfully updated',
            'imagePath': image_path,
            'filename': filename if has_file else None
        }), 200
    
    except Exception as e:
        print(f"Error updating mission: {e}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred while updating the mission'
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