from flask_login import UserMixin
from ravel.api import db
# TODO This is a good idea, but needs more work to wire properly
class AbstractModel(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)