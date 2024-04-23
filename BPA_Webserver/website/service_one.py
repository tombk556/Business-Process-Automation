from flask import Blueprint


service_one = Blueprint('service_one', __name__, url_prefix='/service_one')

@service_one.route('/', methods=['GET', 'POST'])
def home():
    return 'Hello World from Service One!'