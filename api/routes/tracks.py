from flask import Blueprint, abort, request
from ravel.api import db
from ravel.api.models.track import Track
from ravel.api.models.apiresponse import APIResponse

tracks_bp = Blueprint('tracks_bp', __name__)
base_tracks_url = '/api/tracks'

@tracks_bp.route(base_tracks_url, methods=['POST'])
def create_track():
    try:
        email = request.json.get('email')
        name = request.json.get('name')
        password = request.json.get('password')
        raw_track_search = Track.query.filter_by(email=email).first()
        if raw_track_search:
            return "User email already exists"
        raw_track = Track(email=email, name=name, password_hash=password)
        db.session.add(raw_track)
        db.session.commit()

        track = raw_track.to_dict()
        response = APIResponse(track, 201).response
        return response
    except Exception as e:
        abort(500, e)

@tracks_bp.route(base_tracks_url, methods={'GET'})
def get_tracks():
    try:
        raw_tracks = Track.query.all()
        tracks = [raw_track.to_dict() for raw_track in raw_tracks]
        if not tracks:
            abort(400)
        response = APIResponse(tracks, 200).response
        return response
    except Exception as e:
        abort(500, e)

@tracks_bp.route('%s/<int:id>'% base_tracks_url, methods={'GET'})
def get_track_by_id(id):
    try:
        raw_track = Track.query.get(id)
        track = raw_track.to_dict()
        if not track:
            abort(400, "A track with id %s does not exist"%id)
        response = APIResponse(track, 200).response
        return response
    except Exception as e:
        abort(500, e)

@tracks_bp.route('%s/delete/<int:id>'% base_tracks_url, methods={'DELETE'})
def delete_track_by_id(id):
    try:
        raw_track = Track.query.get(id)
        if not raw_track:
            abort(404, "A track with id %s does not exist"%id)
        db.session.delete(raw_track)
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

@tracks_bp.route('%s/<int:id>'% base_tracks_url, methods=['PUT'])
def update_track(id):
    try:
        db.session.query(Track).filter_by(id=id).update(request.json)
        db.session.commit()
        payload = {
            "action":"update",
            "table": "trackouts",
            "id": str(id)
        }
        response = APIResponse(payload, 200).response
        return response
    except Exception as e:
        abort(500, e)