from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from ravel.api.models.User import User
from ravel.api import db

user = Blueprint('user', __name__)

base_user_url = '/api/users'

@user.route('%s/<int:id>', base_user_url)
def get_user_by_id(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})

@user.route('%s/delete/<int:id>', base_user_url) #, method={'DELETE'}
def delete_user_by_id(id):
    user = User.query.get(id)
    if not user:
        abort(404)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'action': "deleted"})

@user.route('%s/<int:id>', base_user_url, methods=['PUT'])
def update_user(id):
    return "Please develop me"