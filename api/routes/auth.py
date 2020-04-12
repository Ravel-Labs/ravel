from flask import Blueprint, request, Response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt import jwt_required
from ravel.api.models.User import User
from ravel.api import db

auth = Blueprint('auth', __name__)

base_auth_url = '/api/auth'


@auth.route('%s/signup' % base_auth_url, methods=['POST'])
def signup_post():
    email = request.json.get('email')
    name = request.json.get('name')
    password = request.json.get('password')

    user = User.query.filter_by(email=email).first()
    if user:
        return Response("User email already exists", status=404)

    new_user = User(
        email=email,
        name=name,
        password_hash=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()

    return Response("created", 201)


@auth.route('%s/check' % base_auth_url)
@jwt_required()
def check():
    return Response("OK", 200)


def authentication_handler(email, password):
    user = User.query.filter_by(email=email).first()

    if user is None:
        return None

    if check_password_hash(user.password_hash, password):
        return user

    return None


def identity_handler(payload):
    user_id = payload['identity']
    user = User.query.filter_by(id=user_id).first()
    return user
