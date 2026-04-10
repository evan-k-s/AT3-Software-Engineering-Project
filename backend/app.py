from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from database.data import db, User
from classes.Error import AccessError, InputError
from services.auth import login_user, register_user
from decorators.error import catch_errors
import re
import os


# Specify alternative location for templates
TEMPLATE_DIR = os.path.abspath('../frontend')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=TEMPLATE_DIR)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)


# Load local .env file
load_dotenv()

# Credentials from .env for MySQL db
db_user = os.environ['DB_USER']
db_password = os.environ['DB_PASSWORD']
db_name = os.environ['DB_NAME']

# Configure MySQL db
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{db_user}:{db_password}@localhost/{db_name}"
db.init_app(app)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
@catch_errors
def login():
    msg = ""
    data = request.form
    if request.method == 'POST':
        if "username" in data and "password" in data:
            username = data["username"]
            password = data["password"]

            session_token, csrf_token = login_user(username, password)
            response = jsonify({"session_token": session_token, "csrf_token": csrf_token})
            response.set_cookie("session_token", session_token, httponly=True, samesite="Lax", secure=True)

            return render_template('index.html', msg='Logged in successfully!')
        else:
            msg = "Missing required fields: username and password"
            raise AccessError("Missing required fields: username and password")
    
    return render_template('login.html', msg=msg)


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ""
    data = request.form
    if request.method == 'POST':
        if "username" in data and "email" in data and "password" in data and "confirm-password" in data:
            email = data["email"]
            username = data["username"]
            password = data["password"]
            confirm_password = data["confirm-password"]

            if password == confirm_password:
                session_token, csrf_token = register_user(username, email, password)
                response = jsonify({"session_token": session_token, "csrf_token": csrf_token})
                response.set_cookie("session_token", session_token, httponly=True, samesite="Lax", secure=True)

                return render_template('index.html', msg='Registered successfully!')
            else:
                msg = "Confirmed password does not match!"
                raise InputError("Confirmed password does not match!")
        else:
            msg = "Missing required fields: email, username, and password"
            raise InputError("Missing required fields: email, username, and password")
    return render_template('register.html', msg=msg)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)