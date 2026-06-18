from flask_sqlalchemy import SQLAlchemy
from classes.Error import InputError, AccessError
from database.data import db, Review

def user_create_review(user, title, author, olid, rating, review_body):
    if type(rating) != int:
        InputError("Invalid rating!")

    new_review = Review(user, title, author, olid, rating, review_body)

    new_review.save_to_db()