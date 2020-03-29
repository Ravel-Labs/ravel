from flask import Blueprint, render_template
from flask_login import login_required, current_user
main = Blueprint("main", __name__)
'''
    Server rendered components
'''
# Landing page
@main.route('/')
def index():
    return "Render index"
    # return render_template('index.html')

# Restricted page
@main.route('/profile')
@login_required
def profile():
    return "Render profile"
    # return render_template('profile.html', name=current_user.name)
