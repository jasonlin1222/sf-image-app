import os
from flask import Flask, flash, json, jsonify, request, redirect, url_for, send_from_directory
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename

# config
app = Flask(__name__)
UPLOAD_FOLDER = './image'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
cors = CORS(app)
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
    body = request.args.get('query', "dog")
    return jsonify({'success': 1, 'image_url': body})


@app.route('/getfile', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route('/uploads/<name>', methods=['GET'])
def download_file(name):
    return send_from_directory(app.config['UPLOAD_FOLDER'], name)
