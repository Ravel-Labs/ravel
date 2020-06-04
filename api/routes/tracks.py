from io import BytesIO
from hashlib import md5
from flask import Blueprint, abort, request
from flask_jwt import jwt_required, current_identity
from ravel.api import db
from ravel.api.models.track_models import Track, TrackOut
from ravel.api.models.track_models import Equalizer
from ravel.api import ADMINS_FROM_EMAIL_ADDRESS, mail, Q, Job
from ravel.api.processing import Handler, Processor
from ravel.api.services.email.email import email_proxy
from ravel.api.models.apiresponse import APIResponse
import json
import time


tracks_bp = Blueprint('tracks_bp', __name__)
base_tracks_url = '/api/tracks'

# Creational pattern to the processing layer
handler = Handler()

# @jwt_required()
@tracks_bp.route(base_tracks_url, methods=['POST'])
def create_track():
    try:
        name = request.json.get('name')
        user_id = 1
        artist = request.json.get('artist')
        info = request.json.get('info')

        raw_track = Track(
            name=name,
            user_id=user_id,
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


# @jwt_required()
@tracks_bp.route(base_tracks_url, methods={'GET'})
def get_tracks():
    try:
        raw_tracks = Track.query.filter_by(user_id=1)
        tracks = [raw_track.to_dict() for raw_track in raw_tracks]
        if not tracks:
            abort(400)
        response = APIResponse(tracks, 200).response
        return response
    except Exception as e:
        abort(500, e)


# @jwt_required()
@tracks_bp.route('%s/<int:id>' % base_tracks_url, methods={'GET'})
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


# @jwt_required()
@tracks_bp.route('%s/delete/<int:id>' % base_tracks_url, methods={'DELETE'})
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


# @jwt_required()
@tracks_bp.route('%s/<int:id>' % base_tracks_url, methods=['PUT'])
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


# @jwt_required()
@tracks_bp.route('%s/process/<int:id>' % base_tracks_url, methods=['PUT'])
def process_track(id):
    print(f"hello processing {id}")
    # Get trackouts > wavfile
    try:
        # Dispatch email processing progress
        # email_proxy(
        #     template_type="status",
        #     user_to_email_address=email,
        #     user_name=name,
        #     button_title="")

        # Get tracks by id
        raw_track = Track.query.get(id)
        print(raw_track)
        payload = {
            "job": "started"
        }

        trackouts = raw_track.trackouts.all()
        print(f'len trackouts: {len(trackouts)}')
        trackouts_equalization = [track_out for track_out in trackouts]
        print(type(trackouts_equalization))
        # trackout_binarys = [track_out.file_binary for track_out in trackouts]
        
        # if there is equalization to the track then apply it
        # TODO Any effect that is being applied
        # Based on the data we are passing in
        for trackout in trackouts_equalization:
            print(type(set([trackout])))
            # Minimum number of trackouts? Can a track be analysed against itself? If not then what?
            remaining_track_outs = set(trackouts_equalization)-set([trackout])

            print(f"Got to the for loop {len(remaining_track_outs)}")
            wavfile = trackout.file_binary
            eq_function = process_and_save

            # TODO: These params should come from the request that's updating
            # the track.
            '''
                Equalize each trackout A in a Set against the subset (totalSet - A)
            '''
            eq_params = {
                "trackout_id": 1,
                "freq": "1200",
                "filter_type": "",
                "gain": 1
            }
            eq_arguments = (wavfile, remaining_track_outs, eq_params, trackout.id)
            processing_job = Job(eq_function, eq_arguments)
            print(f'processing job:  {processing_job}')

            # TODO: needs to resolve the wavfile ID of the processing job
            # so that it can be updated in the database for the trackout
            resolved = Q.put(processing_job)
            print(f'resolved: ', {type(resolved)})

            # update database to match records
            # db.session.query(Track).filter_by(id=id).update(request.json)
            # db.session.commit()

            # TODO done processing update the trackout model with a new
            # resolved processing

        
        # print(trackouts_equalization[0].file_binary)
        # function_arguments = (a, b)
        # process_job = Job(processing, function_arguments)
        # Q.put(process_job)

        response = APIResponse(payload, 200).response
        return response
    except Exception as e:
        abort(500, e)


@tracks_bp.route(f'{base_tracks_url}/trackouts/<int:id>', methods={'GET'})
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


def process_and_save(mainWavfile, listOfWavfiles, eq_params, trackout_id):

    processor = Processor(mainWavfile, listOfWavfiles)
    trackout = TrackOut.query.get(trackout_id)
    eq_wav = processor.equalize()
    print(f"equalized complete: {bool(eq_wav)}")
    raw_equalizer = Equalizer(
        trackout_id=trackout_id,
        freq=eq_params["freq"],
        filter_type=eq_params["filter_type"],
        gain=eq_params["gain"],
        equalized_binary=eq_wav,
        eq=trackout
    )
# TODO try batching db writes
    db.session.add(raw_equalizer)
    db.session.commit()

    # eq_wav = processor.compress()