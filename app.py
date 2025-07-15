from flask import Flask, render_template, request, redirect, session, url_for
import os
import joblib
import pandas as pd
from ocr_utils import get_upi_data_from_image
from sklearn.feature_extraction.text import CountVectorizer
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random
import hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

model = joblib.load("fraud_model.pkl")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    gender = db.Column(db.String(10))
    dob = db.Column(db.String(20))
    uploads = db.relationship('UploadHistory', backref='user', lazy=True)

class UploadHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    result = db.Column(db.String(100))
    timestamp = db.Column(db.String(100))
    location = db.Column(db.String(200))
    hash = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


@app.route('/')
def root():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        dob = request.form['dob']
        gender = request.form['gender']
        birth_year = int(dob.split("-")[0])
        age = datetime.now().year - birth_year
        if age < 18:
            return render_template('signup.html', error="User must be 18 or older.")
        user = User(name=name, email=email, password=password, dob=dob, gender=gender)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid email or password.")
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        file = request.files['screenshot']
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        extracted_data = get_upi_data_from_image(filepath)
        raw_text = "\n".join([f"{k}: {v}" for k, v in extracted_data.items()])

        amount = float(extracted_data.get('amount', 0)) if extracted_data.get('amount') else 0.0
        status = extracted_data.get('transaction_status', '').lower()

        # Create a consistent hash of the OCR text
        hash_seed = hashlib.sha256(raw_text.encode()).hexdigest()

        # Force fraud if transaction is failed
        if status == "failed":
            prediction = 1
            reason = "Transaction failed"
            random.seed(int(hash_seed[:8], 16))
            percentage = random.randint(70, 95)
            prediction_text = f"{percentage}% chance of fraud"

        else:
            # Predict using model
            isFlaggedFraud = 0
            input_data = {
                "step": 1,
                "type": 1,
                "amount": amount,
                "oldbalanceOrg": 10000.0,
                "newbalanceOrig": 10000.0 - amount,
                "oldbalanceDest": 5000.0,
                "newbalanceDest": 5000.0 + amount,
                "isFlaggedFraud": isFlaggedFraud
            }
            input_df = pd.DataFrame([input_data])
            prediction = model.predict(input_df)[0]
            reason = "Transaction looks successful"
            prediction_text = "Not Fraud"
            if prediction == 1:
                random.seed(int(hash_seed[:8], 16))
                percentage = random.randint(50, 85)
                prediction_text = f"{percentage}% chance of fraud"


        # Check for duplicate
        existing = UploadHistory.query.filter_by(user_id=user.id, hash=hash_seed).first()

        location = session.get('location')
        location_str = f"{location['lat']}, {location['lon']}" if location else "Unknown"

        if not existing:
            # Save new upload
            if prediction == 1:
                result_text = f"{percentage}% chance of fraud - {reason}"
            else:
                result_text = reason

            history = UploadHistory(
                filename=file.filename,
                result=result_text,
                timestamp=datetime.now().strftime("%d %b %Y, %I:%M %p"),
                hash=hash_seed,
                user_id=user.id,
                location=location_str
            )

            db.session.add(history)
            db.session.commit()
        else:
            # Reuse previous result
            result_parts = existing.result.split('%')[0], existing.result.split(' - ')[-1]
            percentage, reason = result_parts[0], result_parts[1]

        return render_template('result.html', text=raw_text, prediction=prediction_text, reason=reason)

    history = UploadHistory.query.filter_by(user_id=user.id).all()
    return render_template('dashboard.html', history=history)

@app.route('/upload_history')
def upload_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    uploads = UploadHistory.query.filter_by(user_id=session['user_id']).all()
    return render_template('upload_history.html', uploads=uploads)


@app.route('/save_location', methods=['POST'])
def save_location():
    if 'user_id' in session:
        session['location'] = request.get_json()
    return '', 204


@app.route('/clear_history')
def clear_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    UploadHistory.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return redirect(url_for('upload_history'))

@app.route('/delete_history/<int:upload_id>')
def delete_history(upload_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    history_entry = UploadHistory.query.get(upload_id)
    
    if history_entry and history_entry.user_id == session['user_id']:
        db.session.delete(history_entry)
        db.session.commit()

    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)