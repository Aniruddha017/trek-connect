from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config


db = SQLAlchemy()
login_manager = LoginManager()

from app.models import User

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))

    if user and user.is_blacklisted == True:
        return None 
    return user

def create_app():
    
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)


    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from app.main_routes import main
    from app.routes.auth import auth
    from app.routes.admin import admin 

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    

    return app 
