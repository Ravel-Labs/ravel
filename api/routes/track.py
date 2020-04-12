from flask import Blueprint, jsonify, abort, request
from ravel.api.models.track import Track
from ravel.api import db

track = Blueprint('track', __name__)

base_track_url = '/api/track'


@track.route('%s' % base_track_url, methods=['POST'])
def create_track():

    email = request.json.get('email')
    name = request.json.get('name')
    password = request.json.get('password')
    track = Track.query.filter_by(email=email).first()
    if track:
        return "User email already exists"
        # return redirect(url_for('auth.signup'))
    new_track = Track(email=email, name=name, password_hash=password)
    db.session.add(new_track)
    db.session.commit()
    return "Created"


@track.route(base_track_url, methods={'GET'})
def get_tracks():
    tracks = Track.query.all()
    json_returnable = [track.create_obj() for track in tracks]
    if not json_returnable:
        abort(400)
    return jsonify({'users': json_returnable})


@track.route('%s/<int:id>' % base_track_url, methods={'GET'})
def get_track_by_id(id):
    track = Track.query.get(id)
    if not track:
        abort(400)
    return jsonify({'payload': track.name})


@track.route('%s/delete/<int:id>' % base_track_url, methods={'DELETE'})
def delete_track_by_id(id):
    track = Track.query.get(id)
    if not track:
        abort(404)
    db.session.delete(track)
    db.session.commit()
    return jsonify({'action': "deleted"})


@track.route('%s/<int:id>' % base_track_url, methods=['PUT'])
def update_track(id):
    db.session.query(Track).filter_by(id=id).update(request.json)
    db.session.commit()
    return jsonify({'action': "updated"})
