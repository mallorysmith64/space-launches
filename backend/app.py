import os
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)

# Define the directory where your images are stored
IMAGES_DIR = os.path.join(app.root_path, 'images')

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/images/<filename>")
def get_image(filename):
    return send_from_directory(IMAGES_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)