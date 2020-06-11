from io import BytesIO
from hashlib import md5
from flask import Blueprint, abort, request, send_file
from flask_jwt import jwt_required, current_identity
from scipy.io.wavfile import write, read
from ravel.api import db
import numpy as np
from ravel.api.models.track_models import Track, TrackOut
from ravel.api.models.track_models import Equalizer
from ravel.api.services.firestore import retreive_from_file_store
from ravel.api.routes.trackOuts import get_wav_from_trackout
from ravel.api import ADMINS_FROM_EMAIL_ADDRESS, mail, Q, Job
from ravel.api.processing import Handler, Processor
from ravel.api.services.email.email import email_proxy
from ravel.api.models.apiresponse import APIResponse
from os import remove
import json
import time
import scipy.io as sio


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


# @jwt_required()
@tracks_bp.route('%s/process/<int:id>' % base_tracks_url, methods=['PUT'])
def process_track(id):
    try:
        # Dispatch email processing progress, managed by queueWorker
        # email_proxy(
        #     template_type="status",
        #     user_to_email_address=email,
        #     user_name=name,
        #     button_title="")

        # Get tracks by id
        raw_track = Track.query.get(id)
        trackouts = raw_track.trackouts.all()
        trackout_paths = [track_out.path for track_out in trackouts]
        num_of_trackouts = len(trackout_paths)
        print(num_of_trackouts)
        
        # for each path request file from firebase
        trackouts_as_numpy = list()
        for index, path in enumerate(trackout_paths):
            retreive_from_file_store(path, str(index))
            sam_rate, main_trackout = sio.wavfile.read(f"trackout_{index}.wav")
            main_trackout = main_trackout.astype(np.float32)
            trackouts_as_numpy.append(main_trackout)
        # for each trackout run equalize
        for i, trackout in enumerate(trackouts):
            # remaining_trackouts = set(trackouts)-set([trackout])
            # Equalize each trackout A in a Set against the subset (totalSet - A)
            # TODO get this from DB model
            eq_params = {
                "trackout_id": 1,
                "freq": "1200",
                "filter_type": 0,
                "gain": 1
            }
            # load main_trackout
            main_trackout = trackouts_as_numpy[i]
            remaining_trackouts = trackouts_as_numpy[:i-1] + trackouts_as_numpy[i:]
            eq_arguments = (main_trackout, remaining_trackouts, trackouts_as_numpy, eq_params, trackout.id)
            processing_job = Job(process_and_save, eq_arguments)
            print(f'processing job:  {processing_job}')
            resolved = Q.put(processing_job)
            print(f'Resolved: {type(resolved)}')
            
        # Todo remove all trackouts in storage
        for i, _ in enumerate(trackout_paths):
            remove(f"trackout_{i}.wav")

    #    """
    #     # trackout_binarys = [track_out.file_binary for track_out in trackouts]
        
    #     # if there is equalization to the track then apply it
    #     # TODO Any effect that is being applied
    #     # Based on the data we are passing in

    #         print(type(set([trackout])))
    #         # Minimum number of trackouts? Can a track be analysed against itself? If not then what?
    #         remaining_track_outs = set(trackouts)-set([trackout])

    #         print(f"Got to the for loop {len(remaining_track_outs)}")
    #         wavfile = trackout.file_binary
    #         eq_function = process_and_save

    #         # TODO: These params should come from the request that's updating
    #         # the track.

    #         # TODO: needs to resolve the wavfile ID of the processing job
    #         # so that it can be updated in the database for the trackout
    #         resolved = Q.put(processing_job)
    #         print(f'resolved: ', {type(resolved)})

    #         # update database to match records
    #         # db.session.query(Track).filter_by(id=id).update(request.json)
    #         # db.session.commit()

    #         # TODO done processing update the trackout model with a new
    #         # resolved processing

        
    #     # print(trackouts_equalization[0].file_binary)
    #     # function_arguments = (a, b)
    #     # process_job = Job(processing, function_arguments)
    #     # Q.put(process_job)
    # """
        response = APIResponse({}, 200).response
        return response
    except Exception as e:
        abort(500, e)


def process_and_save(main_trackout, other_trackouts, all_trackouts, eq_params, trackout_id):
    print("Processing track")
    processor = Processor(main_trackout, other_trackouts, all_trackouts)
#     trackout = TrackOut.query.get(trackout_id)

    eq_wav = processor.equalize()
    print(f"Processor.equalized completed: {bool(eq_wav)}")
# #     raw_equalizer = Equalizer(
# #         trackout_id=trackout_id,
# #         freq=eq_params["freq"],
# #         filter_type=eq_params["filter_type"],
# #         gain=eq_params["gain"],
# #         equalized_binary=eq_wav,
# #         eq=trackout
# #     )
# # # TODO try batching db writes
# #     db.session.add(raw_equalizer)
# #     db.session.commit()

#     # eq_wav = processor.compress()
#     eq_wav = processor.deesser()


# TODO Should be moved into its own blueprint /eq/<track_id>/<trackout_id>  = not totally correct
@tracks_bp.route(f'{base_tracks_url}/eq/<int:id>', methods={'GET'})
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
            # rendered = write("wavFile.wav", samplerate, eq_binary)

            # return send_file(
            #     rendered,
            #     attachment_filename="wavFile.wav",
            #     as_attachment=True)

    except Exception as e:
        abort(500, e)
