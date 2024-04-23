from flask import Flask

def create_app():
    app = Flask(__name__)
    
    from .service_one import service_one
    from .service_two import service_two
    
    app.register_blueprint(service_one)
    app.register_blueprint(service_two)
    
    return app