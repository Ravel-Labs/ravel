from io import BytesIO
from hashlib import md5
from flask import Blueprint, abort, request, send_file
from flask_jwt import jwt_required, current_identity
from api import db
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
        name = request.json.get('name')
        user_id = current_identity.id
        print(f'getting tracks for current user; ', user_id)
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
    except Exception as e:
        abort(500, e)


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
            abort(400)
        response = APIResponse(tracks, 200).response
        return response
    except Exception as e:
        abort(500, e)


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
    except Exception as e:
        abort(500, e)


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
    except Exception as e:
        abort(500, e)


@tracks_bp.route('%s/process/<int:id>' % base_tracks_url, methods=['PUT'])
@jwt_required()
def process_track(id):
    try:
        # Dispatch email processing progress, managed by queueWorker
        email_proxy(
            template_type="status",
            user_to_email_address=email,
            user_name=name,
            button_title="")
        # extract trackout data from track
        raw_track = Track.query.get(id)
        if not raw_track:
            abort(404, f"There aren't any trackouts for track {id}")
        trackouts = raw_track.trackouts.all()
        orchestrator = Orchestrator(trackouts, raw_track)
        orchestrator.orchestrate()
        payload = {
            "action": "processing",
            "table": "track",
            "id": id
        }
        response = APIResponse(payload, 200).response
        return response
    except Exception as e:
        abort(500, e)


# TODO Rethink what blueprint this falls under
@tracks_bp.route(f'{base_tracks_url}/eq/<int:id>', methods={'GET'})
@jwt_required()
def get_eq_results_by_trackout_id(id):
    try:
        raw_tracks = Track.query.get(id)
        raw_trackouts = raw_tracks.trackouts.all()
        # For each raw_trackout lets get their EQ and return them all
        trackout_eq = dict()
        '''
            This dict will contain meta data described below
            {
                # TODO Think about adding more meta data so subsuquent calls aren't necessary
                track_id: String,
                trackout_id_0: EQ File or Binary,
                trackout_id_1: EQ File or Binary,
            }
        '''
        trackout_eq["track_id"] = id

        for raw_trackout in raw_trackouts:
            '''
            trackout:
                @methods
                    def eq
                    def de
                    def comp
            '''
            print(f'raw_trackout: {raw_trackout}')
            raw_eq = raw_trackout.eq
            eq_id = raw_eq.id
            print(f'eq_id: {eq_id}')
            eq_binary = raw_eq.equalized_binary
            print(type(eq_binary))
            trackout_eq[eq_id] = eq_binary
            samplerate = 44100
            return send_file(
                BytesIO(eq_binary),
                attachment_filename="wavFile.wav",
                as_attachment=True)
    except Exception as e:
        abort(500, e)
