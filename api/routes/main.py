from flask import Blueprint, render_template

main_bp = Blueprint("main_bp", __name__)

'''
    Server rendered components
'''


@main_bp.route('/')
def index():
    return "Render index"


@main_bp.route('/profile')
def profile():
    return "Render profile"
