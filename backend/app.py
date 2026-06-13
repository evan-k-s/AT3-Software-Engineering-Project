from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from database.data import db, User
from classes.Error import AccessError, InputError
from services.auth import auth_login_user, auth_register_user, auth_logout_user
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
secret_key = os.environ['SECRET_KEY']

# Configure MySQL db
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{db_user}:{db_password}@localhost/{db_name}"
app.config['SECRET_KEY'] = secret_key
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'login'

login_manager.login_message = "Please log in!"
login_manager.login_message_category = "info"


@app.route('/')
@app.route('/dashboard')
@catch_errors
@login_required
def dashboard():
    return render_template('index.html', user=current_user)


@app.route('/reviews')
@catch_errors
@login_required
def reviews():
    return render_template('reviews.html', user=current_user)

@app.route('/create-review')
@catch_errors
@login_required
def create_reviews():
    return render_template('create_review.html', user=current_user)

@app.route('/recommendations')
@catch_errors
@login_required
def recommendations():
    return render_template('recommendations.html', user=current_user)

@app.route('/saved-recommendations')
@catch_errors
@login_required
def saved_recommendations():
    return render_template('saved_recommendations.html', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
@catch_errors
def login():
    msg = ""

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        data = request.get_json()
        if "username" in data and "password" in data:
            username = data["username"]
            password = data["password"]
            remember = True if data.get("remember") else False

            session_token, csrf_token, user = auth_login_user(username, password)
            response = jsonify({"session_token": session_token, "csrf_token": csrf_token})
            response.set_cookie("session_token", session_token, httponly=True, samesite="Lax", secure=True)
            
            login_user(user, remember=remember)

            return response, 200
        else:
            msg = "Missing required fields: username and password"
            raise AccessError("Missing required fields: username and password")
    
    return render_template('login.html', msg=msg)


@app.route('/register', methods=['GET', 'POST'])
@catch_errors
def register():
    msg = ""

    if request.method == 'POST':
        data = request.get_json()
        if "username" in data and "email" in data and "password" in data:
            email = data["email"]
            username = data["username"]
            password = data["password"]


            session_token, csrf_token = auth_register_user(username, email, password)
            response = jsonify({"session_token": session_token, "csrf_token": csrf_token})
            response.set_cookie("session_token", session_token, httponly=True, samesite="Lax", secure=True)

            flash("Successfully registered! Please login.")

            return response, 200
        else:
            msg = "Missing required fields: email, username, and password"
            raise InputError("Missing required fields: email, username, and password")
    return render_template('register.html', msg=msg)


@app.route('/logout', methods=['POST'])
@catch_errors
@login_required
def logout():
    auth_logout_user(current_user.session_token)
    logout_user()
    return {}, 200


@login_manager.user_loader
@catch_errors
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)