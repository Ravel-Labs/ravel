from flask import Blueprint, abort, request
from flask_jwt import jwt_required, current_identity
from ravel.api import db
from ravel.api.models.track import Track
from ravel.api.models.track_models import Userx, Post
from ravel.api.services.email.email import email_proxy
from ravel.api.models.apiresponse import APIResponse
import json
import time
tracks_bp = Blueprint('tracks_bp', __name__)
base_tracks_url = '/api/tracks'


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
@tracks_bp.route('%s/process/<int:id>' % base_tracks_url, methods=['GET'])
def process_track(id):
    # Get trackouts > wavfile
    print("ENTER")
    try:
        # Dispatch email processing progress
        # email_proxy(
        #     template_type="status",
        #     user_to_email_address=email,
        #     user_name=name,
        #     button_title="")

        # Get tracks by id
        raw_track = json.loads(get_track_by_id(id).response[0])
        track = raw_track.get("payload")
        # Extract trackout ids from track
        print(track)
        # Get wavfiles from trackouts


        # TODO Add processing to queue for each track...?
        # function_arguments = (a, b)
        # process_job = Job(processing, function_arguments)
        # Q.put(process_job)

        response = APIResponse(payload, 200).response
        return response
    except Exception as e:
        abort(500, e)

@tracks_bp.route(f'{base_tracks_url}/user', methods=['POST'])
def create_userx():
    try:
        username = request.json.get('username')
        email = request.json.get('email')
        password_hash = request.json.get('pas')

        raw_track = Userx(
            username=username,
            email=email,
            password_hash=password_hash)

        db.session.add(raw_track)
        db.session.commit()

        track = raw_track.to_dict()
        response = APIResponse(track, 201).response
        return response
    except Exception as e:
        abort(500, e)

@tracks_bp.route(f'{base_tracks_url}/user/<int:id>', methods={'GET'})
def get_userx(id):
    try:
        raw_tracks=Userx.query.filter_by(id=id).first()
        print(type(raw_tracks))
        print(raw_tracks.to_dict())
        print(raw_tracks.posts)
        tracks=raw_tracks.to_dict()# for raw_track in raw_tracks]
        if not tracks:
            abort(400)
        response=APIResponse(tracks, 200).response
        return response
    except Exception as e:
        abort(500, e)


@tracks_bp.route(f'{base_tracks_url}/post/<int:id>', methods=['POST'])
def create_post(id):
    try:
        print(f"enter {id}")
        userx = Userx.query.get(id)
        print(type(userx))
        print(userx.to_dict())
        body = request.json.get('body')
        # timestamp = request.json.get('timestamp')
        
        raw_track = Post(
            body=body,
            post=userx)
        result = db.session.query(Userx).join(Post)
        # time.sleep(20)
        print(f"holy shit {result.all()}")
        db.session.add(raw_track)
        db.session.commit()

        track = raw_track.to_dict()
        response = APIResponse(track, 201).response
        return response
    except Exception as e:
        abort(500, e)


@tracks_bp.route(f'{base_tracks_url}/post', methods={'GET'})
def get_post():
    try:
        raw_tracks=Post.query.all()
        tracks=[raw_track.to_dict() for raw_track in raw_tracks]
        if not tracks:
            abort(400)
        response=APIResponse(tracks, 200).response
        return response
    except Exception as e:
        abort(500, e)