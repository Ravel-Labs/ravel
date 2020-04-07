from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from os import environ

db = SQLAlchemy()

def create_app():
    # Todo: Make this handle environment configs better
    app = Flask(__name__)

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

    # Configure CORS
    CORS(app, supports_credentials=True, expose_headers="['session', 'remember_token']", origins="*")

    from .models import User, track
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
        user = db.session.query(User.User).filter_by(id=int(user_id)).first()
        if user == None:
            return None
        return user

    @login_manager.request_loader
    def load_user_from_request(request):
        # Check for api_key argument and check for that
        api_key = request.args.get('api_key')
        print('api_key from args: ', api_key)
        if api_key:
            user = User.query.filter_by(api_key=api_key).first()
            if user:
                return user

        ## Check for Authorization Header and use that instead
        api_key = request.headers.get('Authorization')
        print('api_key from headers: ', api_key)
        if api_key:
            api_key = api_key.replace('Basic', '', 1)
            try:
                api_key = base64.b64decode(api_key)
            except TypeError:
                pass
            user = User.query.filter_by(api_key=api_key).first()
            if user:
                return user

        return None

    from .routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .routes.user import user as user_blueprint
    app.register_blueprint(user_blueprint)

    from .routes.track import track as track_blueprint
    app.register_blueprint(track_blueprint)

    from .routes.errors import errors as errors_blueprint
    app.register_blueprint(errors_blueprint)

    @app.route("/heartbeat")
    def heartbeat():
        return jsonify({"status": "healthy"})


    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return app.send_static_file("index.html")

    return app
