from flask import jsonify

class BaseException(Exception):
    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        payload = {
            "message": str(self.message),
            "status": str(self.status_code),
        }
        return payload