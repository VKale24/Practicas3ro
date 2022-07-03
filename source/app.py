from flask import Flask
from flask_jwt_extended import JWTManager

from config import config

#Routes
from routes import Company

app = Flask(__name__)

def page_not_found(error):
    return "<h1>Not Found Page</h1>", 404

if __name__ == '__main__':
    app.config.from_object(config['development'])

    #Blueprints
    app.register_blueprint(Company.main, url_prefix='/auth-service')

    #Error Handlers
    jwt = JWTManager(app)
    app.register_error_handler(404, page_not_found)
    app.run(port=4000)
