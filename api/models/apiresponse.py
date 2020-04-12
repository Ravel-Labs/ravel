from flask import make_response

class APIResponse():
    def __init__(self, payload, status_code=None):
        self.response = make_response({"payload": payload})
        self.response.headers['Content-type'] = 'application/json'
        self.response.status_code = status_code