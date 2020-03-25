from flask import Flask
from os import environ
from flask_cors import CORS
from flask_restful import Api
from views import Quote, User, Track

app = Flask(__name__)
app.config['FLASK_ENV'] = environ.get('FLASK_ENV')
CORS(app)
api = Api(app)

api.add_resource(Quote, '/')
api.add_resource(User, '/users')
api.add_resource(Track, '/tracks')

if __name__ == "__main__":
    app.run()
