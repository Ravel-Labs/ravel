from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt import JWT
from os import environ

db = SQLAlchemy()


def create_app():
    # Todo: Make this handle environment configs better
    app = Flask(__name__)

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "THISISASECRETKEY"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"  # url
    app.config['FLASK_ENV'] = environ.get('FLASK_ENV')
    CORS(app)

    from .routes.auth import authentication_handler, identity_handler
    JWT(app, authentication_handler, identity_handler)

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

    from .routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .routes.user import user as user_blueprint
    app.register_blueprint(user_blueprint)

    from .routes.track import track as track_blueprint
    app.register_blueprint(track_blueprint)

    from .routes.trackOuts import trackOuts as trackOuts_blueprint
    app.register_blueprint(trackOuts_blueprint)

    from .routes.wavFile import wav as wav_blueprint
    app.register_blueprint(wav_blueprint)

    from .routes.errors import errors as errors_blueprint
    app.register_blueprint(errors_blueprint)

    return app
