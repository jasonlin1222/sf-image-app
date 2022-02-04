import os
from flask import Flask, json, jsonify, request, redirect, send_from_directory
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename

# config
app = Flask(__name__)
UPLOAD_FOLDER = './image'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
cors = CORS(app)
app.secret_key="12345"
app.config['CORS_HEADER'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# helper function


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# app


@app.route("/")
def index():
    return "This is the api for sf-image-app"


@app.route("/query", methods=['GET'])
def query():
    body = request.args.get('query', "")
    return jsonify({'success': 1, 'image_url': body})


@app.route('/getfile', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': 0, 'err_msg': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success':0, 'err_msg': 'No selected file'})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'success':1})


@app.route('/uploads/<name>', methods=['GET'])
def download_file(name):
    return send_from_directory(app.config['UPLOAD_FOLDER'], name)
