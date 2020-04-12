from flask import Blueprint, jsonify, abort, request
from ravel.api.models.trackout import TrackOut
from ravel.api.models.apiresponse import APIResponse
from ravel.api import db

trackouts_bp = Blueprint('trackouts_bp', __name__)
base_trackouts_url = '/api/trackouts'

'''
    POST
'''
@trackouts_bp.route(base_trackouts_url, methods=['POST'])
def create_trackout():
    try:
        email = request.json.get('email')
        name = request.json.get('name')
        password = request.json.get('password')
        raw_trackout_search = TrackOut.query.filter_by(email=email).first()
        
        if raw_trackout_search:
            return "User email already exists"
        raw_trackout = TrackOut(email=email, name=name, password_hash=password)
        trackout = raw_trackout.to_dict()
        
        db.session.add(raw_trackout)
        db.session.commit()
        response = APIResponse(trackout, 201).response
        return response
    except Exception as e:
        abort(500, e)

'''
    GET all
'''
@trackouts_bp.route(base_trackouts_url, methods={'GET'})
def get_trackouts():
    try:
        raw_trackouts = TrackOut.query.all()
        trackouts = [raw_trackout.to_dict() for raw_trackout in raw_trackouts]
        if not trackouts:
            abort(400, "No trackouts have been created yet")
        response = APIResponse(trackouts, 200).response
        return response
    except Exception as e:
        abort(500, e)

'''
    GET by ID
    TODO test if dict is worth it here
'''
@trackouts_bp.route('%s/<int:id>'% base_trackouts_url, methods={'GET'})
def get_trackout_by_id(id):
    try:
        raw_trackout = TrackOut.query.get(id)
        if not raw_trackout:
            abort(400, "A trackout with id %s does not exist"%id)
        trackout = raw_trackout.to_dict()
        response = APIResponse(trackout, 200).response
        return response
    except Exception as e:
        abort(500, e)

'''
    DELETE
'''
@trackouts_bp.route('%s/delete/<int:id>'% base_trackouts_url, methods={'GET'})
def delete_trackout_by_id(id):
    try:
        raw_trackout = TrackOut.query.get(id)
        if not raw_trackout:
            abort(404, "A trackout with id %s does not exist"%id)
        db.session.delete(raw_trackout)
        db.session.commit()
        payload = {
            "action": "delete",
            "table": "trackouts",
            "id": id
        }
        response = APIResponse(payload, 200).response
        return response
    except Exception as e:
        abort(500, e)

'''
    PUT TODO check if user exists first
'''
@trackouts_bp.route('%s/<int:id>'% base_trackouts_url, methods=['PUT'])
def update_trackout(id):
    try:
        db.session.query(TrackOut).filter_by(id=id).update(request.json)
        db.session.commit()
        payload = {
            "action": "update",
            "table": "trackouts",
            "id": id
        }
        response = APIResponse(payload, 200).response
        return response
    except Exception as e:
        abort(500, e)