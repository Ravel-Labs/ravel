from flask import make_response


class APIResponse():
    """
    APIResponse provides a uniform, extendible wrapper for our API JSON
    responses.

    The default response is 200 OK
    """

    def __init__(self, payload, status_code=200, message="OK"):
        self.response = make_response({"payload": payload})
        self.response.headers['Content-type'] = 'application/json'
        self.response.status_code = status_code
        self.response.message = message
