import pyrebase
from os import environ
from flask import current_app as app


print(f'### firebase key: {environ.get("FB_API_KEY")}')


firebaseConfig = {
    "apiKey": environ.get("FB_API_KEY"),
    "appId": environ.get("RAVEL_FB_ID"),
    "authDomain": "ravellabs.firebaseapp.com",
    "databaseURL": "https://ravellabs.firebaseio.com",
    "projectId": "ravellabs",
    "storageBucket": "ravellabs.appspot.com",
    "messagingSenderId": "724664302988",
}


def publish_to_file_store(path, file):
    # Type of wavFile is https://tedboy.github.io/flask/generated/generated/werkzeug.FileStorage.html
    try:
        firebase = pyrebase.initialize_app(firebaseConfig)
        storage = firebase.storage()
        fb_info = storage.child(path).put(file)
        fb_store_url = storage.child(path).get_url(firebase)
        return fb_store_url
    except Exception as e:
        raise Exception(f"Firebase Publish Error:{e}")


def retreive_from_file_store(path, uuid=""):
    try:
        firebase = pyrebase.initialize_app(firebaseConfig)
        storage = firebase.storage()
        # Download wav to disk
        local_file_name = f"{uuid}.wav" if uuid else "trackout.wav"
        file = storage.child(path).download(f"wav_tmp/{local_file_name}")
        return file
    except Exception as e:
        raise Exception(f"Firebase Retrieve Error: {e}")
