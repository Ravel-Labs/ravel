from flask import Blueprint, abort, request
from flask_jwt import jwt_required, current_identity
from flask import current_app as app
from api import db
from api.models.User import User
from api.models.apiresponse import APIResponse

users_bp = Blueprint('users_bp', __name__)
base_users_url = '/api/users'


@users_bp.route(base_users_url)
@jwt_required()
def get_users():
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
@jwt_required()
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
@jwt_required()
def delete_user_by_id(id):
    try:
        if id is not current_identity.id:
            abort(401, "Not authorized")
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
@jwt_required()
def update_user(id):
    try:
        db.session.query(User).filter_by(id=id).update(request.json)
        db.session.commit()
        payload = {
            "action": "updated",
            "table": "user",
            "id": id
        }
        response = APIResponse(payload, 200).response
        return response
    except Exception as e:
        abort(500, e)
