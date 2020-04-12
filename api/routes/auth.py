from flask import Blueprint, request, abort
from flask_jwt import jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from ravel.api.models.apiresponse import APIResponse
from ravel.api.models.user import User
from ravel.api import db


auth_bp = Blueprint('auth_bp', __name__)
base_auth_url = '/api/auth'

'''
    Server side rendering
'''
@auth_bp.route('%s/login'% base_auth_url)
def login():
    return "Login"

@auth_bp.route('%s/signup'% base_auth_url)
def signup():
    return "Signup"

'''
    Authentication methods
    
    Known request object attributes
        # request.json
        # request.form.get
'''

@auth_bp.route('%s/signup'% base_auth_url, methods=['POST'])
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
        response = APIResponse(user, 201).response
        return response
    except Exception as e:
        abort(500, e)

@auth_bp.route('%s/check'% base_auth_url)
@jwt_required()
def check():
    return APIResponse("OK", 200).response


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