from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from ravel.api.models.User import User
from ravel.api import db

auth = Blueprint('auth', __name__)

base_auth_url = '/api/auth'

'''
    Server side rendering
'''
@auth.route('%s/login', base_auth_url)
def login():
    return "Login"
    # return render_template('login.html')

@auth.route('%s/signup', base_auth_url)
def signup():
    return "Signup"
    # return render_template('signup.html')

'''
    Authentication methods
    
    Known request object attributes
        # request.json
        # request.form.get
'''
@auth.route('%s/login', base_auth_url, methods=['POST'])
def login_post():
    email = request.json.get('email')
    password = request.json.get('password')
    remember = True if request.json.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user and not check_password_hash(user.password, password):
        return "Please check your login details and try again."
        # return redirect(url_for('auth.login'))

    login_user(user, remember=remember)
    return "login_post"
    # return redirect(url_for('main.profile'))

@auth.route('%s/signup', base_auth_url, methods=['POST'])
def signup_post():

    email = request.json.get('email')
    name = request.json.get('name')
    password = request.json.get('password')

    user = User.query.filter_by(email=email).first()
    if user:
        return "User email already exists"
        # return redirect(url_for('auth.signup'))

    new_user = User(email=email, name=name, password_hash=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()
    return "signup_post"
    # return redirect(url_for('auth.login'))

@auth.route('%s/logout',base_auth_url)
@login_required
def logout():
    logout_user()
    return "logout"
    # return redirect(url_for('main.index'))