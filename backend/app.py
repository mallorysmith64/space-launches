import os
from flask import Flask, jsonify, request, send_from_directory, render_template_string, session, redirect, url_for
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'secret-key')  # Change this in production!

# Define the directory where your images are stored
IMAGES_DIR = os.path.join(app.root_path, 'images')

# Define templates to fix undefined variables
LOGIN_TEMPLATE = """
<!doctype html>
<title>Admin Login</title>
<h2>Admin Login</h2>
{% if error %}<p style="color: red;">{{ error }}</p>{% endif %}
<form method="post">
    <p><input type="text" name="username" placeholder="Username" required></p>
    <p><input type="password" name="password" placeholder="Password" required></p>
    <p><input type="submit" value="Login"></p>
</form>
"""

DASHBOARD_TEMPLATE = """
<!doctype html>
<title>Admin Dashboard</title>
<h2>Welcome to the Admin Dashboard</h2>
<p>You are logged in successfully.</p>
<p><a href="{{ url_for('admin_logout') }}">Logout</a></p>
"""

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    """Admin login page"""
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple authentication (replace with real authentication in production)
        if username == 'admin' and password == 'password':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Invalid username or password'
            return render_template_string(LOGIN_TEMPLATE, error=error)
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route("/admin/dashboard")
def admin_dashboard():
    """Admin dashboard (protected route)"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route("/admin/logout")
def admin_logout():
    """Logout"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)