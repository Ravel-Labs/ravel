#!/usr/bin/env python
import os
import json
from os import environ
from flask import Flask, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from flask_login import login_user, current_user, logout_user, login_required,LoginManager
from flask_bcrypt import Bcrypt as bcrypt
from flask_cors import CORS
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
# from views import Quote, User, Track

# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
# change
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['FLASK_ENV'] = environ.get('FLASK_ENV')

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()
CORS(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))
    active = db.Column(db.Boolean())

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    def create_obj(self):
        return {
            "id": self.id,
            "username": self.username,
            "password_hash": self.password_hash
        }

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

@app.route('/api/auth/user', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        return User.query.filter_by(username=username).first().username
        abort(400)    # existing user
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'username': user.create_obj()}), 201

@app.route('/api/auth/user/<int:id>')
@login_manager.request_loader
def get_user_by_id(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})

@app.route('/api/auth/user/delete/<int:id>')
def delete_user_by_id(id):
    # Only user session can delete itself
    # Logout here
    user = User.query.get(id)
    if not user:
        abort(404)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'action': "deleted"})

@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    json_returnable = [user.create_obj() for user in users]
    if not json_returnable:
        abort(400)
    return jsonify({'users': json_returnable})

@app.route('/api/user/update', methods=['PUT'])
# TODO update user profile
def update_user():
    users = User.query.all()
    json_returnable = [user.create_obj() for user in users]
    if not json_returnable:
        abort(400)
    return jsonify({'users': json_returnable})

@app.route('/api/auth/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})

@app.route("/login", methods=['GET', 'POST'])
def login():
    # if current_user.is_authenticated:
    #     return 'already authenticated'

    username = request.json.get('username')
    password = request.json.get('password')
    user = User.query.filter_by(username=username).first()
    if user and user.verify_password(password=password):
        login_user(user)
        return "logged in"
    else:
        return 'bad email'
    return "what..."

@app.route("/logout")
def logout():
    logout_user()
    return "logged out"

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, host='0.0.0.0', port=8080)
