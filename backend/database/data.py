from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import secrets


db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "user_accounts"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    password_hash = db.Column(db.String(255), nullable=False)
    session_token = db.Column(db.String(50), nullable=False)
    csrf_token = db.Column(db.String(50), nullable=False)
    reviews = db.relationship('Review', backref='user')
    
    def __init__(self, username, email, created_at, password=None, password_hash=None, session_token=None, csrf_token=None, **kwargs):
        
        super(User, self).__init__(**kwargs)

        self.username = username
        self.email = email
        self.created_at = created_at

        if password:  
            self.password_hash = generate_password_hash(password)
        elif password_hash:
            self.password_hash = password_hash
        else:
            raise ValueError("Either password or password_hash must be provided")
        
        self.session_token = session_token
        self.csrf_token = csrf_token

    
    def __repr__(self):
        return f"<User {self.username}>"
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.add(self)
        db.session.commit()
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password_input):
        return check_password_hash(self.password_hash, password_input)
    
    def generate_token(self):
        return secrets.token_urlsafe(32)
    
    def initiate_user_session(self):
        self.session_token = self.generate_token()
        self.csrf_token = self.generate_token()
        self.update(session_token=self.session_token, csrf_token=self.csrf_token)
        return self.session_token, self.csrf_token
    
    def revoke_user_session(self):
        self.session_token = None
        self.csrf_token = None


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "password_hash": self.password_hash,
            "session_token": self.session_token,
            "csrf_token": self.csrf_token
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            email=data["email"],
            username=data["username"],
            password_hash=data["password_hash"],
            created_at=data["created_at"],
            session_token=data.get("session_token"),
            csrf_token=data.get("csrf_token")
        )


class Review(db.Model):
    __tablename__ = "user_reviews"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_accounts.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    olid = db.Column(db.String(80), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_body = db.Column(db.Text, nullable=False)

    def __init__(self, user, title, author, olid, rating, review_body):
        self.user = user
        self.title = title
        self.author = author
        self.olid = olid
        self.rating = rating
        self.review_body = review_body

    def __repr__(self):
        return f"<Review from {self.user.username} about {self.title} by {self.author}>"
    

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "olid": self.olid,
            "rating": self.rating,
            "review_body": self.review_body
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data["title"],
            author=data["author"],
            olid=data["olid"],
            rating=data["rating"],
            review_body=data["review_body"]
        )