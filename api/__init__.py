# from run import User
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from config import config
# app = Flask(__name__)
# db = SQLAlchemy()

# def create_app(config_name):
#     app = Flask(__name__)
#     app.config.from_object(config[config_name])
#     config[config_name].init_app(app)
#     db.init_app(app)
#     return app

# @app.shell_context_processor
# def make_shell_context():
#     return dict(db=db, User=User)