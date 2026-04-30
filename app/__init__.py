from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    from app.auth import routes as auth_routes
    from app.complaints import routes as complaints_routes
    from app.admin import routes as admin_routes
    
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(complaints_routes.bp)
    app.register_blueprint(admin_routes.bp)
    
    with app.app_context():
        db.create_all()
    
    return app