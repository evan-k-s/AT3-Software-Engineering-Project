from flask_sqlalchemy import SQLAlchemy
from classes.Error import InputError, AccessError
from database.data import db, Review, User
from datetime import datetime

def user_create_review(user, title, author, olid, rating, review_body):
    if type(rating) != int:
        InputError("Invalid rating!")
    
    exists = User.query.join(User.reviews).filter(User.id==user.id, Review.olid==olid).first() is not None

    if exists:
        raise InputError("Book already reviewed")
    
    created_at = datetime.now()

    new_review = Review(user, title, author, olid, rating, review_body, created_at)

    new_review.save_to_db()


def user_delete_review(user, id):
    review = Review.query.filter_by(user_id=user.id, id=id).first()
    db.session.delete(review)
    db.session.commit()