# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///relationships.db'
# db = SQLAlchemy(app)

# class Person(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     name = db.Column(db.String(20))
#     pets = db.relationship('Pet', backref='owner')
# class Pet(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     name = db.Column(db.String(20))
#     owner_id = db.Column(db.Integer, db.ForeignKey('person.id'))