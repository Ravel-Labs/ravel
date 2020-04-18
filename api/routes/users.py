from flask import Blueprint, abort, request
from flask_jwt import jwt_required, current_identity
from ravel.api import db
from ravel.api.models.user import User
from ravel.api.models.apiresponse import APIResponse
from ravel.api.services.email import follower_notification
users_bp = Blueprint('users_bp', __name__)
base_users_url = '/api/users'


@users_bp.route(base_users_url)
@jwt_required()
def get_users():
    print('current_identity', current_identity)
    try:
        raw_users = User.query.all()
        users = [raw_user.to_dict() for raw_user in raw_users]
        if not users:
            abort(404, "There aren't any users")
        response = APIResponse(users, 200).response
        return response
    except Exception as e:
        abort(500, e)


@users_bp.route('%s/<int:id>' % base_users_url)
def get_user_by_id(id):
    try:
        user = User.query.get(id)
        if not user:
            abort(404, "User not found")
        response = APIResponse(user.to_dict(), 200).response
        return response
    except Exception as e:
        abort(500, e)


@users_bp.route('%s/delete/<int:id>' % base_users_url, methods={'GET'})
def delete_user_by_id(id):
    try:
        user = User.query.get(id)
        if not user:
            abort(404, "User id %s does not exist" % id)
        db.session.delete(user)
        db.session.commit()
        payload = {
            "action": "deleted",
            "table": "user",
            "id": id
        }
        response = APIResponse(payload, 200).response
        return response
    except Exception as e:
        abort(500, e)


@users_bp.route('%s/<int:id>' % base_users_url, methods=['PUT'])
def update_user(id):
    try:
        db.session.query(User).filter_by(id=id).update(request.json)
        db.session.commit()
        payload = {
            "action": "updated",
            "table": "user",
            "id": id
        }
        # or 204 and dont return a response
        response = APIResponse(payload, 200).response
        return response
    except Exception as e:
        abort(500, e)

@users_bp.route('send/email' % base_users_url, methods=['PUT'])
def send_email(id):
    follower_notification()
    # return redirect(url_for('user', nickname=nickname))