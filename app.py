from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from datetime import datetime
from flask_cors import CORS
from Models.Config import db
from Models.Appointment import Appointment
from Models.Doctor import Doctor
from Models.Patient import Patient
from Models.User import User
from Models.Inventory import Inventory
from Models.Invoice import Invoice

app=Flask(__name__)
CORS(app, origins=["https://physio-clinic.onrender.com", 'http://localhost:3000'], methods=['GET', 'POST', 'DELETE', 'PATCH'], supports_credentials=True)
# ma = Marshmallow(app)
ma = Marshmallow(app)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://craygenx:GOBtmBu8h24dyjfBWV7aUJihCQ2TY5ty@dpg-ckkge6bj89us73aj8jj0-a.ohio-postgres.render.com/therapy_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.json.compact = False

migrate = Migrate(app, db)

class DoctorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Doctor

doctor_schema = DoctorSchema()
doctors_schema = DoctorSchema(many=True)

# Patient Schema
class PatientSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Patient

patient_schema = PatientSchema()
patients_schema = PatientSchema(many=True)

# Appointment Schema
class AppointmentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Appointment

appointment_schema = AppointmentSchema()
appointments_schema = AppointmentSchema(many=True)

@app.route('/signUp', methods=['POST'])
def SignUp():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return {'message': 'Username and password are required'}, 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return {'message': 'User already exists'}, 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return {'message': 'User created successfully'}, 201

@app.route('/signIn', methods=['POST'])
def SignIn():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return {'message': 'Username and password are required'}, 400

    user = User.query.filter_by(username=username, password=password).first()
    if user:
        return {'message': 'Login successful'}, 200
    else:
        return {'message': 'Invalid credentials'}, 401

# Create a Doctor
@app.route('/doctors', methods=['POST'])
def create_doctor():
    data = request.json
    new_doc = {
        'first_name': data['firstName'],
        'last_name': data['lastName'],
        'speciality': data['occupation'],
    }
    new_doctor = Doctor(**new_doc)
    db.session.add(new_doctor)
    db.session.commit()
    return doctor_schema.jsonify(new_doctor), 201

# Retrieve all Doctors
@app.route('/doctors', methods=['GET'])
def get_doctors():
    # doctors = Doctor.query.all()
    docs =[]
    for doc in Doctor.query.all():
        doc_dict = {
            'id':doc.id,
            'first_name':doc.first_name,
            'last_name': doc.last_name,
            'speciality':doc.speciality
        }
        docs.append(doc_dict)
    return jsonify(docs), 200
    # return doctors_schema.jsonify(doctors), 200

# Retrieve a specific Doctor
@app.route('/doctors/<int:doctor_id>', methods=['GET'])
def get_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    return doctor_schema.jsonify(doctor), 200

# Update (Patch) a Doctor
@app.route('/doctors/<int:doctor_id>', methods=['PATCH'])
def update_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    data = request.json
    for key, value in data.items():
        setattr(doctor, key, value)
    db.session.commit()
    return doctor_schema.jsonify(doctor), 200

# Delete a Doctor
@app.route('/doctors/<int:doctor_id>', methods=['DELETE'])
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(int(doctor_id))
    db.session.delete(doctor)
    db.session.commit()
    return '', 204

@app.route('/appointments', methods=['GET', 'POST'])
def create_appointment():
    if request.method == 'POST':
        data = request.json
        new_data = {
            'type': data['sessionType'],
            'date': datetime.strptime(data['date'], '%Y-%m-%d'),
            'start_time': datetime.strptime(data['startTime'], '%H:%M').time(),
            'end_time': datetime.strptime(data['endTime'], '%H:%M').time(),
            'description': data['description'],
            'doctor_id': int(data['doctorsId']),
            'patient_id':int(data['patientId']),
            'status': 'active',
            'amount': float(data['amount']),
            'doctorsComment':''
        }
        new_appintment = Appointment(**new_data)
        db.session.add(new_appintment)
        db.session.commit()
        return appointment_schema.jsonify(new_appintment), 201
    if request.method == 'GET':
        # appointments = Doctor.query.all()
        appointments = []
        for appointment in Appointment.query.all():
            appointment_dict = {
                'id': appointment.id,
                'type':appointment.type,
                'date':appointment.date,
                'start_time':appointment.start_time.strftime('%H:%M'),
                'end_time':appointment.end_time.strftime('%H:%M'),
                'description':appointment.description,
                'status':appointment.status,
                'doctor_id':appointment.doctor_id,
                'patient_id':appointment.patient_id,
                'amount':appointment.amount,
                'doctorsComment': appointment.doctorsComment,
                'doctor':'',
                'patient':''
            }
            doctor = Doctor.query.get(appointment.doctor_id)
            appointment_dict['doctor'] = {
                'id':doctor.id,
                'first_name': doctor.first_name,
                'last_name': doctor.last_name
            }
            patient = Patient.query.get(appointment.patient_id)
            appointment_dict['patient'] = {
                'id':patient.id,
                'first_name': patient.first_name,
                'last_name': patient.last_name,
                'address': patient.address,
                'email': patient.email
            }
            appointments.append(appointment_dict)
        return jsonify(appointments), 200
        # return appointment_schema.jsonify(appointments), 200


@app.route('/appointments/<int:appointment_id>', methods=['DELETE', 'PATCH'])
def delete_appointment(appointment_id):
    if request.method == 'DELETE':
        appointment = Appointment.query.get_or_404(appointment_id)
        db.session.delete(appointment)
        db.session.commit()
        return '', 204
    else:
        data = request.json
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({'message': 'Appointment not found'}), 404

        # Update the fields specified in the request
        if 'sessionType' in data:
            appointment.type = data['sessionType']
        if 'date' in data:
            appointment.date = datetime.strptime(data['date'], '%Y-%m-%d')
        if 'startTime' in data:
            appointment.start_time = datetime.strptime(data['startTime'], '%H:%M').time()
        if 'endTime' in data:
            appointment.end_time = datetime.strptime(data['endTime'], '%H:%M').time()
        if 'description' in data:
            appointment.description = data['description']
        if 'doctorsId' in data:
            appointment.doctor_id = int(data['doctorsId'])
        if 'patientId' in data:
            appointment.patient_id = int(data['patientId'])
        if 'amount' in data:
            appointment.amount = float(data['amount'])
        if 'doctorComment' in data:
            appointment.doctorsComment = data['doctorComment']
        if 'status' in data:
            appointment.status = data['status']

        db.session.commit()
        return appointment_schema.jsonify(appointment), 200

@app.route('/patients', methods=['GET', 'POST'])
def create_patient():
    if request.method == 'POST':
        data = request.json
        new_data = {
            'first_name': data['firstname'],
            'last_name':data['lastname'],
            'tax_number':data['tax-number'],
            'dob':datetime.strptime(data['dobFull'], '%Y-%m-%d'),
            'gender':data['genderpick'],
            'next_of_kin':data['kinname'],
            'blood_type':data['bloodtypepick'],
            'marital_status':data['maritalStatuspick'],
            'address':data['address'],
            'mobile': data['mobile'],
            'email':data['email'],
        }
        new_patient = Patient(**new_data)
        db.session.add(new_patient)
        db.session.commit()
        return patient_schema.jsonify(new_patient), 201
    if request.method == 'GET':
        # patients = Patient.query.all()
        # return jsonify(patients)
        patients = []
        for patient in Patient.query.all():
            patient_dict = {
                'id':patient.id,
                'first_name':patient.first_name,
                'last_name':patient.last_name,
                'tax_number':patient.tax_number,
                'dob':patient.dob,
                'gender':patient.gender,
                'next_of_kin':patient.next_of_kin,
                'blood_type':patient.blood_type,
                'marital_status':patient.marital_status,
                'address':patient.address,
                'mobile':patient.mobile,
                'email':patient.email
            }
            patients.append(patient_dict)
        return jsonify(patients)
        # return patient_schema.jsonify(patients), 200

@app.route('/patients/<int:patients_id>', methods=['DELETE'])
def delete_patient(patients_id):
    appointment = Appointment.query.get_or_404(patients_id)
    db.session.delete(appointment)
    db.session.commit()
    return '', 204

@app.route('/invoice', methods=['POST'])
def create_invoice():
    data = request.json
    new_invoice = {
        'date': datetime.strptime(data['date'], '%d/%m/%Y'),
        'payment_type': data['paymentMethod'],
        'patient_id': data['patient_id'],
        'appointment_id': data['appointment_id'],
    }
    new_doctor = Invoice(**new_invoice)
    db.session.add(new_doctor)
    db.session.commit()
    return jsonify({'message': "invoice added"}), 201

db.init_app(app)
if __name__ == '__main__':
    app.run(port=5555)