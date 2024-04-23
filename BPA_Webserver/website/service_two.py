from flask import Blueprint


service_two = Blueprint('service_two', __name__, url_prefix='/service_two')

@service_two.route('/', methods=['GET', 'POST'])
def home():
    return 'Hello World from Service Two!'