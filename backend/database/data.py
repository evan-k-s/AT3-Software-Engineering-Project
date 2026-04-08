from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import secrets


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user_accounts"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    password_hash = db.Column(db.String(100), nullable=False)
    session_token = db.Column(db.String(50), nullable=False)
    csrf_token = db.Column(db.String(50), nullable=False)
    
    def __init__(self, id, username, email, created_at, password=None, password_hash=None, session_token=None, csrf_token=None, **kwargs):
        
        super(User, self).__init__(**kwargs)

        self.__id = id
        self.__username = username
        self.__email = email
        self.__created_at = created_at

        if password:  
            self.__password = generate_password_hash(password)
        elif password_hash:
            self.__password = password_hash
        else:
            raise ValueError("Either password or password_hash must be provided")
        
        self.__session_token = session_token
        self.__csrf_token = csrf_token

    
    def __repr__(self):
        return f"<User {self.username}>"
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password_input):
        return check_password_hash(self.password, password_input)
    
    def generate_token(self):
        return secrets.token_urlsafe(32)
    
    def initiate_user_session(self):
        self.session_token = self.generate_token()
        self.csrf_token = self.generate_token()
        return self.session_token, self.csrf_token
    
    def revoke_user_session(self):
        self.session_token = None
        self.csrf_token = None


    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "password_hash": self.password,
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