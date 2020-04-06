from flask import Blueprint, jsonify, abort, request
from ravel.api.models.User import User
from ravel.api import db

user = Blueprint('user', __name__)

base_user_url = '/api/users'

@user.route(base_user_url)
def get_users():
    users = User.query.all()
    json_returnable = [user.create_obj() for user in users]
    if not json_returnable:
        abort(400)
    return jsonify({'users': json_returnable})

@user.route('%s/<int:id>'% base_user_url)
def get_user_by_id(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})

@user.route('%s/delete/<int:id>'% base_user_url) #, method={'DELETE'}
def delete_user_by_id(id):
    user = User.query.get(id)
    if not user:
        abort(404)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'action': "deleted"})

@user.route('%s/<int:id>'% base_user_url, methods=['PUT'])
def update_user(id):
    db.session.query(User).filter_by(id=id).update(request.json)
    db.session.commit()
    return jsonify({'action': "updated"})
