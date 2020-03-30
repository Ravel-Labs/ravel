from flask import render_template, Blueprint
from ravel.api import db


errors = Blueprint('errors', __name__)

@errors.errorhandler(404)
def not_found_error(error):
    return "404"
    # return render_template('404.html'), 404

@errors.errorhandler(500)
def internal_error(error):
    return "505"
    # db.session.rollback()
    # return render_template('500.html'), 500