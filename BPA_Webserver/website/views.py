from flask import render_template, Blueprint, jsonify
from pymongo import MongoClient
import sys
sys.path.append('../')
from config import settings
views = Blueprint('views', __name__)

client = MongoClient(settings.mongodb_url)
db = client["BPA_DB"]
collection = db["InspectionData"]

@views.route('/')
def index():
    return render_template('home.html')

@views.route('/data')
def data():
    items = list(collection.find({}))
    for item in items:
        item['_id'] = str(item['_id'])  # Convert ObjectId to string for JSON compatibility
        item['timestamp'] = item['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
    return jsonify(items)