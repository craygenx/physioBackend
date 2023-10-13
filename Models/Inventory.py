from .Config import db

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    appointments = db.relationship('Appointment', backref='inventory', lazy=True)