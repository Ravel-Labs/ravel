import pyrebase
from os import environ
print(environ.get("FB_API_KEY"))
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
        raise Exception(f"Firebase:{e}")


def retreive_from_file_store(path, index=""):
    try:
        firebase = pyrebase.initialize_app(firebaseConfig)
        storage = firebase.storage()
        # Download wav to disk
        local_file_name = f"trackout_{index}.wav" if index else "trackout.wav"
        return storage.child(path).download(local_file_name)
    except Exception as e:
        raise Exception(f"Firebase: {e}")
