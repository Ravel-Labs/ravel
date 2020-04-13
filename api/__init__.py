from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt import JWT
from os import environ

db = SQLAlchemy()


def create_app():
    # Todo: Make this handle environment configs better
    app = Flask(__name__)
    app.config['FLASK_ENV'] = environ.get('FLASK_ENV')
    app.config["SECRET_KEY"] = "thisshouldbesetforproduction"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"  # url
    app.config["JWT_AUTH_URL_RULE"] = "/api/auth/login"
    app.config["JWT_SECRET_KEY"] = "thisshouldbesetforproduction"
    CORS(app)

    from .models import user, track, trackout, wavfile
    from .routes.auth import authentication_handler, identity_handler
    JWT(app, authentication_handler, identity_handler)

    '''
        # db.drop_all()
        # db.create_all() only creates models within scope
    '''
    with app.app_context():
        db.init_app(app)
        # db.drop_all()
        db.create_all()
        db.session.commit()

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
