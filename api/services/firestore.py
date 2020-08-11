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
        app.logger.info(f"Firebase put{fb_info}")
        app.logger.info(f"Firebase url{fb_store_url}")
        return fb_store_url
    except Exception as e:
        raise Exception(f"Firebase Publish Error:{e}")


def retreive_from_file_store(path, index=""):
    try:
        firebase = pyrebase.initialize_app(firebaseConfig)
        storage = firebase.storage()
        # Download wav to disk
        local_file_name = f"trackout_{index}.wav" if index else "trackout.wav"
        file = storage.child(path).download(local_file_name)
        app.logger.info(f"Firebase file: {file}")
        return file
    except Exception as e:
        raise Exception(f"Firebase Retrieve Error: {e}")
