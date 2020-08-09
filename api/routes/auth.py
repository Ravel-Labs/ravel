from flask import Blueprint, request, abort
from flask_jwt import jwt_required, current_identity
from werkzeug.security import generate_password_hash, check_password_hash
from api.models.apiresponse import APIResponse
from api.models.User import User
from api.services.email.email import email_proxy
from api import db
from flask import current_app as app


auth_bp = Blueprint('auth_bp', __name__)
base_auth_url = '/api/auth'

'''
    Authentication methods

    Known request object attributes
        # request.json
        # request.form.get
'''


@auth_bp.route('%s/signup' % base_auth_url, methods=['POST'])
def signup_users():
    try:
        email = request.json.get('email')
        name = request.json.get('name')
        password = request.json.get('password')
        raw_user = User.query.filter_by(email=email).first()

        if raw_user:
            abort(403, "User already exists")

        raw_user = User(
            email=email,
            name=name,
            password_hash=generate_password_hash(password, method='sha256')
        )
        user = raw_user.to_dict()
        db.session.add(raw_user)
        db.session.commit()
        response = APIResponse(user, 201, message="Created").response
        email_proxy("welcome", email, name)
        return response
    except Exception as e:
        app.logger.error("error signing up user:", e)
        abort(500, e)


'''
    Check

    Check will validate your authentication status with the server. 

    It will return an OK 200 response if you're authenticated. 
'''


@auth_bp.route('%s/check' % base_auth_url)
@jwt_required()
def check():
    return APIResponse("OK", 200).response


'''
    authentication_handler is a Flask-JWT specific handler. 

    It takes the email and password given by a login function 
    and returns the result of checking their password.
'''


def authentication_handler(email, password):
    user = User.query.filter_by(email=email).first()
    if user is None:
        return None

    if check_password_hash(user.password_hash, password):
        return user

    return None


'''
    identity_handler is a Flask-JWT specific handler.

    It returns the identity of a given request.
'''


def identity_handler(payload):
    user_id = payload['identity']
    user = User.query.filter_by(id=user_id).first()
    return user
