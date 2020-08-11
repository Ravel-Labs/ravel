from io import BytesIO
from hashlib import md5
from flask import Blueprint, abort, request, send_file
from flask_jwt import jwt_required, current_identity
from flask import current_app as app
from api import db
from api.models.User import User
from api.models.track_models import Track, TrackOut, Equalizer, Deesser
from api.services.firestore import retreive_from_file_store, publish_to_file_store
from api.routes.trackOuts import get_wav_from_trackout
from api import ADMINS_FROM_EMAIL_ADDRESS, mail, Q, Job
from api.services.orchestration.processing import Processor
from api.services.orchestration.orchestrator import Orchestrator
from api.services.email.email import email_proxy
from api.models.apiresponse import APIResponse
import json


tracks_bp = Blueprint('tracks_bp', __name__)
base_tracks_url = '/api/tracks'


@tracks_bp.route(base_tracks_url, methods=['POST'])
@jwt_required()
def create_track():
    try:
        user_id = current_identity.id
        name = request.json.get('name')
        artist = request.json.get('artist')
        info = request.json.get('info')

        raw_track = Track(
            user_id=user_id,
            name=name,
            artist=artist,
            info=info)

        db.session.add(raw_track)
        db.session.commit()

        track = raw_track.to_dict()

        response = APIResponse(track, 201).response
        return response
    except Exception as err:
        app.logger.error("error creating track:", err)
        abort(500, err)


'''
    GET

    tracks that belong to the currently logged in user
'''
@tracks_bp.route(base_tracks_url, methods={'GET'})
@jwt_required()
def get_tracks():
    try:
        user_id = current_identity.id
        raw_tracks = Track.query.filter_by(user_id=user_id).all()
        if not raw_tracks:
            abort(400, "A track with id %s does not exist" % user_id)
        tracks = [raw_track.to_dict() for raw_track in raw_tracks]
        if not tracks:
            # handle empty tracks list
            response = APIResponse([], 200).response
            return response

        response = APIResponse(tracks, 200).response
        print(f'responding with: ', response)
        return response
    except Exception as err:
        print(f'get_tracks error: {err}')
        app.logger.error("error getting track:", err)
        abort(500, err)


@tracks_bp.route('%s/<int:id>' % base_tracks_url, methods={'GET'})
@jwt_required()
def get_track_by_id(id):
    try:
        raw_track = Track.query.get(id)
        track = raw_track.to_dict()
        if not track:
            abort(400, "A track with id %s does not exist" % id)
        response = APIResponse(track, 200).response
        return response
    except Exception as e:
        abort(500, e)


@tracks_bp.route('%s/delete/<int:id>' % base_tracks_url, methods={'DELETE'})
@jwt_required()
def delete_track_by_id(id):
    try:
        raw_track = Track.query.get(id)
        if not raw_track:
            abort(404, "A track with id %s does not exist" % id)
        db.session.delete(raw_track)
        db.session.commit()
        payload = {
            "action": "delete",
            "table": "trackouts",
            "id": id
        }
        response = APIResponse(payload, 200).response
        return response
    except Exception as err:
        app.logger.error("error deleting track:", err)
        abort(500, err)


@tracks_bp.route('%s/<int:id>' % base_tracks_url, methods=['PUT'])
@jwt_required()
def update_track(id):
    try:
        # TODO Effected by an updated trackout
        db.session.query(Track).filter_by(id=id).update(request.json)
        db.session.commit()
        payload = {
            "action": "update",
            "table": "trackouts",
            "id": str(id)
        }
        response = APIResponse(payload, 200).response
        return response
    except Exception as e:
        abort(500, e)


@tracks_bp.route(f'{base_tracks_url}/trackouts/<int:id>', methods={'GET'})
@jwt_required()
def get_trackouts_by_track_id(id):
    try:
        raw_tracks = Track.query.get(id)
        raw_trackouts = raw_tracks.trackouts.all()
        trackouts = [raw_trackout.to_dict() for raw_trackout in raw_trackouts]
        if not trackouts:
            abort(400)
        response = APIResponse(trackouts, 200).response
        return response
    except Exception as err:
        app.logger.error("error getting track by ID:", err)
        abort(500, err)


@tracks_bp.route('%s/process/<int:id>' % base_tracks_url, methods=['PUT'])
@jwt_required()
def process_track(id):
    try:

        # Track should contain user
        current_user = User.query.get(1)
        raw_track = Track.query.get(id)
        toggle_effects_params = request.json.get('toggle_effects_params')
        app.logger.info(f"processing {id} with params: {toggle_effects_params}")

        if not raw_track:
            abort(404, f"There aren't any trackouts for track {id}")

        # Dispatch email processing progress, managed by queueWorker
        email_proxy(
            title="Initiating Processing",
            template_type="status",
            user_to_email_address=current_user.email,
            user_name=current_user.name)

        # extract trackout data from track
        raw_trackouts = raw_track.trackouts.all()
        app.logger.info(f"Processing {len(raw_trackouts)}# trackouts")
        orchestrator = Orchestrator(current_user, raw_trackouts, raw_track, toggle_effects_params)
        orchestrator.orchestrate()

        payload = {
            "action": "processing",
            "table": "track",
            "id": id
        }
        response = APIResponse(payload, 200).response
        return response
    except Exception as err:
        app.logger.error(f'error processing track {id}:', err)
        abort(500, err)
