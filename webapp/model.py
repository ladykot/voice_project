from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pacient_name = db.Column(db.String)
    task = db.Column(db.Text, unique=True)
