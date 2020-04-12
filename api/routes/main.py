from flask import Blueprint, render_template
from flask_jwt import jwt_required

main_bp = Blueprint("main_bp", __name__)

'''
    Server rendered components
'''
# Landing page
@main_bp.route('/')
def index():
    return "Render index"

# Restricted page
@main_bp.route('/profile')
@jwt_required()
def profile():
    return "Render profile"