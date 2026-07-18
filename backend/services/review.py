from flask_sqlalchemy import SQLAlchemy
from classes.Error import InputError, AccessError
from database.data import db, Review, User
from datetime import datetime, timedelta

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


def user_edit_review(user, id, olid, rating, review_body):
    if type(rating) != int:
        InputError("Invalid rating!")
    
    review = Review.query.filter_by(user_id=user.id, id=id).first()

    if (rating == review.rating) and (review_body == review.review_body):
        raise InputError("You must edit the review to perform this action!")

    review.update(rating=rating, review_body=review_body)


def find_review_activity(user_id):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    results = db.session.query(
        db.func.date(Review.created_at).label('review_date'),
        db.func.count(Review.id).label('review_count')
    ).filter(
        Review.user_id == user_id,
        Review.created_at >= start_date
    ).group_by(db.func.date(Review.created_at)).all()

    activity_dict = { str(row.review_date): row.review_count for row in results }

    heatmap_data = []

