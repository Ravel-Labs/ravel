from flask import Blueprint, jsonify, abort, request, send_file
from flask_jwt import jwt_required, current_identity

from api.services.firestore import publish_to_file_store, retreive_from_file_store
from api.models.track_models import TrackOut, Track
from api.models.User import User
from api.models.apiresponse import APIResponse
from api import db
from scipy.io.wavfile import write, read
import requests
import scipy.io as sio
import wave
import pyrebase
from os import remove
from hashlib import md5
from io import BytesIO
trackouts_bp = Blueprint('trackouts_bp', __name__)
base_trackouts_url = '/api/trackouts'

'''
    POST
'''


@trackouts_bp.route(f"{base_trackouts_url}", methods=['POST'])
@jwt_required()
def create_trackout():
    try:
        user_id = current_identity.id
        track_id = request.json.get('track_id')
        type_of_track = request.json.get('type')
        name = request.json.get('name')
        settings = request.json.get('settings')
        raw_track = Track.query.get(track_id)
        print(f"raw track id: {raw_track.id}")
        raw_trackout = TrackOut(
            user_id=user_id,
            track_id=track_id,
            name=name,
            type=type_of_track,
            settings=settings,
            trackouts=raw_track)
        db.session.add(raw_trackout)
        db.session.commit()
        trackout = raw_trackout.to_dict()
        response = APIResponse(trackout, 201).response
        return response
    except Exception as e:
        print(f'#### error creating trackout: {e}')
        app.logger.error("error creating trackout:", e)
        abort(500, e)


'''
    GET all
'''


@trackouts_bp.route(base_trackouts_url, methods={'GET'})
@jwt_required()
def get_trackouts():
    try:
        track_id = request.args.get('track_id')
        print(f'###  Getting trackouts for track_id: {track_id}')

        # get trackouts by track_id
        if track_id:
            raw_trackouts = TrackOut.query.filter_by(track_id=track_id).all()
            trackouts = [rt.to_dict() for rt in raw_trackouts]
            if not trackouts:
                abort(400, "No trackouts have been created yet")
            response = APIResponse(trackouts, 200).response
            return response

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
'''
@trackouts_bp.route('%s/<int:id>' % base_trackouts_url, methods={'GET'})
@jwt_required()
def get_trackout_by_id(id):
    try:
        raw_trackout = TrackOut.query.get(id)
        if not raw_trackout:
            abort(400, "A trackout with id %s does not exist" % id)
        trackout = raw_trackout.to_dict()
        response = APIResponse(trackout, 200).response
        return response
    except Exception as e:
        abort(500, e)


'''
    DELETE
'''
@trackouts_bp.route('%s/<int:id>' % base_trackouts_url, methods={'DELETE'})
@jwt_required()
def delete_trackout_by_id(id):
    try:
        raw_trackout = TrackOut.query.get(id)
        if not raw_trackout:
            abort(404, "A trackout with id %s does not exist" % id)
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
    PUT
'''


@trackouts_bp.route('%s/<int:id>' % base_trackouts_url, methods=['PUT'])
@jwt_required()
def update_trackout(id):
    try:
        # TODO republish a process for a newly updated wavfile
        user_id = current_identity.id
        raw_user = db.session.query(User).get(id=user_id)
        user = raw_user.to_dict()
        if not user:
            abort(400, f"A User with this id {user_id} does not exist")

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


@trackouts_bp.route('%s/wav/<int:id>' % base_trackouts_url, methods=['PUT'])
@jwt_required()
def add_update_wavfile(id):
    try:
        print(f'hit file upload: ', request)
        raw_file = request.files['file']
        raw_trackout = TrackOut.query.get(id)
        if not raw_trackout:
            abort(404, f"There isn't a trackout id {id}")
        trackout_name = raw_trackout.name
        storage_name = f"{trackout_name}.wav"
        firestore_path = f"trackouts/{id}/{storage_name}"
        publish_to_file_store(firestore_path, raw_file)
        update_request = {
            "path": firestore_path
        }
        print(f'add update wavfile id: {id}')
        db.session.query(TrackOut).filter_by(id=id).update(update_request)
        db.session.commit()
        payload = {
            "action": "update",
            "table": "trackout",
            "id": id
        }
        response = APIResponse(payload, 200).response
        return response
    except Exception as e:
        app.logger.error("error updating wav: ", e)
        abort(500, e)


@trackouts_bp.route('%s/wav/<int:id>' % base_trackouts_url, methods=['GET'])
@jwt_required()
def get_wav_from_trackout(id):
    try:
        # Get wav path from TrackOut then call firebase service
        raw_trackout = TrackOut.query.get(id)
        if not raw_trackout:
            abort(404, f"Trackout {id} not found")
        file_name = f"{raw_trackout.name}.wav"
        firestore_path = raw_trackout.path
        retreive_from_file_store(firestore_path)

        # Get file saved to disk and convert into BytesIO
        sam_rate, data = sio.wavfile.read("trackout.wav")
        byte_io = BytesIO(bytes())
        write(byte_io, sam_rate, data)
        file = send_file(
            byte_io,
            attachment_filename=file_name,
            as_attachment=True)

        # Remove file from disk
        remove("trackout.wav")
        return file
    except Exception as e:
        abort(500, e)


@trackouts_bp.route('%s/eq/<int:id>' % base_trackouts_url, methods=['GET'])
@jwt_required()
def get_eq_from_trackout(id):
    try:
        # Get wav path from TrackOut then call firebase service
        raw_trackout = TrackOut.query.get(id)
        if not raw_trackout:
            abort(404, f"Trackout {id} not found")
        eq = raw_trackout.eq
        firestore_path = eq.path
        file_name = f"eq_results.wav"
        retreive_from_file_store(firestore_path)

        # Get file saved to disk and convert into BytesIO
        sam_rate, data = sio.wavfile.read("trackout.wav")
        byte_io = BytesIO(bytes())
        write(byte_io, sam_rate, data)
        file = send_file(
            byte_io,
            attachment_filename=file_name,
            as_attachment=True)
        # Remove file from disk
        remove("trackout.wav")
        return file
    except Exception as e:
        abort(500, e)


@trackouts_bp.route('%s/co/<int:id>' % base_trackouts_url, methods=['GET'])
@jwt_required()
def get_co_from_trackout(id):
    try:
        # Get wav path from TrackOut then call firebase service
        raw_trackout = TrackOut.query.get(id)
        if not raw_trackout:
            abort(404, f"Trackout {id} not found")
        co = raw_trackout.co
        firestore_path = co.path
        file_name = f"co_results.wav"
        retreive_from_file_store(firestore_path)

        # Get file saved to disk and convert into BytesIO
        sam_rate, data = sio.wavfile.read("trackout.wav")
        byte_io = BytesIO(bytes())
        write(byte_io, sam_rate, data)
        file = send_file(
            byte_io,
            attachment_filename=file_name,
            as_attachment=True)
        # Remove file from disk
        remove("trackout.wav")
        return file
    except Exception as e:
        abort(500, e)


@trackouts_bp.route('%s/de/<int:id>' % base_trackouts_url, methods=['GET'])
@jwt_required()
def get_de_from_trackout(id):
    try:
        # Get wav path from TrackOut then call firebase service
        raw_trackout = TrackOut.query.get(id)
        if not raw_trackout:
            abort(404, f"Trackout {id} not found")
        de = raw_trackout.de
        firestore_path = de.path
        file_name = f"de_results.wav"
        retreive_from_file_store(firestore_path)

        # Get file saved to disk and convert into BytesIO
        sam_rate, data = sio.wavfile.read("trackout.wav")
        byte_io = BytesIO(bytes())
        write(byte_io, sam_rate, data)
        file = send_file(
            byte_io,
            attachment_filename=file_name,
            as_attachment=True)
        # Remove file from disk
        remove("trackout.wav")
        return file
    except Exception as e:
        abort(500, e)


# // TODO maybe turn all of the effect gets into one method and request.body for specific details
@trackouts_bp.route('%s/re/<int:id>' % base_trackouts_url, methods=['GET'])
@jwt_required()
def get_re_from_trackout(id):
    try:
        # Get wav path from TrackOut then call firebase service
        raw_trackout = TrackOut.query.get(id)
        if not raw_trackout:
            abort(404, f"Trackout {id} not found")
        re = raw_trackout.re
        firestore_path = re.path
        print(firestore_path)
        file_name = f"re_results.wav"
        retreive_from_file_store(firestore_path)

        # Get file saved to disk and convert into BytesIO
        sam_rate, data = sio.wavfile.read("trackout.wav")
        byte_io = BytesIO(bytes())
        write(byte_io, sam_rate, data)
        file = send_file(
            byte_io,
            attachment_filename=file_name,
            as_attachment=True)
        # Remove file from disk
        remove("trackout.wav")
        return file
    except Exception as e:
        abort(500, e)
