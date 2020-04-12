from flask import Blueprint, abort, request, send_file
from ravel.api.models.apiresponse import APIResponse
from ravel.api.models.wavfile import WavFile
from ravel.api import db
from hashlib import md5
from io import BytesIO
wavfiles_bp = Blueprint('wavfiles_bp', __name__)
base_wavfiles_url = '/api/wavfiles'

@wavfiles_bp.route(base_wavfiles_url, methods=['POST'])
def create_wavfile():
    try:
        raw_file = request.files['file']
        file_binary = raw_file.read()
        file_binary_hash = md5(file_binary).digest()
        raw_wavfile_search = WavFile.query.filter_by(file_hash=file_binary_hash).first()
        if raw_wavfile_search:
            return "Already exists"
        raw_wavfile = WavFile(file_binary=file_binary, file_hash=file_binary_hash)
        wavfile = raw_wavfile.to_dict()
        db.session.add(raw_wavfile)
        db.session.commit()
        response = APIResponse(wavfile, 201).response
        return response
    except Exception as e:
        abort(500, e)

@wavfiles_bp.route(base_wavfiles_url, methods={'GET'})
def get_wavfiles():
    try:
        raw_wavfiles = WavFile.query.all()
        wavfiles = [raw_wavfile.to_dict() for raw_wavfile in raw_wavfiles]
        if not wavfiles:
            abort(400, "No wavfiles have been created")
        response = APIResponse(wavfiles, 200).response
        return response
    except Exception as e:
        abort(500, e)

@wavfiles_bp.route('%s/<int:id>'% base_wavfiles_url, methods={'GET'})
def get_wavfile_by_id(id):
    try:
        raw_wavfile = WavFile.query.get(id)
        if not raw_wavfile:
            abort(404, "A wavefile with id %s does not exist"% id)
        return send_file(BytesIO(raw_wavfile.file_binary), attachment_filename = "wavFile.wav", as_attachment=True)
    except Exception as e:
        abort(500, e)

@wavfiles_bp.route('%s/delete/<int:id>'% base_wavfiles_url, methods={'DELETE'})
def delete_wavfile_by_id(id):
    try:
        raw_wavfile = WavFile.query.get(id)
        if not raw_wavfile:
            abort(404, "A wavefile with id %s does not exist"% id)
        db.session.delete(raw_wavfile)
        db.session.commit()
        payload = {
            "action" : "deleted",
            "table": "wavfile",
            "id": id
        }
        response = APIResponse(payload, 200).response
        return response
    except Exception as e:
        abort(500, e)

@wavfiles_bp.route('%s/<int:id>'% base_wavfiles_url, methods=['PUT'])
def update_wavfile(id):
    try:
        raw_file = request.files['file']
        file_binary = raw_file.read()
        file_binary_hash = md5(file_binary).digest()
        update_request = {
            "file_binary": file_binary,
            "file_hash": file_binary_hash
        }
        db.session.query(WavFile).filter_by(id=id).update(update_request)
        db.session.commit()
        payload = {
            "action" : "update",
            "table": "wavfile",
            "id": id
        }
        response = APIResponse(payload, 200).response
        return response
    except Exception as e:
        abort(500, e)