import requests
import pyrebase


firebaseConfig = {
    "apiKey": "AIzaSyBnVdSGrhaMP2KlF8Xg93V9EESdA9ngCrE",
    "authDomain": "ravellabs.firebaseapp.com",
    "databaseURL": "https://ravellabs.firebaseio.com",
    "projectId": "ravellabs",
    "storageBucket": "ravellabs.appspot.com",
    "messagingSenderId": "724664302988",
    "appId": "1:724664302988:web:e00c15ac79b2179946aaa9"
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
        raise Exception(f"{e}")


def retreive_from_file_store(path, index=""):
    try:
        firebase = pyrebase.initialize_app(firebaseConfig)
        storage = firebase.storage()
        print(path)
        # Download wav to file system
        local_file_name = f"trackout_{index}.wav"
        return storage.child(path).download(local_file_name)
    except Exception as e:
        raise Exception(f"Firebase: {e}")
