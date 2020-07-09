from flask import Blueprint
from api.models.errors import BaseException

errors_bp = Blueprint('errors_bp', __name__)


@errors_bp.app_errorhandler(404)
def not_found_error(error):
    return BaseException(error, 404).to_dict()


@errors_bp.app_errorhandler(403)
def already_exists(error):
    return BaseException(error, 403).to_dict()


@errors_bp.app_errorhandler(401)
def invalid_credentials(error):
    return BaseException(error, 401).to_dict()


@errors_bp.app_errorhandler(500)
def internal_error(error):
    return BaseException(error, 500).to_dict()
