from flask import render_template, Blueprint
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
    data = list(collection.find({})) 
    print(data)
    return render_template('home.html', data=data)