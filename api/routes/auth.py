from flask import Blueprint, request, jsonify, Response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask_jwt import jwt_required, current_identity
from ravel.api.models.User import User
from ravel.api import db

auth = Blueprint('auth', __name__)

base_auth_url = '/api/auth'

'''
    Server side rendering
'''
@auth.route('%s/login' % base_auth_url)
def login():
    return "Login"
    # return render_template('login.html')


@auth.route('%s/signup' % base_auth_url)
def signup():
    return "Signup"
    # return render_template('signup.html')


'''
    Authentication methods

    Known request object attributes
        # request.json
        # request.form.get
'''


@auth.route('%s/signup' % base_auth_url, methods=['POST'])
def signup_post():

    # TODO: make sure unique email validation works
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

    # generate JWT

    # save the JWT to the user

    # login user with login_manager

    # return the user and JWT as JSON
    return "signup_post", 201

# There's no password field on the user that's returned from the query
@auth.route('%s/login' % base_auth_url, methods=['POST'])
def login_post():
    email = request.json.get('email')
    password = request.json.get('password')
    remember = True if request.json.get('remember') else False
    user = User.query.filter_by(email=email).first()
    print('user: ', user)

    if user is None:
        return "No user found", 404

    if user and not check_password_hash(user.password_hash, password):
        return "Please check your login details and try again."

    # generate a new token
    # save it to the user
    # log them in with login manager
    # return the JWT token

    login_user(user, remember=remember)
    return Response(user.api_token, 200)


@auth.route('%s/logout' % base_auth_url)
@login_required
def logout():
    # set users jwt token to nil

    # logout user
    logout_user()
    return "logout"
    # return redirect(url_for('main.index'))


@auth.route('%s/check' % base_auth_url)
@jwt_required()
def check():
    return "OK"


def authentication_handler(email, password):
    user = User.query.filter_by(email=email).first()

    if user is None:
        return None

    if check_password_hash(user.password_hash, password):
        return user

    return None


def identity_handler(payload):
    user_id = payload['identity']
    print("identity user_id: ", user_id)
    user = User.query.filter_by(id=user_id).first()
    print("identity user object: ", print)
    return user
