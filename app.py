# Import required modules
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, session, url_for, send_file, jsonify
from flask_socketio import SocketIO, emit, join_room
from flask_cors import CORS
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import mysql.connector
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from mysql.connector import Error

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/prescriptions', exist_ok=True)

# Enable CORS and SocketIO
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# MySQL config (manual connection for prediction & booking)
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Dhivi@29',
    'database': 'doctor_system'
}
db1 = mysql.connector.connect(**db_config)

# Flask-MySQL config
app.config['MYSQL_HOST'] = db_config['host']
app.config['MYSQL_USER'] = db_config['user']  # fixed
app.config['MYSQL_PASSWORD'] = db_config['password']  # fixed
app.config['MYSQL_DB'] = db_config['database']  # fixed
mysql = MySQL(app)

# Routes
@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "dhivi" and password == "12345":
            session['username'] = username
            return redirect(url_for('profile'))
        else:
            return "Invalid credentials", 403
    return render_template('login.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        email = request.form['email']
        photo = request.files['photo']
        photo_filename = secure_filename(photo.filename) if photo.filename != '' else 'default.png'
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
        session['user'] = {
            'name': name,
            'age': age,
            'gender': gender,
            'email': email,
            'photo': photo_filename,
            'username': session['username']
        }
        return redirect(url_for('dashboard'))
    return render_template('profile.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    profile = session.get('user')
    return render_template('dashboard.html', profile=profile, user=profile)

@app.route('/prescription', methods=['GET', 'POST'])
def prescription():
    if request.method == 'POST':
        file = request.files['prescription']
        if file.filename == '':
            return "No file selected", 400
        filename = secure_filename(file.filename)
        file.save(os.path.join('static/prescriptions', filename))
        return "Prescription uploaded successfully!"
    return render_template('prescription.html')

@app.route('/tips')
def tips():
    health_tips = [
        "Drink more water daily 💧",
        "Exercise 30 minutes a day 🏃‍♂️",
        "Sleep at least 7-8 hours 🛌",
        "Eat more vegetables and fruits 🥗"
    ]
    return render_template('tips.html', tips=health_tips)
@app.route('/medication')
def medication():
    return render_template('medication.html')
@app.route('/symptom_checker')
def symptom_checker():
    return render_template('symptom_checker.html')

@app.route('/wearable')
def wearable():
    return render_template('wearable.html')
@app.route('/bmi')
def bmi():
    return render_template('bmi.html')

@app.route('/notifications')
def notifications():
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("SELECT message FROM notifications ORDER BY created_at DESC")
        notifications = cursor.fetchall()
        cursor.close()
        return render_template('notifications.html', notifications=notifications)
    except Exception as e:
        return f"Error loading notifications: {str(e)}", 500

@app.route('/report')
def report():
    return render_template('report.html')

# Health Prediction Model
X = np.array([[75, 120, 80], [60, 130, 85], [80, 140, 90]])
y = np.array([0, 1, 0])
model = RandomForestClassifier()
model.fit(X, y)

def predict_health_condition(health_data):
    if "fever" in health_data.lower():
        return "Possible fever - Please consult a doctor."
    elif "cough" in health_data.lower():
        return "Possible flu - Consult a healthcare provider."
    return "Health condition unclear, visit a doctor for accurate diagnosis."

@app.route('/health_prediction', methods=['GET', 'POST'])
def predict_health():
    prediction_result = None
    if request.method == 'POST':
        health_data = request.form['health_data']
        prediction_result = predict_health_condition(health_data)
    return render_template('health_prediction.html', prediction=prediction_result)

@app.route('/consult_booking', methods=['GET', 'POST'])
def consult_booking():
    success = False
    try:
        conn = mysql.connection
        cursor = conn.cursor()

        if request.method == 'POST':
            patient_name = request.form['patient_name']
            age = int(request.form['age'])
            gender = request.form['gender']
            doctor_name = request.form['doctor_name']
            specialty = request.form['specialty']
            date = request.form['date']
            time = request.form['time']

            insert_query = """
                INSERT INTO consult_booking (patient_name, age, gender, doctor_name, specialty, date, time)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (patient_name, age, gender, doctor_name, specialty, date, time))
            conn.commit()
            success = True

        select_query = "SELECT * FROM consult_booking ORDER BY date ASC, time ASC"
        cursor.execute(select_query)
        consults = cursor.fetchall()

        cursor.close()
        return render_template('consult_booking.html', consults=consults, success=success)

    except Error as e:
        print("Error while connecting to MySQL", e)
        return "Database connection error", 500

@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    if request.method == 'POST':
        cursor = db1.cursor()
        query = """
            INSERT INTO appointment (username, doctor_name, appointment_date, appointment_time)
            VALUES (%s, %s, %s, %s)
        """
        data = (
            username,
            request.form['doctor_name'],
            request.form['appointment_date'],
            request.form['appointment_time']
        )
        cursor.execute(query, data)
        db1.commit()
        cursor.close()
        return render_template('appointment.html', message="Your appointment has been successfully booked!")
    return render_template('appointment.html')

@app.route('/video')
def video():
    return render_template('video.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/mental_health')
def mental_health():
    return render_template('mental_health.html')

@app.route('/health')
def health():
    return render_template('health.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@socketio.on('send_message')
def handle_send_message(data):
    sender = data['sender']
    receiver = data['receiver']
    content = data['message']
    cursor = db1.cursor()
    sql = "INSERT INTO messages (sender, receiver, content, status) VALUES (%s, %s, %s, 'sent')"
    val = (sender, receiver, content)
    cursor.execute(sql, val)
    db1.commit()
    room = f"{sender}-{receiver}"
    emit('receive_message', {
        'sender': sender,
        'receiver': receiver,
        'message': content,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }, room=room)

@socketio.on('join')
def on_join(data):
    room = f"{data['sender']}-{data['receiver']}"
    join_room(room)
    print(f"{data['sender']} joined room {room}")

# Run the app
if __name__ == '__main__':
    socketio.run(app, debug=True)
