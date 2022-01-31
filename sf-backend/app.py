from flask import Flask, json, jsonify, request
from flask_cors import CORS, cross_origin
import os

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/")
def index():
    return "This is the api for sf-image-app"

@app.route("/query", methods=['GET'])
def query():
    body = request.args.get('query', "dog")
    return jsonify({'success':1, 'image_url':body})