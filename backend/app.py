from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from database.data import db, User, Review
from classes.Error import AccessError, InputError
from services.auth import auth_login_user, auth_register_user, auth_logout_user
from services.review import user_create_review, user_delete_review
from decorators.error import catch_errors
from core.auth_core import authorise_user
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


first_request = True

IGNORE_AUTH_PATHS = [
    "/register",
    "/login",
]

def bypass_auth_check(request):
    if request.path in IGNORE_AUTH_PATHS:
        return True
    else:
        return False

@app.before_request
@catch_errors
def flask_middle_auth():
    global first_request
    if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
        if bypass_auth_check(request):
            return

        # Retrieve session and CSRF tokens from headers and validate
        session_token = request.headers.get("Authorization")
        csrf_token = request.headers.get("X-CSRF-Token")
        print(session_token, csrf_token)
        if not session_token:
            raise AccessError("No session token found")
        else:
            authorise_user(session_token, csrf_token)
    elif first_request:
        first_request = False
        response = redirect(request.url_rule)
        response.set_cookie("session_token", session_token, httponly=True, samesite="Lax", secure=True)
        response.set_cookie("csrf_token", csrf_token, httponly=True, samesite="Lax", secure=True)

        return response


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
    reviews = current_user.reviews
    return render_template('reviews.html', user=current_user, reviews=reviews)

@app.route('/create-review', methods=['GET', 'POST'])
@catch_errors
@login_required
def create_reviews():
    if request.method == 'POST':
        data = request.get_json()
        if ("title" in data) and ("author" in data) and ("olid" in data) and ("rating" in data) and ("reviewBody" in data):
            title = data["title"]
            author = data["author"]
            olid = data["olid"]
            rating = int(data["rating"])
            review_body = data["reviewBody"]
            
            user = current_user

            user_create_review(user, title, author, olid, rating, review_body)

            return {}, 200
        else:
            msg = "Missing required fields for review."
            raise AccessError("Missing required fields for review.")

    return render_template('create_review.html', user=current_user)


@app.route('/delete-review', methods=['GET', 'POST'])
@catch_errors
@login_required
def delete_review():
    if request.method == 'POST':
        data = request.get_json()
        if "review_id" in data:
            review_id = data["review_id"]

            user = current_user

            user_delete_review(user, review_id)

            return {}, 200
        else:
            raise AccessError("Review does not exist.")


@app.route('/view-review/<int:id>/<olid>', methods=['GET', 'POST'])
@catch_errors
@login_required
def view_review(id, olid):
    review = Review.query.filter_by(user_id=current_user.id, id=id).first()
    return render_template('view_review.html', user=current_user, review=review)


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
        session_token, csrf_token = current_user.initiate_user_session()
        response = redirect(url_for('dashboard'))
        response.set_cookie("session_token", session_token, httponly=True, samesite="Lax", secure=True)
        response.set_cookie("csrf_token", csrf_token, httponly=True, samesite="Lax", secure=True)

        return response

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