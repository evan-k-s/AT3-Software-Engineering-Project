from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime, time
from database.data import db, User, Review, UserProfile, RecentRecommendation
from classes.Error import AccessError, InputError
from services.auth import auth_login_user, auth_register_user, auth_logout_user
from services.review import user_create_review, user_delete_review, user_edit_review, find_review_activity
from services.recommendations import client, find_user_preferences, find_book_recommendations, store_recent_recommendations, user_save_recommendation, user_delete_recommendation
from decorators.error import catch_errors
from core.auth_core import authorise_user
import re
import os


# Specify alternative location for templates
TEMPLATE_DIR = os.path.abspath('../frontend/templates')
STATIC_DIR = os.path.abspath('../frontend/src')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
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


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin.html', views=self.admin._views)

    def is_accessible(self):
        return current_user.is_admin
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('dashboard'))

class UserModelView(ModelView):
    column_list = ('username', 'email', 'created_at', 'is_admin')
    form_columns = ('username', 'email', 'is_admin')
    can_create = False

    def is_accessible(self):
        return current_user.is_admin
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('dashboard'))

class ReviewModelView(ModelView):
    column_list = ('user', 'title', 'author', 'rating', 'created_at')
    form_columns = ('user', 'rating', 'review_body')
    can_create = False

    def is_accessible(self):
        return current_user.is_admin
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('dashboard'))

admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(UserModelView(User, db, name='Users'))
admin.add_view(ReviewModelView(Review, db, name='Reviews'))
admin.add_link(MenuLink('Back to Home', '/'))


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
    if bypass_auth_check(request):
        return
    
    if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
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
        session_token, csrf_token = current_user.initiate_user_session()
        response = redirect(request.url_rule)
        response.set_cookie("session_token", session_token, httponly=True, samesite="Lax", secure=True)
        response.set_cookie("csrf_token", csrf_token, httponly=True, samesite="Lax", secure=True)

        return response


@app.route('/')
@app.route('/dashboard')
@catch_errors
@login_required
def dashboard():
    reviews = current_user.reviews
    profile = current_user.details
    saved_recommendations = current_user.saved_recommendations

    activity_data = find_review_activity(current_user.id)

    return render_template('index.html', user=current_user, reviews=reviews, profile=profile, saved_recommendations=saved_recommendations, activity_data=activity_data)


@app.route('/reviews')
@catch_errors
@login_required
def reviews():
    reviews = current_user.reviews
    profile = current_user.details
    return render_template('reviews.html', user=current_user, reviews=reviews, profile=profile)


@app.route('/review_activity/<date>')
@catch_errors
@login_required
def review_activity(date):
    date_obj = datetime.strptime(date, "%Y-%m-%d")

    start_day = datetime.combine(date_obj, time.min)
    end_day = datetime.combine(date_obj, time.max)

    reviews = Review.query.filter(Review.user_id == current_user.id, Review.created_at.between(start_day, end_day)).all()

    profile = current_user.details

    return render_template('review_activity.html', user=current_user, date=date, reviews=reviews, profile=profile)


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
    
    profile = current_user.details

    return render_template('create_review.html', user=current_user, profile=profile)


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
    profile = current_user.details
    return render_template('view_review.html', user=current_user, review=review, profile=profile)


@app.route('/edit-review/<int:id>/<olid>', methods=['GET', 'POST'])
@catch_errors
@login_required
def edit_review(id, olid):
    if request.method == 'POST':
        data = request.get_json()
        if ("olid" in data) and ("rating" in data) and ("reviewBody" in data):
            olid = data["olid"]
            rating = int(data["rating"])
            review_body = data["reviewBody"]

            user = current_user

            user_edit_review(user, id, olid, rating, review_body)

            return {}, 200
        else:
            raise AccessError("Missing required fields: cannot edit review!")
    
    review = Review.query.filter_by(user_id=current_user.id, id=id).first()
    profile = current_user.details

    return render_template('edit_review.html', user=current_user, review=review, profile=profile)


@app.route('/recommendations', methods=['GET', 'POST'])
@catch_errors
@login_required
def recommendations():
    if request.method == "POST":
        reviews = Review.query.filter_by(user_id=current_user.id).all()

        reviews_text_array = []

        for review in reviews:
            review_text = f"Title: {review.title}\nAuthor: {review.author}\nRating: {review.rating}/5\n\nBody: {review.review_body}"
            reviews_text_array.append(review_text)
        
        reviews_text = "\n\n--- new review ---\n\n".join(reviews_text_array)

        preferences = find_user_preferences(reviews_text)
        print(preferences)

        books = find_book_recommendations(preferences, current_user)

        print(books)

        recs_num = store_recent_recommendations(books, current_user)

        if recs_num < 12:
            books = find_book_recommendations(preferences, current_user, True, (12 - recs_num))
            final_num = store_recent_recommendations(books, current_user, True)

        return {}, 200
    
    recommendations = current_user.recent_recommendations

    if len(recommendations) > 0:
        existing = True
    else:
        existing = False

    authors_details = RecentRecommendation.query.with_entities(RecentRecommendation.author).filter_by(user_id=current_user.id).distinct().all()
    authors = [row.author for row in authors_details]

    oldest = RecentRecommendation.query.join(RecentRecommendation.user).filter(User.id==current_user.id).order_by(RecentRecommendation.published.asc()).first()
    oldest_pub = oldest.published if oldest is not None else None
    newest = RecentRecommendation.query.join(RecentRecommendation.user).filter(User.id==current_user.id).order_by(RecentRecommendation.published.desc()).first()
    newest_pub = newest.published if newest is not None else None

    profile = current_user.details

    return render_template('recommendations.html', user=current_user, recommendations=recommendations, profile=profile, authors=authors, oldest=oldest_pub, newest=newest_pub, min=oldest_pub, max=newest_pub, existing=existing)


@app.route('/recommendations/filter/<authors>/<min_era>/<max_era>', methods=['GET', 'POST'])
@catch_errors
@login_required
def filter_recommendations(authors, min_era, max_era):
    
    if not authors == "all":
        authors = authors.split(",")
        recommendations = RecentRecommendation.query.join(RecentRecommendation.user).filter(User.id==current_user.id).filter(RecentRecommendation.published >= min_era).filter(RecentRecommendation.published <= max_era).filter(RecentRecommendation.author.in_(authors)).all()
    else:
        recommendations = RecentRecommendation.query.join(RecentRecommendation.user).filter(User.id==current_user.id).filter(RecentRecommendation.published >= min_era).filter(RecentRecommendation.published <= max_era).all()
    
    authors_details = RecentRecommendation.query.with_entities(RecentRecommendation.author).filter_by(user_id=current_user.id).distinct().all()
    all_authors = [row.author for row in authors_details]

    oldest = RecentRecommendation.query.join(RecentRecommendation.user).filter(User.id==current_user.id).order_by(RecentRecommendation.published.asc()).first()
    oldest_pub = oldest.published
    newest = RecentRecommendation.query.join(RecentRecommendation.user).filter(User.id==current_user.id).order_by(RecentRecommendation.published.desc()).first()
    newest_pub = newest.published

    profile = current_user.details

    return render_template('recommendations.html', user=current_user, recommendations=recommendations, profile=profile, authors=all_authors, oldest=oldest_pub, newest=newest_pub, min=min_era, max=max_era, existing=True)


@app.route('/save-recommendation', methods=['GET', 'POST'])
@catch_errors
@login_required
def save_recommendation():
    if request.method == 'POST':
        data = request.get_json()
        if "recommendation_id" in data:
            recommendation_id = data["recommendation_id"]

            user = current_user

            user_save_recommendation(recommendation_id, user)

            return {}, 200
        else:
            raise AccessError("Review does not exist.")


@app.route('/delete-recommendation', methods=['GET', 'POST'])
@catch_errors
@login_required
def delete_recommendation():
    if request.method == 'POST':
        data = request.get_json()
        if "recommendation_id" in data:
            recommendation_id = data["recommendation_id"]

            user = current_user

            user_delete_recommendation(user, recommendation_id)

            return {}, 200
        else:
            raise AccessError("Recommendation does not exist.")



@app.route('/saved-recommendations')
@catch_errors
@login_required
def saved_recommendations():
    recommendations = current_user.saved_recommendations
    profile = current_user.details

    return render_template('saved_recommendations.html', user=current_user, recommendations=recommendations, profile=profile)



@app.route('/toggle-darkmode', methods=['GET', 'POST'])
@catch_errors
def toggle_darkmode():
    if request.method == 'POST':
        data = request.get_json()
        user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
        darkmode = data.get("darkmode", False)
        user_profile.update(darkmode=darkmode)

        return {}, 200



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