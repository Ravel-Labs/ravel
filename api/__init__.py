from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from os import environ

db = SQLAlchemy()

def create_app():
    # TODO: Make this handle environment configs better
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

    from .models import user, track, trackout, wavfile
    '''
        db methods
        # db.drop_all()
        # db.create_all() only creates models within scope
    '''
    with app.app_context():
        db.init_app(app)
        # db.drop_all()
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
        return db.session.query(user).filter_by(int(user_id))

    '''
    WebServer Rendering Routes
    '''
    from .routes.main import main_bp
    app.register_blueprint(main_bp)

    '''
    Database Interactive Routes 
    '''
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from .routes.users import users_bp
    app.register_blueprint(users_bp)

    from .routes.tracks import tracks_bp
    app.register_blueprint(tracks_bp)

    from .routes.trackouts import trackouts_bp
    app.register_blueprint(trackouts_bp)
    
    from .routes.wavfiles import wavfiles_bp
    app.register_blueprint(wavfiles_bp)

    from .routes.errors import errors_bp
    app.register_blueprint(errors_bp)
    
    return app