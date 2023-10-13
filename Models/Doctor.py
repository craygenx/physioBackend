from .Config import db

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    speciality = db.Column(db.String(255), nullable=False)
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)
