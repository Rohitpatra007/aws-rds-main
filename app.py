from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from config import DATABASE_URL  # Import from config.py

app = Flask(__name__, static_folder="static")
CORS(app)

# Use PostgreSQL database (AWS RDS)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Student model
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    major = db.Column(db.String(100))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "major": self.major
        }

# Create the table in the database
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

# Create Student (POST)
@app.route('/students', methods=['POST'])
def create_student():
    data = request.get_json()
    new_student = Student(
        name=data['name'],
        email=data['email'],
        phone=data.get('phone'),
        major=data.get('major')
    )
    db.session.add(new_student)
    db.session.commit()
    return jsonify(new_student.to_dict()), 201

# Get All Students (GET)
@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([student.to_dict() for student in students])

# Get Student by ID (GET)
@app.route('/students/<int:id>', methods=['GET'])
def get_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    return jsonify(student.to_dict())

# Update Student by ID (PUT)
@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    data = request.get_json()
    student.name = data.get('name', student.name)
    student.email = data.get('email', student.email)
    student.phone = data.get('phone', student.phone)
    student.major = data.get('major', student.major)
    db.session.commit()
    return jsonify(student.to_dict())

# Delete Student by ID (DELETE)
@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    db.session.delete(student)
    db.session.commit()
    return jsonify({'message': 'Student deleted successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

