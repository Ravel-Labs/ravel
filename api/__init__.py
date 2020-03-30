from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from os import environ

db = SQLAlchemy()

def create_app():
    # Todo: Make this handle environment configs better
    environment = environ.get('FLASK_ENV')
    db_url = environ.get('FLASK_DB_URL')

    LOCAL = "mysql+pymysql://dbuser:dbpassword@localhost:3306/quotes_db"
    DOCKER = "mysql+pymysql://dbuser:dbpassword@db/quotes_db"
    
    if db_url != None:
        url=db_url
    if environment == "development":
        url=LOCAL
    if environment == "production":
        url=DOCKER
    else:
        url=DOCKER

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "THISISASECRETKEY"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite" # url
    app.config['FLASK_ENV'] = environ.get('FLASK_ENV')
    CORS(app)

    from .models import User
    '''
        db methods
        # db.drop_all()
        # db.create_all() only creates models within scope
    '''
    with app.app_context():
        db.init_app(app)
        db.create_all()
        db.session.commit()

    login_manager = LoginManager()
    # When not authenticated client will be redirected to auth.login route
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    # Connection between browser cookie user id and db user object
    # TODO Remove this comment once confirmed working with UI
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .routes.user import user as user_blueprint
    app.register_blueprint(user_blueprint)
    
    return app