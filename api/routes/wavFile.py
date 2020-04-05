from flask import Blueprint, jsonify, abort, request, send_file
from ravel.api.models.wavFile import WavFile
from ravel.api import db
from io import BytesIO

wav = Blueprint('wav', __name__)
wav.config = {}
base_wavFile_url = '/api/wav'

@wav.route('%s'% base_wavFile_url, methods=['POST'])
def create_wavFile(): 

    wavFile = request.files['file']
    binary = wavFile.read()
    wavFile = WavFile.query.filter_by(binary=binary).first()
    if wavFile:
        return "Already exists"
        # return redirect(url_for('auth.signup'))
    new_wavFile = WavFile(binary=binary)
    db.session.add(new_wavFile)
    db.session.commit()
    return "Created"

@wav.route(base_wavFile_url, methods={'GET'})
def get_wavFile():
    wavFiles = WavFile.query.all()
    json_returnable = [wavFile.create_obj() for wavFile in wavFiles]
    if not json_returnable:
        abort(400)
    return jsonify({'users': json_returnable})

@wav.route('%s/<int:id>'% base_wavFile_url, methods={'GET'})
def get_track_by_id(id):
    wavFile = WavFile.query.get(id)
    if not wavFile:
        abort(400)
    return send_file(BytesIO(wavFile.binary), attachment_filename = "wavFile.wav", as_attachment=True)

@wav.route('%s/delete/<int:id>'% base_wavFile_url, methods={'DELETE'})
def delete_track_by_id(id):
    wavFile = WavFile.query.get(id)
    if not wavFile:
        abort(404)
    db.session.delete(wavFile)
    db.session.commit()
    return jsonify({'action': "deleted"})

@wav.route('%s/<int:id>'% base_wavFile_url, methods=['PUT'])
def update_track(id):
    db.session.query(WavFile).filter_by(id=id).update(request.json)
    db.session.commit()
    return jsonify({'action': "updated"})