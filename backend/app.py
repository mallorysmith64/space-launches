import os
from flask import Flask, jsonify, request, session, redirect, url_for
from flask_cors import CORS
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Enable CORS with proper configuration for Vue dev server
CORS(
    app,
    resources={r"/admin*": {"origins": ["http://localhost:5000", "http://localhost:3000", "http://localhost:5173"]}},
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

@app.route("/")
def hello_world():
    return jsonify({'message': 'Hello, World!'})

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    """Admin login endpoint"""
    if request.method == "POST":
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

@app.route("/admin/dashboard", methods=["GET"])
@login_required
def admin_dashboard():
    """Admin dashboard (protected route)"""
    return jsonify({
        'status': 'success',
        'message': 'Welcome to the Admin Dashboard',
        'user': 'admin'
    }), 200

@app.route("/admin/logout", methods=["GET"])
def admin_logout():
    """Logout endpoint"""
    session.pop('admin_logged_in', None)
    return jsonify({
        'status': 'success',
        'message': 'Logged out successfully'
    }), 200

@app.route("/admin/status", methods=["GET"])
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