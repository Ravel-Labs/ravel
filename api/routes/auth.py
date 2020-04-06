from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, abort, Response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from ravel.api.models.User import User
from ravel.api import db

auth = Blueprint('auth', __name__)

base_auth_url = '/api/auth'

'''
    Server side rendering
'''
@auth.route('%s/login'% base_auth_url)
def login():
    return "Login"
    # return render_template('login.html')

@auth.route('%s/signup'% base_auth_url)
def signup():
    return "Signup"
    # return render_template('signup.html')

'''
    Authentication methods

    Known request object attributes
        # request.json
        # request.form.get
'''

@auth.route('%s/signup'% base_auth_url, methods=['POST'])
def signup_post():

    email = request.json.get('email')
    name = request.json.get('name')
    password = request.json.get('password')

    user = User.query.filter_by(email=email).first()
    if user:
        return Response("User email already exists", status=404)

    new_user = User(email=email, name=name, password_hash=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()
    return "signup_post", 201

@auth.route('%s/login'% base_auth_url, methods=['POST'])
def login_post():
    email = request.json.get('email')
    password = request.json.get('password')
    remember = True if request.json.get('remember') else False
    user = User.query.filter_by(email=email).first()

    if user == None:
        return "No user found", 404

    if not user and not check_password_hash(user.password, password):
        return "Please check your login details and try again."

    login_user(user, remember=remember)
    return Response("logged in successfully", 200)

@auth.route('%s/logout'% base_auth_url)
@login_required
def logout():
    logout_user()
    return "logout"
    # return redirect(url_for('main.index'))


@auth.route('%s/check'% base_auth_url)
@login_required
def check():
    user = current_user()
    return Response(jsonify(user), 200)
    # return redirect(url_for('main.index'))
