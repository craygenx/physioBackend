from .Config import db

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    tax_number = db.Column(db.String(255), unique=True, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    next_of_kin = db.Column(db.String(255), nullable=True)
    blood_type = db.Column(db.String(10), nullable=True)
    marital_status = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    mobile = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    appointments = db.relationship('Appointment', backref='patient', lazy=True)