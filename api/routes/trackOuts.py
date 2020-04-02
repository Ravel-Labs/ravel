from flask import Blueprint, jsonify, abort, request
from ravel.api.models.trackOuts import TrackOut
from ravel.api import db

trackOuts = Blueprint('trackOuts', __name__)

base_trackOut_url = '/api/trackout'

@trackOuts.route('%s'% base_trackOut_url, methods=['POST'])
def create_trackOut():

    email = request.json.get('email')
    name = request.json.get('name')
    password = request.json.get('password')
    trackOut = TrackOut.query.filter_by(email=email).first()
    if trackOut:
        return "User email already exists"
        # return redirect(url_for('auth.signup'))
    new_trackOut = TrackOut(email=email, name=name, password_hash=password)
    db.session.add(new_trackOut)
    db.session.commit()
    return "Created"

@trackOuts.route(base_trackOut_url, methods={'GET'})
def get_trackOuts():
    trackOuts = TrackOut.query.all()
    json_returnable = [trackOut.create_obj() for trackOut in trackOuts]
    if not json_returnable:
        abort(400)
    return jsonify({'users': json_returnable})

@trackOuts.route('%s/<int:id>'% base_trackOut_url, methods={'GET'})
def get_track_by_id(id):
    trackOut = trackOuts.query.get(id)
    if not trackOut:
        abort(400)
    return jsonify({'payload': trackOuts.name})

@trackOuts.route('%s/delete/<int:id>'% base_trackOut_url, methods={'DELETE'})
def delete_track_by_id(id):
    trackOut = TrackOut.query.get(id)
    if not trackOut:
        abort(404)
    db.session.delete(trackOut)
    db.session.commit()
    return jsonify({'action': "deleted"})

@trackOuts.route('%s/<int:id>'% base_trackOut_url, methods=['PUT'])
def update_track(id):
    db.session.query(TrackOut).filter_by(id=id).update(request.json)
    db.session.commit()
    return jsonify({'action': "updated"})